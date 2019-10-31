import asyncio

from yarpc import Client

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0
COMMAND_SLOW_PING = 1
COMMAND_FIX_BUGS = 42


async def main() -> None:
    client = Client("example", default_timeout=5, default_expect_responses=1)

    loop = asyncio.get_event_loop()
    loop.create_task(client.start((REDIS_HOST, REDIS_PORT)))

    await client.wait_until_ready()

    ping_data = {"message": input("Enter message to send or leave blank: ")}

    print("PING      ->", await client.call(COMMAND_PING, ping_data))
    print("SLOW_PING ->", await client.call(COMMAND_SLOW_PING, timeout=1))
    print("FIX_BUGS  ->", await client.call(COMMAND_FIX_BUGS))

    # exit
    client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
