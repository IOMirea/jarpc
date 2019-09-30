# NOTE: see client.py example

import os
import asyncio

from iomirea_rpc import Server, Request

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0
COMMAND_SLOW_PING = 1


async def ping(srv: Server, req: Request, message: str = "") -> str:
    """Responds with provided message argument or 'pong'."""

    print("Recieved PING command")

    return "pong" if message == "" else message


async def slow_ping(srv: Server, req: Request) -> str:
    """Responds with 'pong' after 2 seconds, too slow..."""

    print("Recieved SLOW_PING command")

    await asyncio.sleep(2)

    return "ping"


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    server = Server("example", loop=loop, node=f"example-{os.getpid()}")
    server.register_command(COMMAND_PING, ping)
    server.register_command(COMMAND_SLOW_PING, slow_ping)

    loop.run_until_complete(server.run((REDIS_HOST, REDIS_PORT)))
