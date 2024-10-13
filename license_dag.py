#!/usr/bin/env python3
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the Python path

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'license_data_pipeline',
    default_args=default_args,
    description='Fetch API data, store in Redis, transfer to MongoDB, and update analytics',
    schedule_interval=timedelta(hours=1),  # Run every hour
)


with dag:
    run_main_script = BashOperator(
        task_id='run_main_script',
        bash_command = './main.py',
    )


    run_main_script
