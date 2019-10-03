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

import json
import time
import uuid
import asyncio
import logging

from typing import Any, Dict, List, Tuple, Union, Optional, Generator

import aioredis

from .abc import ABCClient, ResponsesIterator
from .response import Response

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
        client: Client,
        queue: asyncio.Queue[Response],
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
        async def coro() -> List[Response]:
            return [resp async for resp in self]

        return coro().__await__()

    def __aiter__(self) -> ResponsesWithTimeout:
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
        return self._responses_seen

    @property
    def time_remaining(self) -> float:
        return self._timeout - time.time() + self._start_time

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} time_remaining={self.time_remaining} responses_seen={self.responses_seen}>"


class EmtpyResponses(ResponsesIterator):
    """Looks and behaves the same way as ResponsesWithTimeout, but is empty."""

    def __await__(self) -> Generator[Any, None, List[Response]]:
        async def coro() -> List[Response]:
            return []

        return coro().__await__()

    def __aiter__(self) -> EmtpyResponses:
        return self

    async def __anext__(self) -> Response:
        raise StopAsyncIteration


class Client(ABCClient):
    """RPC client sends commands to servers and listens for responses."""

    def __init__(
        self,
        channel_name: str,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        default_timeout: Optional[int] = None,
        default_expect_responses: Optional[int] = None,
    ):
        self._call_address = f"rpc:{channel_name}"
        self._resp_address = f"{self._call_address}-response"

        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop

        self._default_timeout = default_timeout
        self._default_expect_responses = default_expect_responses

        self._listeners: Dict[str, asyncio.Queue[Response]] = {}

    async def start(
        self, redis_address: Union[Tuple[str, int], str], **kwargs: Any
    ) -> None:
        """Starts client."""

        self._call_conn = await aioredis.create_redis(
            redis_address, loop=self._loop, **kwargs
        )
        self._resp_conn = await aioredis.create_redis(
            redis_address, loop=self._loop, **kwargs
        )

        channels = await self._resp_conn.subscribe(self._resp_address)

        log.info(f"listening: {self._resp_address}")
        log.info(f"calling: {self._call_address}")

        await self._handler(channels[0])

    def run(self, *args: Any, **kwargs: Any) -> None:
        """A blocking way to start client. Takes same arguments as Server.start."""

        self._loop.run_until_complete(self.start(*args, **kwargs))

    async def _handler(self, channel: aioredis.pubsub.Channel) -> None:
        async for msg in channel.iter():
            try:
                response = Response.from_data(json.loads(msg))
            except Exception as e:
                log.error(f"error parsing response: {e.__class__.__name__}: {e}")
                continue

            log.info(f"received response from node {response.node}")

            queue = self._listeners.get(response._address)
            if queue is None:
                log.debug(f"ignoring response from node {response.node}")
                continue

            await queue.put(response)

    def _add_queue(self, address: str, queue: asyncio.Queue[Response]) -> None:
        self._listeners[address] = queue

    def _remove_queue(self, address: str) -> None:
        self._listeners.pop(address, None)

    async def _send(self, payload: Dict[str, Any]) -> None:
        num_listeners = await self._call_conn.publish_json(self._call_address, payload)
        log.debug(f"delivered to {num_listeners} listeners")

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

        log.info(f"sending command {command_index}")

        payload = {"c": command_index, "d": data}

        if timeout is None:
            timeout = self._default_timeout

        if timeout is not None:
            address = uuid.uuid4().hex
            payload["a"] = address

            queue: asyncio.Queue[Response] = asyncio.Queue(loop=self._loop)
            self._add_queue(address, queue)

        asyncio.create_task(self._send(payload))

        if timeout is None:
            return EmtpyResponses()
        else:
            return ResponsesWithTimeout(
                self,
                queue,
                address,
                timeout,
                expect_responses or self._default_expect_responses,
            )

    def close(self) -> None:
        """Closes connections stopping client."""

        log.info("closing connections")

        self._call_conn.close()
        self._resp_conn.close()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} call_address={self._call_address} resp_address={self._resp_address}>"
