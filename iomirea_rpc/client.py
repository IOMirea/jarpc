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

from .response import Response

log = logging.getLogger(__name__)


class ResponsesWithTimeout:
    """
    Provides access to command responses for limited time.

    Instances can be awaited to get all responses at once or used as async iterator to
    process responses as soon as they come.

    If timeout is not provided, response processing is skipped completely.
    """

    __slots__ = ("_client", "_address", "_timeout", "_start_time", "_queue")

    def __init__(self, client: Client, address: str, timeout: Optional[int] = None):
        self._client = client
        self._address = address
        self._timeout = timeout

        self._start_time = time.time()

        if timeout is not None:
            self._queue: asyncio.Queue[Response] = asyncio.Queue(
                loop=self._client._loop
            )
            self._client._add_queue(address, self._queue)

    def __await__(self) -> Generator[Any, None, List[Response]]:
        async def coro() -> List[Response]:
            return [resp async for resp in self]

        return coro().__await__()

    def __aiter__(self) -> ResponsesWithTimeout:
        return self

    async def __anext__(self) -> Response:
        if self._timeout is None:
            raise StopAsyncIteration

        time_remaining = self._timeout - time.time() + self._start_time

        try:
            return await asyncio.wait_for(
                self._queue.get(), timeout=time_remaining, loop=self._client._loop
            )
        except asyncio.TimeoutError:
            raise StopAsyncIteration

    def __del__(self) -> None:
        self._client._remove_queue(self._address)


class Client:
    """RPC client sends commands to servers and listens for responses."""

    def __init__(
        self,
        channel_name: str,
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
    ):
        self._call_address = f"rpc:{channel_name}"
        self._resp_address = f"{self._call_address}-response"

        self._loop = loop

        self._listeners: Dict[str, asyncio.Queue[Response]] = {}

    async def run(
        self, redis_address: Union[Tuple[str, int], str], **kwargs: Any
    ) -> None:
        """Launches client."""

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

    async def _handler(self, channel: aioredis.pubsub.Channel) -> None:
        async for msg in channel.iter():
            try:
                response = Response.from_json(json.loads(msg))
            except Exception as e:
                log.error(f"error parsing response: {e.__class__.__name__}: {e}")
                continue

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
        timeout: Optional[int] = None,
    ) -> ResponsesWithTimeout:
        """
        Calls command and returns received responses. Skips response processing
        completely if timeout is None.
        """

        log.info(f"sending command {command_index}")

        payload = {"c": command_index, "d": data}

        if timeout is not None:
            address = uuid.uuid4().hex
            payload["a"] = address
        else:
            address = ""

        asyncio.create_task(self._send(payload))

        return ResponsesWithTimeout(self, address, timeout)

    def close(self) -> None:
        """Closes connections stopping client."""

        log.info("closing connections")

        self._call_conn.close()
        self._resp_conn.close()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} call_address={self._call_address} resp_address={self._resp_address}>"
