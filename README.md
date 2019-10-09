# yarpc

## Warning: project is in early development stage, expect bugs and frequent breaking changes

yarpc - Yet another python RPC library based on redis pubsub. It is built with [aioredis](https://github.com/aio-libs/aioredis).

<img src="https://raw.githubusercontent.com/IOMirea/yarpc/master/docs/logo.png" height="100">

[![Documentation Status](https://readthedocs.org/projects/yarpc/badge/?version=latest)](https://yarpc.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/IOMirea/yarpc.svg?branch=master)](https://travis-ci.org/IOMirea/yarpc)
[![codecov](https://codecov.io/gh/IOMirea/yarpc/branch/master/graph/badge.svg)](https://codecov.io/gh/IOMirea/yarpc)

### Installation
Library can be installed from repository: `pip install git+https://github.com/IOMirea/yarpc.git#egg=yarpc` (PyPI release soon)

### Running
There are 3 run modes: `Client`, `Server` and `ClientServer`.

|                    | Client | Server |  ClientServer   |
| :----------------- | :----: | :----: | :-------------: |
| Sending command    |    ✔️   |        | not implemented |
| Receiving commands |        |    ✔️   | not implemented |

##### Client
Sends commands to servers and waits for responses.

##### Server
Waits for commands from clients, responds to them.

##### ClientServer
Combines both client and server. It can send commands to servers as well as respond to clients.

Examples of running in each mode can be found in [examples folder](https://github.com/IOMirea/yarpc/blob/master/examples).

## Contributing
Feel free to open an issue or submit a pull request.  

## License
Source code is available under GPL v3.0 license, you can see it [here](https://github.com/IOMirea/yarpc/blob/master/LICENSE).
