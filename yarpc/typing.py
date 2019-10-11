# yarpc - yet another RPC
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

from typing import Any, Union, Callable

# These types are only useful for library users.
# Variable having these types will produce typing errors upon use in internal code.
# These errors should be explicitly suppressed.
_Serializer = Union[Callable[[Any], bytes], Callable[[Any], str]]
_Deserializer = Union[Callable[[bytes], Any], Callable[[str], Any]]

_CommandType = Any

# TODO: annotate _CommandType properly.
# Possible solutions (do not work for different reasons)
#
# typing_extensions.Protocol
# class _CommandType(Protocol):
#     def __call__(self, __request: Request, **kwargs: Any) -> Any:
#         ...
#
# mypy_extensions.KwArg
# _CommandType = Callable[["Server", KwArg(Any)], Awaitable[Any]]
#
# typing.TypeVar ?
