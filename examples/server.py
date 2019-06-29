# NOTE: see client.py example

import os
import asyncio

from iomirea_rpc import Server, Request


REDIS_HOST = "localhost"
REDIS_PORT = 6379


async def ping(srv: Server, req: Request, message: str = "") -> str:
    # responds with provided message argument or "pong"

    return "pong" if message == "" else message


async def late_ping(srv: Server, req: Request) -> str:
    # responds with "pong" after 2 seconds

    await asyncio.sleep(2)

    return "ping"


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    server = Server("example", loop=loop, node=f"example-{os.getpid()}")
    server.register_command(0, ping)
    server.register_command(1, late_ping)

    loop.run_until_complete(server.run((REDIS_HOST, REDIS_PORT)))
