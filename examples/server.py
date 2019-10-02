# NOTE: see client.py example

import os
import random
import asyncio

from iomirea_rpc import Server, Request

REDIS_HOST = "localhost"
REDIS_PORT = 6379

server = Server("example", node=f"example-{os.getpid()}")


@server.command(0)
async def ping(req: Request, message: str = "") -> str:
    """Responds with provided message argument or 'pong'."""

    print("Received PING command")

    return "pong" if message == "" else message


@server.command(1)
async def slow_ping(req: Request) -> str:
    """Responds with 'pong' after 2 seconds, too slow..."""

    print("Received SLOW_PING command")

    await asyncio.sleep(2)

    return "pong"


@server.command(2)
async def multiple_responses(req: Request) -> None:
    """Sends random number 5 times."""

    print("Received MULTIPLE_RESPONSES")

    for i in range(5):
        await req.reply(random.randint(0, 42))
        await asyncio.sleep(1)


if __name__ == "__main__":
    server.run((REDIS_HOST, REDIS_PORT))
