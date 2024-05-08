## Unlimited Python Async Operations

This method is inspired by the article [Making an Unlimited Number of Requests with Python aiohttp + pypeln](https://medium.com/@cgarciae/making-an-infinite-number-of-requests-with-python-aiohttp-pypeln-3a552b97dc95).

Unlimited async operation with Python, e.g., performing an unlimited number of HTTP requests.

- [Overview](#overview)
- [Enhanced Method](#enhanced-method)
- [Results](#results)
- [Setup](#setup)

# Overview

### Original Method [Cristian Garcia](https://medium.com/@cgarciae/making-an-infinite-number-of-requests-with-python-aiohttp-pypeln-3a552b97dc95):

```python
from aiohttp import ClientSession, TCPConnector
import asyncio
import sys
import pypeln as pl


limit = 1000
urls = ("http://007-server-1:8080/{}".format(i) for i in range(int(sys.argv[1])))


async def main():
    async with ClientSession(connector=TCPConnector(limit=0)) as session:

        async def fetch(url):
            async with session.get(url) as response:
                print(url)
                return await response.read()

        await pl.task.each(
            fetch,
            urls,
            workers=limit,
        )


asyncio.run(main())

```

- Method in `client/bench.py` file
- This using `pypeln` for parallelizing and pipelining data processing tasks
- `limit=1000` : maximum number of concurrent HTTP requests allowed, so if you increase the `limit` the Memory and CPU usage will increase to.

### Enhanced Method:

```python
from aiohttp import ClientSession, TCPConnector
import asyncio
import sys

limit = 1000
sem = asyncio.Semaphore(limit)

async def fetch(url, session):
    async with sem:
        async with session.get(url) as response:
            print(url)
            return await response.read()

async def main():
    urls = [f"http://007-server-1:8080/{i}" for i in range(int(sys.argv[1]))]
    async with ClientSession(connector=TCPConnector(limit=0)) as session:
        tasks = [fetch(url, session) for url in urls]
        await asyncio.gather(*tasks)

asyncio.run(main())

```

- Method in `client/bench_v2.py` file.
- It use `asyncio.Semaphore` to limit the number of concurrent tasks, thereby reducing Memory usage by approximately 50%.

# Results

#### System Information

- **OS**: Ubuntu 22.04.4 LTS, jammy
- 8GB Memory, CPU Intel(R) i3-10100F 3.60GHz - 8 Cors, 4 Core ber socket
- **Docker version**: 26.1.0, build 9714adc

Version 2 that use `asyncio.Semaphore` in `client/bench_v2.py`, is better then origin [Cristian Garcia](https://medium.com/@cgarciae/making-an-infinite-number-of-requests-with-python-aiohttp-pypeln-3a552b97dc95) method in `client/bench.py` file , just in memory usage, he lees then it almost by `50%`, but other thing like the time he takes and the CUP usage they almost same.

This chart explain some results for `bench.py` VS `bench_v2`, in Memory usage by diffracts request count:

# Setup

Each service is separated in different container, `client` and `server`, you can use the server container if you wanted a tests local, or you can just run the `client`.

- **Server service**: in `./server` it contain `./server/server.py` which functions as a simple `HTTP` server using [aiohttp](https://docs.aiohttp.org/en/stable/), we create a http://localhost:8080/{name} route, he simply have a delay with a random time between `1-3` second and return a response with the name you pass.

- **Client service**: in `./client`, includes the original method(`./client/bench.py`) by [Cristian Garcia](https://medium.com/@cgarciae/making-an-infinite-number-of-requests-with-python-aiohttp-pypeln-3a552b97dc95), and the enhanced version (`./client/bench_v2.py`) with `asyncio.Semaphore`, we use `timed.sh` script to calc the python app time taken and also the CPU and Memory usage, `./client/benchmark_log.txt` this is a log file

### Setting Up Local Server & Client

We use `docker compose` to handle it:

```shell
# first you need to go in the project directory and simple run:
docker compose up

# to run in background or detach mode add '-d' flag:
docker compose up -d
```

This command starts both server and client services. The server runs on http://localhost:8080 on your system.

The client service does not execute any services but keeps the container alive by running `tail -f /dev/null`. Alternatively, you can modify the `./client/Dockerfile` to execute the Python script or benchmark test.

### Setting Up Just the Client

- Build the image:

  ```shell
  docker build -t py-bench ./client
  # ./client is the directory containing the Dockerfile
  ```

- Run the container:

  ```shell
  docker run -d py-bench
  ```

### Development Client

For development, utilize the VSCode Dev Container. Run the container, then use "Attach to Running Container" in VSCode for a seamless development environment. Any changes made will be applied automatically.

To execute commands inside the container, open a shell in VSCode or use the following in your terminal:

```shell
docker ps
# List all running containers and note the client name.

docker exec -it <container name> sh
# Replace <container name> with the actual container name.
# Use a specific command instead of 'sh' for just running a command in the container and close the shell
```

### Running Tests

Use `./client/timed.sh` to measure the Python app's runtime, CPU, and Memory usage. For example:

```shell
./timed.sh python bench.py 10000
```

Results will be printed in ./client/benchmark_log.txt and displayed in the terminal.
