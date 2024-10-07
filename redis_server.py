#!/usr/bin/env python3

import redis
import json


def start_redis(local_host: str, port: int, dbms: str) -> redis.Redis:
    """ Start Redis Server """
    try:
        r = redis.Redis(host=local_host, port=port, db=dbms)
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis Server: {e}")
        return None
