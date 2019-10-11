import os
import asyncio

from yarpc import Request, ClientServer

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0

loop = asyncio.get_event_loop()

cs = ClientServer(
    "example",
    loop=loop,
    node=f"example-{os.getpid()}",
    default_timeout=5,
    default_expect_responses=1,
)


@cs.command(COMMAND_PING)
async def ping(req: Request, message: str = "") -> str:
    """Responds with provided message argument or 'pong'."""

    print("Received PING command")

    return "pong" if message == "" else message


async def call_commands(cs: ClientServer) -> None:
    # wait for client to establish connection
    await asyncio.sleep(1)

    print("Calling PING: ", end="", flush=True)
    print(await cs.call(COMMAND_PING))


if __name__ == "__main__":
    loop.create_task(cs.start((REDIS_HOST, REDIS_PORT)))
    loop.create_task(call_commands(cs))
    loop.run_forever()
