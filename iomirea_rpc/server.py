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

from typing import Union, Dict, Any, Tuple

import aioredis

from .log import rpc_log
from .constants import StatusCode


# TODO: find a solution to fix typing
_CommandType = Any
# _CommandType = Callable[["Server", str, Any], Awaitable[Any]]

NoValue = object()


class Server:
    def __init__(
        self,
        channel_name: str,
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
        node: str = uuid.uuid4().hex,
    ):
        self._call_address = f"rpc:{channel_name}"
        self._resp_address = f"{self._call_address}-response"

        self.loop = loop
        self.node = node

        self._commands: Dict[int, _CommandType] = {}

    def register_command(self, index: int, fn: _CommandType) -> int:
        if index in self._commands:
            raise ValueError(f"Command with index {index} already registered")

        self._commands[index] = fn

        return index

    def remove_command(self, index: int) -> _CommandType:
        if index not in self._commands:
            raise ValueError(f"Command with index {index} is not registered")

        return self._commands.pop(index)

    async def run(
        self, redis_address: Union[Tuple[str, int], str], **kwargs: Any
    ) -> None:
        self._call_conn = await aioredis.create_redis(
            redis_address, loop=self.loop, **kwargs
        )
        self._resp_conn = await aioredis.create_redis(
            redis_address, loop=self.loop, **kwargs
        )

        channels = await self._call_conn.subscribe(self._call_address)

        self._log(f"running on node {self.node}")
        self._log(f"listening: {self._call_address}")
        self._log(f"responding: {self._resp_address}")

        await self._handler(channels[0])

    async def _parse_payload(
        self, payload: Dict[str, Any]
    ) -> Tuple[int, str, Dict[str, Any]]:
        return (payload["c"], payload["a"], payload.get("d", {}))

    async def _handler(self, channel: aioredis.pubsub.Channel) -> None:
        async for msg in channel.iter():
            try:
                payload = json.loads(msg)

                command_index, address, data = await self._parse_payload(
                    payload
                )
            except Exception as e:
                self._log(
                    f"error parsing command: {e.__class__.__name__}: {e}"
                )

                # address is unavailable
                # await self._respond(address, StatusCode.bad_format)
                continue

            self._log(f"recieved command {command_index}")

            fn = self._commands.get(command_index)
            if fn is None:
                self._log(f"unknown command {command_index}")

                await self._respond(StatusCode.unknown_command, address)

                continue

            try:
                command = fn(self, address, **data)
            except TypeError as e:
                self._log(f"bad arguments given to {command_index}: {e}")

                await self._respond(StatusCode.bad_params, address, str(e))

                continue

            try:
                command_result = await command
            except Exception as e:
                self._log(
                    f"error calling command {command_index}: {e.__class__.__name__}: {e}"
                )

                await self._respond(StatusCode.internal_error, address, str(e))

                continue

            if command_result is NoValue:
                return

            await self.respond(address, command_result)

    async def _respond(
        self, status: StatusCode, address: str, data: Any = NoValue
    ) -> None:
        response = {"s": status.value, "n": self.node, "a": address}

        if data is not NoValue:
            response["d"] = data

        await self._resp_conn.publish_json(self._resp_address, response)

    async def respond(self, address: str, data: Any) -> None:
        await self._respond(StatusCode.success, address, data)

    def close(self) -> None:
        self._log("closing connections")

        self._call_conn.close()
        self._resp_conn.close()

    def _log(self, text: str) -> None:
        rpc_log(text, prefix="server")

    def __repr__(self) -> str:
        return f"<Server call_address={self._call_address} resp_addrss={self._resp_address} node={self.node}>"
