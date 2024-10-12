#!/usr/bin/env python3

import sys
import os
import logging
from bson import ObjectId

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from flask import Flask, jsonify, request, render_template
from configs import mongo_db
from flask_cors import CORS
from pymongo import MongoClient

# Set up logging
logging.basicConfig(level=logging.DEBUG)

MONGO_CLIENT = MongoClient('mongodb://localhost:27017')  # Synchronous MongoClient
app = Flask(__name__)
CORS(app)

db = MONGO_CLIENT['Business_lsc']
collection = db['licenses']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        limit = int(request.args.get('limit', 50))  # Items per page
        page = int(request.args.get('page', 1))  # Current page number

        if page < 1:
            return jsonify({"error": "Invalid page number"}), 400

        skip = (page - 1) * limit  # Calculate how many documents to skip

        query = {}  # You can add any filters here if necessary
        cursor = collection.find(query).skip(skip).limit(limit)

        documents = list(cursor)
        total_docs = collection.count_documents(query)
        total_pages = (total_docs + limit - 1) // limit  # Total pages calculation

        result = {
            'data': [mongo_db.serialize_doc(doc) for doc in documents],
            'total_pages': total_pages,
            'current_page': page
        }

        app.logger.info(f"Fetched {len(documents)} documents for page {page}")
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching data: {str(e)}")
        return jsonify({"error": "An error occurred while fetching data"}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
