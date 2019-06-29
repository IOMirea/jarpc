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

from typing import Any, Dict


class Request:

    __slots__ = ("command_index", "address", "_data")

    def __init__(self, command_index: int, address: str, data: Any):
        self.command_index = command_index
        self.address = address

        self._data = data

    @classmethod
    def from_json(cls, payload: Dict[str, Any]) -> Request:
        return cls(
            command_index=payload["c"],
            address=payload["a"],
            data=payload.get("d", {}),
        )

    def __repr__(self) -> str:
        return (
            f"<Request command_index={self.command_index} data={self._data}>"
        )
