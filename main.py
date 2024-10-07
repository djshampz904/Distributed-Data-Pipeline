#!/usr/bin/env python3

import nyc_async as nyc
import redis_server
import json
""" Main Module """

if __name__ == '__main__':
    """ Fetch Data from NYC Open Data"""
    all_data = nyc.run_async()
    redis_server = redis_server.start_redis('localhost', 6379, 0)

    pipeline = redis_server.pipeline()

    for index, value in enumerate(all_data):
        key = f"{value['license_nbr']}"
        pipeline.set(key, json.dumps(value))

    pipeline.execute()

    # list first 10 records

