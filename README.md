# IOMirea-rpc
## Warning: project is in early development stage, expect bugs and frequent breaking changes

IOMirea-rpc is RPC library based on redis pubsub built with [aioredis](https://github.com/aio-libs/aioredis).

[![Build Status](https://travis-ci.org/IOMirea/rpc.svg?branch=master)](https://travis-ci.org/IOMirea/rpc)
[![codecov](https://codecov.io/gh/IOMirea/rpc/branch/master/graph/badge.svg)](https://codecov.io/gh/IOMirea/rpc)

### Installation
Library can be installed with the following command `pip install git+https://github.com/IOMirea/rpc.git#egg=iomirea_rpc`

### Running
There are 3 run modes: `Client`, `Server` and `ClientServer`.

|                    | Client | Server |  ClientServer   |
| :----------------- | :----: | :----: | :-------------: |
| Sending command    |    ✔️   |        | not implemented |
| Receiving commands |        |    ✔️   | not implemented |

##### Client
Sends commands to servers and waites for responses.

##### Server
Waits for commands from clients, runs functions and responds.

##### ClientServer
Combines both client and server. It can send commands to servers and respond to clients at the same time.

Examples of running in each can be found in [examples folder](https://github.com/IOMirea/rpc/blob/master/examples).

## Contributing
Feel free to open an issue or submit a pull request.  

## License
Source code is available under GPL v3.0 license, you can get it [here](https://github.com/IOMirea/rpc/blob/master/LICENSE).
