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

import time
import uuid
import asyncio
import logging

from typing import Any, Dict, List, Optional, Generator

from .abc import ABCClient, ResponsesIterator
from .typing import TypedQueue
from .response import Response
from .connection import Connection

log = logging.getLogger(__name__)


class ResponsesWithTimeout(ResponsesIterator):
    """Provides access to command responses for limited time."""

    __slots__ = (
        "_client",
        "_address",
        "_timeout",
        "_expect_responses",
        "_responses_seen",
        "_start_time",
        "_queue",
    )

    def __init__(
        self,
        client: "Client",
        queue: TypedQueue[Response],
        address: str,
        timeout: float,
        expect_responses: Optional[int] = None,
    ):
        self._client = client
        self._queue = queue
        self._address = address
        self._timeout = timeout

        if expect_responses is None:
            expect_responses = 0

        if expect_responses < 0:
            raise ValueError("expect_responses should be >= 0")

        self._expect_responses = expect_responses

        self._responses_seen = 0

        self._start_time = time.time()

    def __await__(self) -> Generator[Any, None, List[Response]]:
        """Returns all responses once they are ready."""

        async def coro() -> List[Response]:
            return [resp async for resp in self]

        return coro().__await__()

    def __aiter__(self) -> "ResponsesWithTimeout":
        return self

    async def __anext__(self) -> Response:
        if (
            self._expect_responses != 0
            and self._expect_responses == self._responses_seen
        ):
            raise StopAsyncIteration

        try:
            resp = await asyncio.wait_for(
                self._queue.get(), timeout=self.time_remaining, loop=self._client._loop
            )
        except asyncio.TimeoutError:
            raise StopAsyncIteration

        self._responses_seen += 1

        return resp

    def __del__(self) -> None:
        self._client._remove_queue(self._address)

    @property
    def responses_seen(self) -> int:
        """Amount of yielded responses."""

        return self._responses_seen

    @property
    def time_remaining(self) -> float:
        """Remaining time until iterator is closed."""

        return self._timeout - time.time() + self._start_time

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} time_remaining={self.time_remaining} responses_seen={self.responses_seen}>"


class EmptyResponses(ResponsesIterator):
    """Behaves the same way as ResponsesWithTimeout, except it is empty."""

    def __await__(self) -> Generator[Any, None, List[Response]]:
        """Returns empty list of responses."""

        async def coro() -> List[Response]:
            return []

        return coro().__await__()

    def __aiter__(self) -> "EmptyResponses":
        return self

    async def __anext__(self) -> Response:
        raise StopAsyncIteration


class Client(Connection, ABCClient):
    """Sends commands to servers and listens for responses."""

    # NOTE: defining different __slots__ in Client and Server causes error creating
    # Slient

    def __init__(
        self,
        *args: Any,
        default_timeout: Optional[int] = None,
        default_expect_responses: Optional[int] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        self._default_timeout = default_timeout
        self._default_expect_responses = default_expect_responses

        self._listeners: Dict[str, TypedQueue[Response]] = {}

    def _make_response(self, data: Any) -> Optional[Response]:
        return Response.from_data(data)

    async def _handle_response(self, response: Response) -> None:
        log.info("received response from node %s", response.node)

        queue = self._listeners.get(response._address)
        if queue is None:
            log.debug("ignoring response from node %s", response.node)
            return

        await queue.put(response)

    def _add_queue(self, address: str, queue: TypedQueue[Response]) -> None:
        self._listeners[address] = queue

    def _remove_queue(self, address: str) -> None:
        self._listeners.pop(address, None)

    def call(
        self,
        command_index: int,
        data: Dict[str, Any] = {},
        timeout: Optional[float] = None,
        expect_responses: Optional[int] = None,
    ) -> ResponsesIterator:
        """
        Calls command and returns received responses. Skips response processing
        completely if timeout is None.
        """

        log.info("sending command %d", command_index)

        payload = {"n": self._node, "c": command_index, "d": data}

        if timeout is None:
            timeout = self._default_timeout

        if timeout is not None:
            address = uuid.uuid4().hex
            payload["a"] = address

            queue: TypedQueue[Response] = TypedQueue(loop=self._loop)
            self._add_queue(address, queue)

        self._loop.create_task(self._send_request(payload))

        if timeout is None:
            return EmptyResponses()
        else:
            return ResponsesWithTimeout(
                self,
                queue,
                address,
                timeout,
                expect_responses or self._default_expect_responses,
            )
