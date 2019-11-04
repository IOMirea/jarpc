# jarpc

## Warning: project is in early development stage, expect bugs and frequent breaking changes

jarpc - Just another python RPC library based on redis pubsub. It is built with [aioredis](https://github.com/aio-libs/aioredis).

<img src="https://raw.github.com/IOMirea/jarpc/master/docs/logo.svg?sanitize=true" height="100">

[![Documentation Status](https://readthedocs.org/projects/jarpc/badge/?version=latest)](https://jarpc.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/IOMirea/jarpc.svg?branch=master)](https://travis-ci.org/IOMirea/jarpc)
[![codecov](https://codecov.io/gh/IOMirea/jarpc/branch/master/graph/badge.svg)](https://codecov.io/gh/IOMirea/jarpc)

### Features
- `Client`, `Server` and `Slient` connection modes.

|                    | Client | Server | Slient |
| :----------------- | :----: | :----: | :----: |
| Calling commands   |   yes  |   no   |   yes  |
| Receiving commands |   no   |   yes  |   yes  |

- asyncronous response processing (AsyncIterator).
- encoding customization (marshal (default), json, msgpack, pickle, ...).

### Installation
Library can be installed from repository: `pip install git+https://github.com/IOMirea/jarpc.git#egg=jarpc` (PyPI release soon)

### Examples

#### Client
```python
import asyncio

from jarpc import Client

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0
COMMAND_SLOW_PING = 1
COMMAND_FIX_BUGS = 42


async def main() -> None:
    client = Client("example", default_timeout=5, default_expect_responses=1)


    asyncio.create_task(client.start((REDIS_HOST, REDIS_PORT)))

    await client.wait_until_ready()

    ping_data = {"message": input("Enter message to send or leave blank: ")}

    print("PING      ->", await client.call(COMMAND_PING, ping_data))
    print("SLOW_PING ->", await client.call(COMMAND_SLOW_PING, timeout=1))
    print("FIX_BUGS  ->", await client.call(COMMAND_FIX_BUGS))

    # exit
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
```


#### Server
```python
import os
import asyncio

from jarpc import Server, Request

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0
COMMAND_SLOW_PING = 1

server = Server("example", node=f"example-{os.getpid()}")


@server.command(COMMAND_PING)
async def ping(req: Request, message: str = "") -> str:
    """Responds with provided message argument or 'pong'."""

    print("Received PING command")

    return "pong" if message == "" else message


@server.command(COMMAND_SLOW_PING)
async def slow_ping(req: Request) -> str:
    """Responds with 'pong' after 2 seconds, too slow..."""

    print("Received SLOW_PING command")

    await asyncio.sleep(2)

    return "pong"


if __name__ == "__main__":
    server.run((REDIS_HOST, REDIS_PORT))
```

#### Slient
```python
import os
import asyncio

from jarpc import Slient, Request

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMAND_PING = 0

loop = asyncio.get_event_loop()

slient = Slient(
    "example",
    loop=loop,
    node=f"example-{os.getpid()}",
    default_timeout=5,
    default_expect_responses=1,
)


@slient.command(COMMAND_PING)
async def ping(req: Request, message: str = "") -> str:
    """Responds with provided message argument or 'pong'."""

    print("Received PING command")

    return "pong" if message == "" else message


async def call_ping(slient: Slient) -> None:
    await slient.wait_until_ready()

    print("PING ->", await slient.call(COMMAND_PING))


if __name__ == "__main__":
    loop.create_task(slient.start((REDIS_HOST, REDIS_PORT)))
    loop.create_task(call_ping(slient))

    # continue listening for commands
    loop.run_forever()
```

More examples can be found in [examples folder](https://github.com/IOMirea/jarpc/blob/master/examples).

### Dependencies
- Python >= 3.6
- [aioredis](https://github.com/aio-libs/aioredis)

### Documentation
Documentation is available at https://jarpc.readthedocs.io

### Source code
Source code is available on GitHub: https://github.com/IOMirea/jarpc

### Protocol specification
Soon

## Contributing
Feel free to open an issue or submit a pull request.  

## License
Source code is available under GPL v3.0 license, you can see it [here](https://github.com/IOMirea/jarpc/blob/master/LICENSE).
