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

from typing import Any, Dict, Tuple, Union, Callable, Optional
from functools import wraps

import aioredis

from .enums import StatusCode
from .request import Request
from .constants import NoValue

_CommandType = Any

# TODO: annotate _CommandType properly.
# Possible solutions (do not work for different reasons)
#
# typing_extensions.Protocol
# class _CommandType(Protocol):
#     def __call__(self, __request: Request, **kwargs: Any) -> Any:
#         ...
#
# mypy_extensions.TypeVar
# _CommandType = Callable[["Server", KwArg(Any)], Awaitable[Any]]
#
# typing.TypeVar ?

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

    def command(self, index: int) -> Callable[[_CommandType], None]:
        def inner(func: _CommandType) -> None:
            self.register_command(index, func)

        return inner

    def register_command(self, index: int, fn: _CommandType) -> int:
        if index in self._commands:
            raise ValueError(f"Command with index {index} already registered")

        self._commands[index] = fn

        return index

    def remove_command(self, index: int) -> _CommandType:
        if index not in self._commands:
            raise ValueError(f"Command with index {index} is not registered")

        return self._commands.pop(index)

    async def start(
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

    def run(self, *args: Any, **kwargs: Any) -> None:
        self.loop.run_until_complete(self.start(*args, **kwargs))

    async def _handler(self, channel: aioredis.pubsub.Channel) -> None:
        async for msg in channel.iter():
            try:
                request = Request.from_data(self, json.loads(msg))
            except Exception as e:
                log.error(f"error parsing request: {e.__class__.__name__}: {e}")

                # address is unavailable
                # await self._respond(request.address, StatusCode.BAD_FORMAT)
                continue

            log.info(f"received command {request.command_index}")

            fn = self._commands.get(request.command_index)
            if fn is None:
                log.warning(f"unknown command {request.command_index}")

                await request._reply_with_status(status=StatusCode.UNKNOWN_COMMAND)

                continue

            try:
                command = fn(request, **request._data)
            except TypeError as e:
                log.error(f"bad arguments given to {request.command_index}: {e}")

                await request._reply_with_status(str(e), StatusCode.BAD_PARAMS)

                continue

            try:
                command_result = await command
            except Exception as e:
                log.error(
                    f"error calling command {request.command_index}: {e.__class__.__name__}: {e}"
                )

                await request._reply_with_status(str(e), StatusCode.INTERNAL_ERROR)

                continue

            if command_result is None:
                # Special case, should be documented.
                # returning None is allowed using request.reply
                continue

            await request.reply(command_result)

    async def _send(self, payload: Dict[str, Any]) -> None:
        await self._resp_conn.publish_json(self._resp_address, payload)

    async def reply(
        self, *, address: Optional[str], status: StatusCode, data: Any
    ) -> None:
        if address is None:
            log.debug("no address, unable to respond")
            return

        payload = {"s": status.value, "n": self.node, "a": address}

        if data is not NoValue:
            payload["d"] = data

        await self._send(payload)

    def close(self) -> None:
        """Closes connections stopping server."""

        log.info("closing connections")

        self._call_conn.close()
        self._resp_conn.close()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} call_address={self._call_address} resp_address={self._resp_address} node={self.node}>"
