import json
import pickle
import asyncio

from typing import Any

from yarpc import Client, Server, Request

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0


async def ping(req: Request, data: Any) -> str:
    """Prints data and sends it back."""

    print("Received data (client):", data)

    return data


async def main() -> None:
    await test_encoder(json)
    await test_encoder(pickle)


async def test_encoder(encoder: Any) -> None:
    print("Testing encoder", encoder)

    client = Client(
        "custom_encoder",
        default_expect_responses=1,
        loads=encoder.loads,
        dumps=encoder.dumps,
    )
    server = Server("custom_encoder", loads=encoder.loads, dumps=encoder.dumps)
    server.add_command(COMMAND_PING, ping)

    loop = asyncio.get_event_loop()

    loop.create_task(client.start((REDIS_HOST, REDIS_PORT)))
    loop.create_task(server.start((REDIS_HOST, REDIS_PORT)))

    await client.wait_until_ready()
    await server.wait_until_ready()

    # NOTE: json encoder does not support bytes
    data = {"data": dict(int=42, str="str", list=(1, 2, 3), dict={"a": "b"})}

    responses = await client.call(COMMAND_PING, data, timeout=5)
    assert len(responses) == 1, "Wrong number of responses (if any)"

    print("Received data (server):", responses[0].data)

    server.close()
    client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
