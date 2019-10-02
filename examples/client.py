# NOTE: server should be started first, check server.py example

import asyncio

from iomirea_rpc import Client

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0
COMMAND_SLOW_PING = 1
COMMAND_MULTIPLE_RESPONSES = 2
COMMAND_FIX_CODE = 999


async def call_commands(client: Client) -> None:
    # wait for client to establish connection
    await asyncio.sleep(1)

    ping_data = {"message": input("Enter message to send or leave blank: ")}

    print("Calling PING: ", end="", flush=True)
    print(await client.call(COMMAND_PING, ping_data))

    print("Calling SLOW_PING: ", end="", flush=True)
    print(await client.call(COMMAND_SLOW_PING, timeout=1))

    print("Calling unknown command: ", end="", flush=True)
    print(await client.call(COMMAND_FIX_CODE))

    # exit
    client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    client = Client("example", loop=loop, default_timeout=5, default_expect_responses=1)

    loop.create_task(client.run((REDIS_HOST, REDIS_PORT)))
    loop.run_until_complete(call_commands(client))
