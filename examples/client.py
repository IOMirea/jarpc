# NOTE: server should be started first, check server.py example

import asyncio

from iomirea_rpc import Client, Server


REDIS_HOST = "localhost"
REDIS_PORT = 6379


async def call_ping(client: Client) -> None:
    # wait for server to start
    await asyncio.sleep(1)

    data = {"message": input("Enter message to send or leave blank: ")}

    print("Ping responses:", await client.call(0, data, timeout=1))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    client = Client("example", loop=loop)

    loop.create_task(client.run((REDIS_HOST, REDIS_PORT)))
    loop.create_task(call_ping(client))
    loop.run_forever()
