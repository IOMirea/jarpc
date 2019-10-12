from .client import Client
from .server import Server
from .request import Request


class Slient(Client, Server):
    """Slient combines functionality of Client and Server."""

    async def _handle_request(self, request: Request) -> None:
        if request._address in self._listeners:
            # ignore our own commands
            return

        await super()._handle_request(request)
