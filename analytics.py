#!/usr/bin/env python3
from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.json_util import dumps
from celery_task import calculate_analytics, process_data
from celery.exceptions import OperationalError as CeleryOperationalError

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client['Business_lsc']
collection = db['licenses']


@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Business License Analytics API",
        "endpoints": {
            "/api/analytics": "GET - Retrieve analytics",
            "/api/licenses/by-status": "GET - Get licenses grouped by status",
            "/api/licenses/by-category": "GET - Get licenses grouped by category",
            "/api/licenses": "GET - Retrieve all licenses (paginated)"
        }
    })


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        # Calculate analytics directly from the database
        total_licenses = collection.count_documents({})
        active_licenses = collection.count_documents({'license_status': 'Active'})
        inactive_licenses = total_licenses - active_licenses

        analytics = {
            'total_licenses': total_licenses,
            'active_licenses': active_licenses,
            'inactive_licenses': inactive_licenses
        }

        return jsonify(analytics)
    except Exception as e:
        return jsonify({"error": f"Error calculating analytics: {str(e)}"}), 500


@app.route('/api/licenses/by-status', methods=['GET'])
def licenses_by_status():
    try:
        pipeline = [
            {"$group": {"_id": "$license_status", "count": {"$sum": 1}}}
        ]
        result = list(collection.aggregate(pipeline))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Error retrieving licenses by status: {str(e)}"}), 500


@app.route('/api/licenses/by-category', methods=['GET'])
def licenses_by_category():
    try:
        pipeline = [
            {"$group": {"_id": "$business_category", "count": {"$sum": 1}}}
        ]
        result = list(collection.aggregate(pipeline))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Error retrieving licenses by category: {str(e)}"}), 500


# Convert ObjectId to string
def clean_json(data):
    if isinstance(data, list):
        for item in data:
            item['_id'] = str(item['_id'])
    elif isinstance(data, dict):
        if '_id' in data:
            data['_id'] = str(data['_id'])
    return data

@app.route('/api/licenses', methods=['GET'])
def get_licenses():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        skip = (page - 1) * per_page

        licenses = list(collection.find({}).skip(skip).limit(per_page))

        # Clean the ObjectIds to be strings for JSON serialization
        licenses = [clean_json(license) for license in licenses]

        return jsonify(licenses)
    except Exception as e:
        return jsonify({"error": f"Error retrieving licenses: {str(e)}"}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": "The requested URL was not found on the server."}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error", "message": "An unexpected error occurred on the server."}), 500


if __name__ == '__main__':
    app.run(debug=True)