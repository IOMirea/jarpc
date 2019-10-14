import random
import asyncio

from yarpc import Client, Server, Request

REDIS_HOST = "localhost"
REDIS_PORT = 6379

NUM_SERVERS = 10

COMMAND_PING = 0


async def random_ping(req: Request) -> str:
    """Sleeps for random time, then responds."""

    sleep_seconds = random.uniform(0, 5)
    await asyncio.sleep(sleep_seconds)

    return f"pong! I slept for {round(sleep_seconds, 1)} seconds"


async def main() -> None:
    client = Client(
        "response_iterator", default_timeout=5, default_expect_responses=NUM_SERVERS
    )
    servers = [
        Server("response_iterator", node=f"node-{i}") for i in range(NUM_SERVERS)
    ]

    for server in servers:
        server.add_command(COMMAND_PING, random_ping)

    print(f"Starting 1 client and {NUM_SERVERS} servers")
    loop = asyncio.get_event_loop()

    for i in (client, *servers):
        loop.create_task(i.start((REDIS_HOST, REDIS_PORT)))

    await asyncio.wait(
        (client.wait_until_ready(), *[s.wait_until_ready() for s in servers])
    )

    print("Sending request")
    async for response in client.call(COMMAND_PING):
        print(f"{response.node}: {response.data}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
