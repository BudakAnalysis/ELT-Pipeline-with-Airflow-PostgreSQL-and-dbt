from datetime import datetime, timedelta
from airflow import DAG
from docker.types import Mount
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
import subprocess
import logging
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def run_elt_script():
    """Run ELT script with better error handling and logging"""
    script_path = "/opt/airflow/elt/elt_script.py"
    
    logging.info(f"Starting ELT script: {script_path}")
    
    try:
        import os
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"ELT script not found at {script_path}")
        
        result = subprocess.run(
            ["python", script_path],
            capture_output=True, 
            text=True,
            timeout=300  
        )
        
        logging.info(f"Script stdout: {result.stdout}")
        if result.stderr:
            logging.warning(f"Script stderr: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"Script failed with return code {result.returncode}. Error: {result.stderr}")
        else:
            logging.info("ELT script completed successfully")
            print(result.stdout)
            return result.stdout
            
    except subprocess.TimeoutExpired:
        raise Exception("ELT script timed out after 5 minutes")
    except Exception as e:
        logging.error(f"ELT script failed: {str(e)}")
        raise

dag = DAG(
    'elt_and_dbt',
    default_args=default_args,
    description="An ELT workflow with dbt",
    start_date=datetime(2025, 7, 20),
    schedule_interval=None,  
    catchup=False,
    max_active_runs=1,
)

t1 = PythonOperator(
    task_id="run_elt_script",
    python_callable=run_elt_script,
    dag=dag
)

host_project_path = os.environ.get('HOST_PROJECT_PATH', '/tmp')
dbt_project_path = os.path.join(host_project_path, 'custom_postgres')


dbt_profiles_path = r'C:\Users\natur\.dbt'

t2 = DockerOperator(
    task_id="dbt_run",
    image='python:3.9-slim',
    command=[
        "bash", "-c", 
        """
        # Install dbt-postgres and git (required by dbt)
        apt-get update && apt-get install -y git &&
        pip install dbt-postgres==1.4.7 &&
        echo '=== Starting dbt transformations ===' &&
        cd /dbt &&
        dbt run --profiles-dir /home/airflow/.dbt &&
        echo '=== dbt transformations completed successfully ==='
        """
    ],
    auto_remove=False,  
    docker_url="unix://var/run/docker.sock",
    network_mode="elt_elt_network",  
    mounts=[
        Mount(source=dbt_project_path, target='/dbt', type='bind'),
        Mount(source=dbt_profiles_path, target='/home/airflow/.dbt', type='bind')
    ],
    environment={
        'DBT_PROFILES_DIR': '/home/airflow/.dbt'
    },
    mount_tmp_dir=False,
    dag=dag
)

t1 >> t2