import os
import asyncio

from jarpc import Slient, Request

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0

loop = asyncio.get_event_loop()

slient = Slient(
    "example",
    loop=loop,
    node=f"example-{os.getpid()}",
    default_timeout=5,
    default_expect_responses=1,
)


@slient.command(COMMAND_PING)
async def ping(req: Request, message: str = "") -> str:
    """Responds with provided message argument or 'pong'."""

    print("Received PING command")

    return "pong" if message == "" else message


async def call_ping(slient: Slient) -> None:
    await slient.wait_until_ready()

    print("PING ->", await slient.call(COMMAND_PING))


if __name__ == "__main__":
    loop.create_task(slient.start((REDIS_HOST, REDIS_PORT)))
    loop.create_task(call_ping(slient))

    # continue listening for commands
    loop.run_forever()
