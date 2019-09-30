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
    print(await client.call(COMMAND_PING, ping_data, timeout=1).flatten())
    print("Calling SLOW_PING: ", end="", flush=True)
    print(await client.call(COMMAND_SLOW_PING, timeout=1).flatten())

    # wait for slow ping (response will be ignored because timeout ends before it responds)
    print("Waiting ...")
    await asyncio.sleep(2)

    print("Calling MULTIPLE_RESPONSES: ", end="", flush=True)
    async for resp in client.call(COMMAND_MULTIPLE_RESPONSES, timeout=5):
        print(resp.data, end=" ", flush=True)
    print()

    print("Calling unknown command: ", end="", flush=True)
    print(await client.call(COMMAND_FIX_CODE, timeout=1).flatten())

    # exit
    client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    client = Client("example", loop=loop)

    loop.create_task(call_commands(client))
    loop.run_until_complete(client.run((REDIS_HOST, REDIS_PORT)))
