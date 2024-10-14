from airflow.operators.bash import BashOperator
from airflow import DAG
from datetime import datetime, timedelta
import os

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

# The directory where the DAG file is located
dag_directory = os.path.dirname(os.path.abspath(__file__))

with dag:
    run_main_script = BashOperator(
        task_id='run_main_script',
        bash_command=f'cd {dag_directory} && ./main.py',
    )

    run_main_script