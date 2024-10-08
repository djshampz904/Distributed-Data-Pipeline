#!/usr/bin/env python3
from pymongo import MongoClient


def start_mongo(local_host: str, port: int) -> MongoClient:
    """ Start MongoDB Server """
    try:
        client = MongoClient(local_host, port)
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB Server: {e}")
        return None

def insert_data(client: MongoClient, db_name: str, collection_name: str, data: dict) -> bool:
    """ Insert Data into MongoDB """
    try:
        db = client[db_name]
        collection = db[collection_name]
        collection.insert_many(data)
        return True
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")
        return False

