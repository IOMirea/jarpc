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

from __future__ import annotations

import json
import time
import uuid
import asyncio
import logging

from typing import Any, Dict, List, Tuple, Union, Optional

import aioredis

from .response import Response

log = logging.getLogger(__name__)


class AsyncTimeoutResponseIterator:

    __slots__ = ("_client", "_address", "_timeout", "_start_time")

    def __init__(
        self,
        client: Client,
        address: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self._client = client
        self._address = address
        self._timeout = timeout

        self._start_time = time.time()

        if self._address is not None and self._timeout is not None:
            self._client._responses[self._address] = asyncio.Queue(
                loop=self._client._loop
            )

    async def flatten(self) -> List[Response]:
        """Convenience function that exhausts iterator and returns all responses."""

        return [resp async for resp in self]

    def __aiter__(self) -> AsyncTimeoutResponseIterator:
        return self

    async def __anext__(self) -> Response:
        if self._address is None or self._timeout is None:
            raise StopAsyncIteration

        try:
            return await asyncio.wait_for(
                self._client._responses[self._address].get(),
                timeout=time.time() - self._start_time + self._timeout,
                loop=self._client._loop,
            )
        except asyncio.TimeoutError:
            del self._client._responses[self._address]
            raise StopAsyncIteration


class Client:
    """RPC client sends commands to servers and listens for responses."""

    def __init__(
        self,
        channel_name: str,
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
    ):
        self._call_address = f"rpc:{channel_name}"
        self._resp_address = f"{self._call_address}-response"

        self._loop = loop

        self._responses: Dict[str, asyncio.Queue[Response]] = {}

    async def run(
        self, redis_address: Union[Tuple[str, int], str], **kwargs: Any
    ) -> None:
        """Launches client."""

        self._call_conn = await aioredis.create_redis(
            redis_address, loop=self._loop, **kwargs
        )
        self._resp_conn = await aioredis.create_redis(
            redis_address, loop=self._loop, **kwargs
        )

        channels = await self._resp_conn.subscribe(self._resp_address)

        log.info(f"listening: {self._resp_address}")
        log.info(f"calling: {self._call_address}")

        await self._handler(channels[0])

    async def _handler(self, channel: aioredis.pubsub.Channel) -> None:
        async for msg in channel.iter():
            try:
                response = Response.from_json(json.loads(msg))
            except Exception as e:
                log.error(f"error parsing response: {e.__class__.__name__}: {e}")
                continue

            if response._address not in self._responses:
                log.debug(f"ignoring response from node {response.node}")
                continue

            await self._responses[response._address].put(response)

    async def _send(self, payload: Dict[str, Any]) -> None:
        num_listeners = await self._call_conn.publish_json(self._call_address, payload)
        log.debug(f"delivered to {num_listeners} listeners")

    def call(
        self,
        command_index: int,
        data: Dict[str, Any] = {},
        timeout: Optional[int] = None,
    ) -> AsyncTimeoutResponseIterator:
        """
        Calls command and returns recieved responses. Skips response processing
        completely if timeout is None.
        """

        log.info(f"sending command {command_index}")

        payload = {"c": command_index, "d": data}

        address: Optional[str]

        if timeout is not None:
            address = uuid.uuid4().hex
            payload["a"] = address
        else:
            address = None

        asyncio.create_task(self._send(payload))

        return AsyncTimeoutResponseIterator(self, address, timeout)

    def close(self) -> None:
        log.info("closing connections")

        self._call_conn.close()
        self._resp_conn.close()

    def __repr__(self) -> str:
        return f"<Client call_address={self._call_address} resp_addrss={self._resp_address}>"
