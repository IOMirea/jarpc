"""
IOMirea-rpc - RPC system for IOMirea messenger
Copyright (C) 2019  Eugene Ershov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import uuid
import asyncio

from typing import Union, Dict, Any, Tuple, List

import aioredis

from .response import Response
from .log import rpc_log


class Client:
    def __init__(
        self,
        channel_name: str,
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
    ):
        self._call_address = f"rpc:{channel_name}"
        self._resp_address = f"{self._call_address}-response"
        self._loop = loop

        self._responses: Dict[str, List[Response]] = {}

    async def run(
        self, redis_address: Union[Tuple[str, int], str], **kwargs: Any
    ) -> None:
        self._call_conn = await aioredis.create_redis(redis_address, **kwargs)
        self._resp_conn = await aioredis.create_redis(redis_address, **kwargs)

        channels = await self._resp_conn.subscribe(self._resp_address)
        self._loop.create_task(self._handler(channels[0]))

        self._log(f"listening: {self._resp_address}")
        self._log(f"calling: {self._call_address}")

    async def _parse_payload(
        self, payload: Dict[str, Any]
    ) -> Tuple[str, str, Dict[str, Any]]:
        return (payload["n"], payload["a"], payload.get("d", {}))

    async def _handler(self, channel: aioredis.pubsub.Channel) -> None:
        async for msg in channel.iter():
            try:
                payload = json.loads(msg)

                node, address, data = await self._parse_payload(payload)
            except Exception as e:
                self._log(
                    f"error parsing response from node {node}: {e.__class__.__name__}: {e}"
                )
                continue

            if address not in self._responses:
                self._log(f"ignoring response from node {node}")
                continue

            response = Response(node, data)
            self._responses[address].append(response)

    async def call(
        self, index: int, data: Dict[str, Any] = {}, timeout: int = -1
    ) -> List[Response]:
        address = uuid.uuid4().hex

        payload = {"c": index, "a": address, "d": data}

        self._log(f"sending command {index}")

        await self._call_conn.publish_json(self._call_address, payload)

        if timeout == -1:
            return []

        self._responses[address] = []  # register listener

        await asyncio.sleep(timeout)

        return self._responses.pop(address)

    def _log(self, text: str) -> None:
        rpc_log(text, prefix="client")
