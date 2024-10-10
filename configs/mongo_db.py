#!/usr/bin/env python3
from pymongo import MongoClient
import pymongo
from bson import ObjectId


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
        print("Inserting data")
        for value in data:
            record = collection.find_one({'license_nbr': value['license_nbr']})
            if not record:
                collection.insert_one(value)
        return True
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")
        return False


def create_index(client: MongoClient, db_name: str, collection_name: str, column_name: str):
    database = client[db_name]
    collection_name = database[collection_name]
    indexes = collection_name.index_information()

    if f"{column_name}_1" in indexes:
        print(f"Index on '{column_name}' already exists.")
    else:
        # Create a unique index on the specified column
        collection_name.create_index([(column_name, pymongo.ASCENDING)], unique=True)
        print(f"Unique index created on '{column_name}'")
    # check if index created
    print(collection_name.list_indexes())


def fetch_all_data(client: MongoClient, db_name: str, collection_name: str):
    database = client[db_name]
    collection_name = database[collection_name]

    data = collection_name.find({})
    return (data)


def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format."""
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, (dict, list)):
                doc[key] = serialize_doc(value)
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    return doc
