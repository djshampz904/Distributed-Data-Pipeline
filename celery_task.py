from celery import Celery
from pymongo import MongoClient

# Use 'amqp://guest:guest@localhost:5672/' if RabbitMQ is running with default settings
app = Celery('tasks', broker='amqp://guest:guest@localhost:5672/')

client = MongoClient('localhost', 27017)
db = client['Business_lsc']
collection = db['licenses']


@app.task
def process_data(data):
    try:
        collection.update_one(
            {'license_nbr': data['license_nbr']},
            {'$set': data},
            upsert=True
        )
        return f"Processed data for license number: {data['license_nbr']}"
    except Exception as e:
        return f"Error processing data: {str(e)}"


@app.task
def calculate_analytics():
    try:
        total_licenses = collection.count_documents({})
        active_licenses = collection.count_documents({'license_status': 'Active'})

        analytics_result = {
            'total_licenses': total_licenses,
            'active_licenses': active_licenses,
            'inactive_licenses': total_licenses - active_licenses
        }

        db['analytics'].update_one(
            {'_id': 'current_stats'},
            {'$set': analytics_result},
            upsert=True
        )

        return "Analytics calculated and stored"
    except Exception as e:
        return f"Error calculating analytics: {str(e)}"