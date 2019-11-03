# jarpc - just another RPC
# Copyright (C) 2019  Eugene Ershov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

from typing import Any, Dict, Callable, Optional

from .abc import ABCServer
from .enums import StatusCode
from .typing import CommandType
from .request import Request
from .constants import NoValue
from .connection import Connection

log = logging.getLogger(__name__)


class Server(Connection, ABCServer):
    """Listens for commands from clients and sends responses."""

    # NOTE: defining different __slots__ in Client and Server causes error creating
    # Slient

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self._commands: Dict[int, CommandType] = {}

    def command(self, index: int) -> Callable[[CommandType], None]:
        """Flask-style decorator used to register commands. Calls register_command."""

        def inner(func: CommandType) -> None:
            self.add_command(index, func)

        return inner

    def add_command(self, index: int, fn: CommandType) -> int:
        """Registers new command. Raises ValueError if index already used."""

        if index in self._commands:
            raise ValueError("Command with index %d already registered", index)

        self._commands[index] = fn

        return index

    def remove_command(self, index: int) -> CommandType:
        """Removes existing command. Raises ValueError if index not found."""

        if index not in self._commands:
            raise ValueError("Command with index %d is not registered", index)

        return self._commands.pop(index)

    def _make_request(self, data: Any) -> Optional[Request]:
        return Request.from_data(self, data)

    async def _handle_request(self, request: Request) -> None:
        log.info("received command %d", request.command_index)

        fn = self._commands.get(request.command_index)
        if fn is None:
            log.warning("unknown command %d", request.command_index)

            await request._reply_with_status(status=StatusCode.UNKNOWN_COMMAND)

            return

        try:
            command = fn(request, **request._data)
        except TypeError as e:
            log.error("bad arguments given to %d: %s", request.command_index, str(e))

            await request._reply_with_status(str(e), StatusCode.BAD_PARAMS)

            return

        try:
            command_result = await command
        except Exception as e:
            log.error(
                "error calling command %d %s: %s",
                request.command_index,
                e.__class__.__name__,
                str(e),
            )

            await request._reply_with_status(str(e), StatusCode.INTERNAL_ERROR)

            return

        if command_result is None:
            # Special case, should be documented.
            # Returning None is allowed using request.reply
            return

        await request.reply(command_result)

    async def reply(
        self, *, address: Optional[str], status: StatusCode, data: Any
    ) -> None:
        """Sends response to address (if address is present)."""

        if address is None:
            log.debug("no address, unable to respond")
            return

        payload = {"s": status.value, "n": self.node, "a": address}

        if data is not NoValue:
            payload["d"] = data

        await self._send_response(payload)
