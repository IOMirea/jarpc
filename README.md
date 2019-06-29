# IOMirea-rpc
## Warning: project is in early development stage, expect bugs and frequent breaking changes

IOMirea-rpc is RPC library based on redis channels built with [aioredis](https://github.com/aio-libs/aioredis) 
developed for IOMirea messenger internal use.

### Installation

Library can be installed with the following command `pip install git+https://github.com/IOMirea/rpc.git#egg=iomirea_rpc`

### Running

There are 2 supported modes: server and client.  
Client can send commands and process responses, server listens for commands and executes them, sending responses.  
There is no limit for clients/servers, you can run several instances in parallel without problems.

Examples of both server and client can be found in examples folder.

## Contributing
Feel free to open an issue or submit a pull request.  
Note: [pre-commit](https://pre-commit.com) checks should be satisfied before submitting code.

## License
Source code is available under GPL v3.0 license, you can get it [here](https://github.com/IOMirea/rpc/blob/master/LICENSE).
