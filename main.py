#!/usr/bin/env python3
from configs import mongo_db, nyc_async as nyc, redis_server
import asyncio

""" Main Module """


async def main():
    """ Fetch Data from NYC Open Data"""
    all_data = await redis_server.start_redis_fetch_data()

    # Connect to MongoDB
    mongo_client = mongo_db.start_mongo('localhost', 27017)

    mongo_db.create_index(mongo_client, 'Business_lsc', 'licenses', 'license_nbr')
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
