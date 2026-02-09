import datetime as dt
from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator


default_args = {
    'owner': 'dhias renaldy',
    'start_date': dt.datetime(2024, 1, 1),
    'retries': 0,
    'retry_delay': dt.timedelta(minutes=600),
}


with DAG('Final_transaction',
         default_args=default_args,
         schedule_interval='10-30/10 9 * * 6',
         catchup=False,
         ) as dag:

    python_extract = BashOperator(task_id='python_extract', bash_command='python /opt/airflow/scripts/1_project_extract.py')
    python_transform = BashOperator(task_id='python_transform', bash_command='python /opt/airflow/scripts/2_project_transform.py')
    python_validate = BashOperator(task_id='python_validate', bash_command='python /opt/airflow/scripts/3_project_validate.py')
    python_load = BashOperator(task_id='python_load', bash_command='python /opt/airflow/scripts/4_project_load.py')

python_extract >> python_transform >> python_validate >> python_load

