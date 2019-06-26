import asyncio

from iomirea_rpc import Server


REDIS_HOST = "localhost"
REDIS_PORT = 6379


async def ping(srv: Server, address: str, message: str = "") -> None:
    response = "pong" if message == "" else message

    await srv.respond(address, response)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    server = Server("example", loop=loop, node="examole_node")
    server.register_command(0, ping)

    loop.create_task(server.run((REDIS_HOST, REDIS_PORT)))
    loop.run_forever()
