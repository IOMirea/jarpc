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
import logging

from typing import Any, Dict, Tuple, Union, Optional

import aioredis

from .enums import StatusCode
from .request import Request

# TODO: find a solution to fix typing
_CommandType = Any
# _CommandType = Callable[["Server", Request, Any], Awaitable[Any]]

NoValue = object()

log = logging.getLogger(__name__)


class Server:
    """RPC server listens for commands from clients and sends responses."""

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

        log.info(f"running on node {self.node}")
        log.info(f"listening: {self._call_address}")
        log.info(f"responding: {self._resp_address}")

        await self._handler(channels[0])

    async def _handler(self, channel: aioredis.pubsub.Channel) -> None:
        async for msg in channel.iter():
            try:
                request = Request.from_json(json.loads(msg))
            except Exception as e:
                log.error(f"error parsing request: {e.__class__.__name__}: {e}")

                # address is unavailable
                # await self._respond(request.address, StatusCode.BAD_FORMAT)
                continue

            log.info(f"received command {request.command_index}")

            fn = self._commands.get(request.command_index)
            if fn is None:
                log.warning(f"unknown command {request.command_index}")

                await self._respond(StatusCode.UNKNOWN_COMMAND, request.address)

                continue

            try:
                command = fn(self, request, **request._data)
            except TypeError as e:
                log.error(f"bad arguments given to {request.command_index}: {e}")

                await self._respond(StatusCode.BAD_PARAMS, request.address, str(e))

                continue

            try:
                command_result = await command
            except Exception as e:
                log.error(
                    f"error calling command {request.command_index}: {e.__class__.__name__}: {e}"
                )

                await self._respond(StatusCode.INTERNAL_ERROR, request.address, str(e))

                continue

            if command_result is None:
                continue

            await self.respond(request, command_result)

    async def _send(self, payload: Dict[str, Any]) -> None:
        await self._resp_conn.publish_json(self._resp_address, payload)

    async def _respond(
        self, status: StatusCode, address: Optional[str], data: Any = NoValue
    ) -> None:
        if address is None:
            log.debug("no address, unable to respond")
            return

        payload = {"s": status.value, "n": self.node, "a": address}

        if data is not NoValue:
            payload["d"] = data

        await self._send(payload)

    async def respond(self, request: Request, data: Any) -> None:
        await self._respond(StatusCode.SUCCESS, request.address, data)

    def close(self) -> None:
        log.info("closing connections")

        self._call_conn.close()
        self._resp_conn.close()

    def __repr__(self) -> str:
        return f"<Server call_address={self._call_address} resp_addrss={self._resp_address} node={self.node}>"
