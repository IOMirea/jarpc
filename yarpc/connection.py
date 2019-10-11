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


import asyncio
import logging

from typing import Any, Tuple, Union, Optional

import aioredis

from .enums import PayloadType
from .typing import _Serializer, _Deserializer
from .request import Request
from .response import Response

log = logging.getLogger(__name__)


_payload_value_to_type = {
    "0": PayloadType.REQUEST,
    "1": PayloadType.RESPONSE,
    b"0": PayloadType.REQUEST,
    b"1": PayloadType.RESPONSE,
}

_payload_type_to_value = {PayloadType.REQUEST: b"0", PayloadType.RESPONSE: b"1"}


class Connection:

    __slots__ = (
        "_name",
        "_sub_address",
        "_pub_address",
        "_loop",
        "_loads",
        "_dumps",
        "_sub",
        "_pub",
    )

    def __init__(
        self,
        name: str,
        loads: Optional[_Deserializer] = None,
        dumps: Optional[_Serializer] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        node: Optional[str] = None,
    ):
        self._name = f"rpc:{name}"

        self._loop = asyncio.get_event_loop() if loop is None else loop

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
        """Starts client."""

        self._sub = await aioredis.create_redis(
            redis_address, loop=self._loop, **kwargs
        )
        self._pub = await aioredis.create_redis(
            redis_address, loop=self._loop, **kwargs
        )

        channels = await self._sub.subscribe(self._name)
        assert len(channels) == 1

        log.info(f"sub: connected: {self._name}")
        log.info(f"pub: connected: {self._name}")

        await self._handler(channels[0])

    def run(self, *args: Any, **kwargs: Any) -> None:
        """A blocking way to start connection. Takes same arguments as Connection.start."""

        self._loop.run_until_complete(self.start(*args, **kwargs))

    async def _handler(self, channel: aioredis.pubsub.Channel) -> None:
        async for msg in channel.iter():
            try:
                # TODO: parser
                pl_type = _payload_value_to_type.get(msg[0:1], PayloadType.UNKNOWN_TYPE)
                if pl_type == PayloadType.UNKNOWN_TYPE:
                    log.error("Unknown payload type: %d", pl_type.value)
                    continue

                data = self._loads(msg[1:])
            except Exception as e:
                log.error(f"error parsing request: {e.__class__.__name__}: {e}")

                # address is unavailable
                # await self._respond(request.address, StatusCode.BAD_FORMAT)
                continue

            if pl_type == PayloadType.REQUEST:
                request = self._make_request(data)
                if request is not None:
                    await self._handle_request(request)

            elif pl_type == PayloadType.RESPONSE:
                response = self._make_response(data)
                if response is not None:
                    await self._handle_response(response)

    def _make_request(self, data: Any) -> Optional[Request]:
        return None

    def _make_response(self, data: Any) -> Optional[Response]:
        return None

    async def _handle_request(self, request: Request) -> None:
        pass

    async def _handle_response(self, response: Response) -> None:
        pass

    async def _send_request(self, payload: Union[bytes, str]) -> None:
        await self._send(payload, _payload_type_to_value[PayloadType.REQUEST])

    async def _send_response(self, payload: Union[bytes, str]) -> None:
        await self._send(payload, _payload_type_to_value[PayloadType.RESPONSE])

    async def _send(self, payload: Union[bytes, str], pl_type: bytes) -> None:
        if isinstance(payload, str):
            payload = pl_type.decode() + payload
        else:
            payload = pl_type + payload

        num_listeners = await self._pub.publish(self._name, payload)
        log.debug(f"delivered to {num_listeners} listeners")

    def close(self) -> None:
        """Closes connection."""

        log.info("closing connections")

        self._sub.close()
        self._pub.close()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
