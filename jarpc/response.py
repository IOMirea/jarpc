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

from typing import Any, Dict

from .enums import StatusCode


class Response:

    __slots__ = ("status", "node", "data", "_address")

    def __init__(self, status: StatusCode, node: str, data: Any, address: str):
        self.status = status
        self.node = node
        self.data = data

        self._address = address

    @classmethod
    def from_data(cls, payload: Dict[str, Any]) -> "Response":
        return cls(
            status=StatusCode(payload["s"]),
            node=payload["n"],
            data=payload.get("d", {}),
            address=payload["a"],
        )

    def __str__(self) -> str:
        return str(self.data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} status={self.status} node={self.node} data={self.data}>"
