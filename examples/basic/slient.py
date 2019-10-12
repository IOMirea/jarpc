import os
import asyncio

from yarpc import Slient, Request

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0

loop = asyncio.get_event_loop()

sl = Slient(
    "example",
    loop=loop,
    node=f"example-{os.getpid()}",
    default_timeout=5,
    default_expect_responses=1,
)


@sl.command(COMMAND_PING)
async def ping(req: Request, message: str = "") -> str:
    """Responds with provided message argument or 'pong'."""

    print("Received PING command")

    return "pong" if message == "" else message


async def call_commands(sl: Slient) -> None:
    # wait for client to establish connection
    await asyncio.sleep(1)

    print("Calling PING: ", end="", flush=True)
    print(await sl.call(COMMAND_PING))


if __name__ == "__main__":
    loop.create_task(sl.start((REDIS_HOST, REDIS_PORT)))
    loop.create_task(call_commands(sl))
    loop.run_forever()
