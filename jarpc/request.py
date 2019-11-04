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

import warnings

from typing import Any, Dict, Optional

from .abc import ABCServer
from .enums import StatusCode
from .constants import NoValue


class Request:

    __slots__ = (
        "server",
        "command_index",
        "node",
        "_data",
        "_address",
        "_reply_called",
    )

    def __init__(
        self,
        server: ABCServer,
        command_index: int,
        node: str,
        data: Any,
        address: Optional[str],
    ):
        self.server = server

        self.command_index = command_index
        self.node = node

        self._data = data
        self._address = address

        self._reply_called = False

    @classmethod
    def from_data(cls, server: ABCServer, payload: Dict[str, Any]) -> "Request":
        return cls(
            server=server,
            command_index=payload["c"],
            node=payload["n"],
            data=payload.get("d", {}),
            address=payload.get("a"),
        )

    async def reply(self, data: Any) -> None:
        await self._reply_with_status(data)

    async def _reply_with_status(
        self, data: Any = NoValue, status: StatusCode = StatusCode.SUCCESS
    ) -> None:
        if self._reply_called:
            warnings.warn(
                "Reply function was called already. Using it multiple times may cause problems"
            )
        else:
            self._reply_called = True
            await self.server.reply(address=self._address, data=data, status=status)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} command_index={self.command_index}>"
