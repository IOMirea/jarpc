import os
import asyncio
import logging

from yarpc import Server, Request

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0
COMMAND_SLOW_PING = 1

server = Server("example", node=f"example-{os.getpid()}")
logging.basicConfig(level=logging.DEBUG)


@server.command(COMMAND_PING)
async def ping(req: Request, message: str = "") -> str:
    """Responds with provided message argument or 'pong'."""

    print("Received PING command")

    return "pong" if message == "" else message


@server.command(COMMAND_SLOW_PING)
async def slow_ping(req: Request) -> str:
    """Responds with 'pong' after 2 seconds, too slow..."""

    print("Received SLOW_PING command")

    await asyncio.sleep(2)

    return "pong"


if __name__ == "__main__":
    try:
        server.run((REDIS_HOST, REDIS_PORT))
    except KeyboardInterrupt:
        for task in asyncio.all_tasks():
            task.cancel()