# NOTE: server should be started first, check server.py example

import asyncio

from iomirea_rpc import Client

REDIS_HOST = "localhost"
REDIS_PORT = 6379


async def call_commands(client: Client) -> None:
    # wait for client to establish connection
    await asyncio.sleep(1)

    ping_data = {"message": input("Enter message to send or leave blank: ")}

    print("Calling ping:", await client.call(0, ping_data, timeout=1))
    print("Calling late ping:", await client.call(1, timeout=1))

    # wait for late ping response
    await asyncio.sleep(2)

    print("Calling unknown command:", await client.call(999, timeout=1))

    # exit
    client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    client = Client("example", loop=loop)

    loop.create_task(call_commands(client))
    loop.run_until_complete(client.run((REDIS_HOST, REDIS_PORT)))
