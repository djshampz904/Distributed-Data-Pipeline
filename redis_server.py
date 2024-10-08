#!/usr/bin/env python3

import redis
import json
import aioredis
import asyncio


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


async def main():
    redis_server = await start_redis('localhost', 6379, 0)
    if redis_server:
        all_data = await fetch_data(redis_server, '*')
        print(json.dumps(all_data, indent=2))

