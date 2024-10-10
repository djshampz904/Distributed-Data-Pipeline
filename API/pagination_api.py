#!/usr/bin/env python3

import sys
import os
import asyncio
from bson import ObjectId
import requests

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from flask import Flask, jsonify, request, render_template
from configs import mongo_db
from flask_cors import CORS
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_CLIENT = AsyncIOMotorClient('mongodb://localhost:27017')
app = Flask(__name__)
CORS(app)

db = MONGO_CLIENT['Business_lsc']
collection = db['licenses']


@app.route('/data')
async def get_data():
    limit = int(request.args.get('limit', 10))
    cursor = request.args.get('cursor')

    query = {}
    if cursor:
        query['id'] = {'$gt': ObjectId(cursor)}

    cursor = collection.find(query).limit(limit + 1)
    documents = await cursor.to_list(length=limit + 1)

    has_next = len(documents) > limit
    documents = documents[:limit]

    result = {
        'data': [mongo_db.serialize_doc(doc) for doc in documents],
        'has_next': has_next
    }
    if has_next:
        result['next_cursor'] = str(documents[-1]['_id'])

    return render_template('index.html', data=result)


def fetch_next_page(cursor=None):
    # Send cursor if provided for pagination
    params = {'limit': 10}
    if cursor:
        params['cursor'] = cursor

    response = requests.get('http://localhost:3000/data', params=params)

    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return {"error": "Failed to fetch data from the API."}

if __name__ == '__main__':
    app.run(port=3000)
