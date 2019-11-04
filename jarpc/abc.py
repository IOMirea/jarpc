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

import abc

from typing import Any, Dict, List, Tuple, Union, Optional, Generator

from .enums import StatusCode
from .typing import CommandType
from .response import Response

__all__ = ("ResponsesIterator", "ABCConnection", "ABCClient", "ABCServer")


class ResponsesIterator(abc.ABC):
    """
    Provides access to command responses.

    Instances can be awaited to get all responses at once or used as async iterator to
    process responses as soon as they come.
    """

    @abc.abstractmethod
    def __await__(self) -> Generator[Any, None, List[Response]]:
        """Returns all responses once they are ready."""

    @abc.abstractmethod
    def __aiter__(self) -> "ResponsesIterator":
        ...

    @abc.abstractmethod
    async def __anext__(self) -> Response:
        ...


class ABCConnection(abc.ABC):
    """RPC Connection."""

    @abc.abstractproperty
    def name(self) -> str:
        """Connection name."""

    @abc.abstractproperty
    def node(self) -> str:
        """Node identifier."""

    @abc.abstractmethod
    async def start(
        self, redis_address: Union[Tuple[str, int], str], **kwargs: Any
    ) -> None:
        """Starts processing messages."""

    @abc.abstractmethod
    def close(self) -> None:
        """Closes connection."""


class ABCClient(ABCConnection):
    """Calls commands."""

    @abc.abstractmethod
    def call(
        self,
        command_index: int,
        data: Dict[str, Any] = {},
        timeout: Optional[float] = None,
        expect_responses: int = 0,
    ) -> ResponsesIterator:
        """Calls command by index."""


class ABCServer(ABCConnection):
    """Responds to commands."""

    @abc.abstractmethod
    def add_command(self, index: int, fn: CommandType) -> int:
        """Registers new command."""

    @abc.abstractmethod
    def remove_command(self, index: int) -> CommandType:
        """Removes existing command."""

    @abc.abstractmethod
    async def reply(
        self, *, address: Optional[str], status: StatusCode, data: Any
    ) -> None:
        """Sends response to address."""
