#!/usr/bin/env python3
import nyc_async as nyc
import mongo_db
import redis_server
import asyncio
import json

""" Main Module """


async def main():
    """ Fetch Data from NYC Open Data"""
    all_data = await nyc.run_async()  # This no longer uses asyncio.run() inside nyc_async.py
    redis_client = await redis_server.start_redis('localhost', 6379, 0)

    pipeline = redis_client.pipeline()

    for index, value in enumerate(all_data):
        key = f"{value['license_nbr']}"
        pipeline.set(key, json.dumps(value))

    await pipeline.execute()

    # Connect to MongoDB
    mongo_client = mongo_db.start_mongo('localhost', 27017)

    # Insert data into MongoDB
    mongo_db.insert_data(mongo_client, 'Business_lsc', 'licenses', all_data)


if __name__ == "__main__":
    # Check if an event loop is running and handle accordingly
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # No event loop is running
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Run the main function
    loop.run_until_complete(main())
