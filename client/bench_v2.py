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
