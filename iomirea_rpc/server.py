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
import asyncio

from typing import Union, Dict, Any, Tuple, Callable, Awaitable

import aioredis

from .log import rpc_log


_CommandType = Callable[["Server", str, Any], Awaitable[None]]


class Server:
    def __init__(
        self,
        channel_name: str,
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
    ):
        self._call_address = f"rpc:{channel_name}"
        self._resp_address = f"{self._call_address}-response"
        self._loop = loop

        self._commands: Dict[int, _CommandType] = {}

    def register_command(self, index: int, fn: _CommandType) -> int:
        if index in self._commands:
            raise ValueError(f"Command with index {index} already registered")

        self._commands[index] = fn

        return index

    async def run(
        self, redis_address: Union[Tuple[str, str], str], **kwargs: Any
    ) -> None:
        self._call_conn = await aioredis.create_redis(redis_address, **kwargs)
        self._resp_conn = await aioredis.create_redis(redis_address, **kwargs)

        channels = await self._call_conn.subscribe(self._call_address)
        self._loop.create_task(self._handler(channels[0]))

        self._log(f"listening: {self._call_address}")
        self._log(f"responding: {self._resp_address}")

    async def _parse_payload(
        self, payload: Dict[str, Any]
    ) -> Tuple[int, str, Dict[str, Any]]:
        return (payload["c"], payload["a"], payload.get("d", {}))

    async def _handler(self, channel: aioredis.pubsub.Channel) -> None:
        async for msg in channel.iter():
            try:
                payload = json.loads(msg)

                command, address, data = await self._parse_payload(payload)
            except Exception as e:
                self._log(
                    f"error parsing command: {e.__class__.__name__}: {e}"
                )
                continue

            self._log(f"recieved command {command}")

            fn = self._commands.get(command)
            if fn is None:
                self._log(f"unknown command {command}")
                continue

            try:
                # kwargs typing issue
                await fn(self, address, **data)  # type: ignore
            except Exception as e:
                self._log(
                    f"error calling command {command}: {e.__class__.__name__}: {e}"
                )

    async def respond(self, address: str, data: Any) -> None:
        await self._resp_conn.publish_json(
            self._resp_address, {"a": address, "d": data}
        )

    def _log(self, text: str) -> None:
        rpc_log(text, prefix="server")
