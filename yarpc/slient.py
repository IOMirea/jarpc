from .client import Client
from .server import Server
from .request import Request


class Slient(Client, Server):
    """Slient combines functionality of Client and Server."""

    async def _handle_request(self, request: Request) -> None:
        if request.node == self.node:
            # ignore requests sent from this slient
            return

        await super()._handle_request(request)
