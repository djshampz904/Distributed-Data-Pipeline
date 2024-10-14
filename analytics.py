#!/usr/bin/env python3
from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from bson.json_util import dumps
from datetime import datetime, timedelta
from celery_task import calculate_analytics, process_data
from celery.exceptions import OperationalError as CeleryOperationalError
from flask_caching import Cache

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client['Business_lsc']
collection = db['licenses']


@app.route('/')
def home():
    return render_template('dashboard.html')


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        total_licenses = collection.count_documents({})
        active_licenses = collection.count_documents({'license_status': 'Active'})
        expired_licenses = collection.count_documents({'license_status': 'Expired'})
        unique_businesses = collection.distinct('business_unique_id')

        analytics = {
            'total_licenses': total_licenses,
            'active_licenses': active_licenses,
            'expired_licenses': expired_licenses,
            'unique_businesses': len(unique_businesses)
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


@app.route('/api/licenses/by-borough', methods=['GET'])
def licenses_by_borough():
    try:
        pipeline = [
            {"$group": {"_id": "$address_borough", "count": {"$sum": 1}}}
        ]
        result = list(collection.aggregate(pipeline))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Error retrieving licenses by borough: {str(e)}"}), 500


@app.route('/api/licenses/trend', methods=['GET'])
def license_trend():
    try:
        # Get the start date (30 days ago)
        start_date = datetime.now() - timedelta(days=30)

        pipeline = [
            {"$match": {"license_creation_date": {"$gte": start_date}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$license_creation_date"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        result = list(collection.aggregate(pipeline))

        # Convert the result to the format expected by the frontend
        trend_data = [{"date": item["_id"], "count": item["count"]} for item in result]
        return jsonify(trend_data)
    except Exception as e:
        return jsonify({"error": f"Error retrieving license trend: {str(e)}"}), 500


@app.route('/api/licenses/locations', methods=['GET'])
def license_locations():
    try:
        # Limit to 1000 locations to prevent overloading the map
        locations = list(collection.find(
            {"latitude": {"$exists": True}, "longitude": {"$exists": True}},
            {"business_name": 1, "license_nbr": 1, "latitude": 1, "longitude": 1}
        ).limit(1000))

        # Clean the ObjectIds to be strings for JSON serialization
        locations = [clean_json(location) for location in locations]
        return jsonify(locations)
    except Exception as e:
        return jsonify({"error": f"Error retrieving license locations: {str(e)}"}), 500


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