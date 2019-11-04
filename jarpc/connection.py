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


import uuid
import asyncio
import logging

from typing import Any, Tuple, Union, Mapping, Optional

import aioredis

from .abc import ABCConnection
from .enums import MessageType
from .typing import Serializer, Deserializer
from .request import Request
from .response import Response

log = logging.getLogger(__name__)


_payload_value_to_type = {b"0": MessageType.REQUEST, b"1": MessageType.RESPONSE}
_payload_type_to_value = {v: k for k, v in _payload_value_to_type.items()}


class Connection(ABCConnection):

    __slots__ = ("_name", "_node" "_loop", "_ready", "_loads", "_dumps", "_sub", "_pub")

    def __init__(
        self,
        name: str,
        loads: Optional[Deserializer] = None,
        dumps: Optional[Serializer] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        node: Optional[str] = None,
    ):
        self._name = f"rpc:{name}"
        self._node = uuid.uuid4().hex if node is None else node

        self._loop = asyncio.get_event_loop() if loop is None else loop
        self._ready = asyncio.Event()

        if loads and dumps:
            self._loads = loads
            self._dumps = dumps
        elif loads is None and dumps is None:
            import marshal

            self._loads = marshal.loads
            self._dumps = marshal.dumps
        else:
            raise ValueError("You cannot define only one of dumps and loads.")

    async def start(
        self, redis_address: Union[Tuple[str, int], str], **kwargs: Any
    ) -> None:
        """Starts processing messages."""

        self._sub = await aioredis.create_redis(
            redis_address, loop=self._loop, **kwargs
        )
        self._pub = await aioredis.create_redis(
            redis_address, loop=self._loop, **kwargs
        )

        channels = await self._sub.subscribe(self._name)
        assert len(channels) == 1

        self._ready.set()

        log.info(f"sub: connected: {self._name}")
        log.info(f"pub: connected: {self._name}")

        await self._handler(channels[0])

    def run(self, *args: Any, **kwargs: Any) -> None:
        """
        A blocking way to launch message processing.
        Takes same arguments as Connection.start.
        """

        self._loop.run_until_complete(self.start(*args, **kwargs))

    async def wait_until_ready(self) -> None:
        """Waits until connection is established."""

        await self._ready.wait()

    async def _handler(self, channel: aioredis.pubsub.Channel) -> None:
        async for msg in channel.iter():
            # TODO: parser
            message_type_byte = msg[0:1]
            msg_type = _payload_value_to_type.get(
                message_type_byte, MessageType.UNKNOWN_TYPE
            )
            if msg_type == MessageType.UNKNOWN_TYPE:
                log.warn(f"Unknown payload type: {message_type_byte}")
                continue

            try:
                data = self._loads(msg[1:])
            except Exception:
                # address is unavailable
                # await self._respond(request.address, StatusCode.BAD_FORMAT)

                log.exception(
                    "could not deserialize payload. Make sure to use same algorithm on both ends"
                )
                continue

            if msg_type == MessageType.REQUEST:
                request = self._make_request(data)
                if request is not None:
                    await self._handle_request(request)

            elif msg_type == MessageType.RESPONSE:
                response = self._make_response(data)
                if response is not None:
                    await self._handle_response(response)

    def _make_request(self, data: Any) -> Optional[Request]:
        """Called for creating request from data. Overridable."""

        return None

    def _make_response(self, data: Any) -> Optional[Response]:
        """Called for creating response from data. Overridable."""

        return None

    async def _handle_request(self, request: Request) -> None:
        """Called for handling request. Overridable."""

        pass

    async def _handle_response(self, response: Response) -> None:
        """Called for handling response. Overridable."""

        pass

    async def _send_request(self, payload: Mapping[str, Any]) -> None:
        """Sends payload of request type."""

        await self._send(payload, _payload_type_to_value[MessageType.REQUEST])

    async def _send_response(self, payload: Mapping[str, Any]) -> None:
        """Sends payload of response type."""

        await self._send(payload, _payload_type_to_value[MessageType.RESPONSE])

    async def _send(self, payload: Mapping[str, Any], pl_type: bytes) -> None:
        """Sends payload of given type."""

        encoded = self._dumps(payload)
        if isinstance(encoded, str):
            encoded = encoded.encode()

        encoded = pl_type + encoded

        num_listeners = await self._pub.publish(self._name, encoded)
        log.debug(f"delivered to {num_listeners} listeners")

    def close(self) -> None:
        """Closes connection."""

        log.info("closing connections")

        self._ready.clear()

        self._sub.close()
        self._pub.close()

    @property
    def name(self) -> str:
        """Connection name."""

        return self._name

    @property
    def node(self) -> str:
        """Node identifier."""

        return self._node

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} node={self.node}>"
