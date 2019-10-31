# Running examples

To run existing examples you would need a running redis instance.  
If you don't have it, redis can be installed with your favourite package manager. (it is only available for linux currently)
After installing redis, open terminal and run `redis-server`.

After ensuring that redis is running you will need to open 2 more terminals and run the following commands.

#### Terminal 1
`python3 examples/basic/server.py`

#### Terminal 2
`python3 examples/basic/client.py`

You should now see messages in both terminals.
