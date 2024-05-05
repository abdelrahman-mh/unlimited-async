## Unlimited Python Async Operations

This method is inspired by the article [Making an Unlimited Number of Requests with Python aiohttp + pypeln](https://medium.com/@cgarciae/making-an-infinite-number-of-requests-with-python-aiohttp-pypeln-3a552b97dc95).

Unlimited async operation with Python, e.g., performing an unlimited number of HTTP requests.

- [Overview](#overview)
- [Some Results](#some-results)
- [Setup](#setup)

# Overview

### This method from [Cristian Garcia](https://medium.com/@cgarciae/making-an-infinite-number-of-requests-with-python-aiohttp-pypeln-3a552b97dc95):

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

### This have some enhancement then the prev one:

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

- This method is **better** from prev one, it use less Memory by `50%`, for more details ses the next header.
- Method in `client/bench_v2.py` file.
- This using `asyncio.Semaphore` using for limiting the number of concurrent tasks, and used to control access to a shared resource or a pool of resources

# Some Results

#### System Information

- **OS**: Ubuntu 22.04.4 LTS, jammy
- 8GB Memory, CPU Intel(R) i3-10100F 3.60GHz - 8 Cors, 4 Core ber socket
- **Docker version**: 26.1.0, build 9714adc

Version 2 that use `asyncio.Semaphore` in `client/bench_v2.py`, is better then origin [Cristian Garcia](https://medium.com/@cgarciae/making-an-infinite-number-of-requests-with-python-aiohttp-pypeln-3a552b97dc95) method in `client/bench.py` file , just in memory usage, he lees then it almost by `50%`, but other thing like the time he takes and the CUP usage they almost same.

This chart explain some results for  `bench.py` VS `bench_v2`, in Memory usage by diffracts request count:

# Setup
