# Distributed Data Pipeline and Analytics System
## Introduction
This project is a distributed data pipeline and analytics system that is designed to process 
and analyze large amounts of data. The system is built using Apache Kafka, Apache Spark, and Apache Cassandra. 
The system is designed to be scalable and fault-tolerant, and can be used to process data from a variety of sources.
### Data ingestion
The system is designed to ingest data from a variety of sources, including files, databases, and APIs.
We will be using NYC business license data as an example dataset for this project.
file: [nyc_async.py](configs/nyc_async.py)
#### File details nyc_async.py
```python
async def fetch_data(session: aiohttp.ClientSession, url: str, ) -> str:
    """ Fetch Data From URL """
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"Error fetching data from {url}: {e}")
        return []


async def get_total_count(session: aiohttp.ClientSession) -> int:
    """ Get Total Count of Records """
    url = f"{BASE_URL}?$select=count(*)"

    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return int(data[0]['count'])
    except (aiohttp.ClientError, KeyError, IndexError, ValueError) as e:
        print(f"Error fetching data from {url}: {e}")
        return MAX_ITEMS


async def fetch_data_from_api():

    async with aiohttp.ClientSession() as session:
        total_count = min(await get_total_count(session), MAX_ITEMS)
        urls = [f"{BASE_URL}?$limit={ROWS_PER_REQUEST}&$offset={offset}" for offset in
                range(0, total_count, ROWS_PER_REQUEST)]

        tasks = [fetch_data(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)

        all_data = [item for sublist in responses for item in json.loads(sublist)]

        # print length of dataset
        print(f"Total records retrieved {sum([len(response) for response in responses])}")

        if all_data:
            print(len(all_data))

        return all_data
```

The following functions were used to handle the fetching of data from the NYC Open Data API.
utilizing the aiohttp library to make asynchronous requests to the API.
This made it possible to fetch data from the API in parallel, which helped to speed up the data ingestion process.
```python
import asyncio
```
### Caching and temporary Storage
The system uses Redis as a caching layer to store temporary data.
file: [redis_server.py](configs/redis_server.py)
```python
async def start_redis(local_host: str, port: int, dbms: int) -> aioredis.Redis:
    """ Start Redis Server """
    try:
        r = await aioredis.from_url(f"redis://{local_host}:{port}/{dbms}")
        return r
    except aioredis.RedisError as e:
        print(f"Error connecting to Redis Server: {e}")
        return None


async def fetch_data(redis_server: aioredis.Redis, key: str) -> dict:
    """ Fetch Data from Redis """
    all_data = {}
    cursor = '0'

    try:
        while cursor != 0:
            cursor, keys = await redis_server.scan(cursor, count = 1000)


            keys = [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]

            values = await asyncio.gather(*[redis_server.get(key) for key in keys])

            for key, value in zip(keys, values):
                all_data[key] = json.loads(value) if value else None

        return all_data

    except aioredis.exceptions.ConnectionError as e:
        print(f"Error fetching data from Redis Server: {e}")
        return None

async def get_or_cache_data(redis_server: aioredis.Redis):
    cached_data_key = 'api_cached_key'
    cached = await redis_server.get(cached_data_key)
    # checked if there is data cached
    if cached:
        print("Fetching data from cache......")
        data = json.loads(cached)
        if not data:
            print("Cached data empty")
            await redis_server.delete(cached_data_key)
        else:
            return data


    data = await nyc_async.run_async()
    pipeline = redis_server.pipeline()

    for index, value in enumerate(data):
        key = f"{value['license_nbr']}"
        pipeline.set(key, json.dumps(value))

    await pipeline.execute()

    await redis_server.set(cached_data_key, json.dumps(data), ex=3600)

    return data
```
Some of the functionality of this code was to:
- Fetch data and save it to the redis server
- Transfer data from the redis server into a proper format for mongodb
- cache the data for a period of time

