import logging
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
from datetime import datetime, timedelta
from xkcd_scripts.logging_config import setup_logging
from xkcd_scripts.extractor import get_last_id, extract_comic_metadata
from xkcd_scripts.database import connect_to_db,  insert_comic_to_db, create_table

setup_logging()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,  
    'email_on_retry': False,  
    'email': ['csuwaki@gmail.com'],
}

with DAG(
    "xkcd_comics",
    description="Fetch and insert XKCD comics into a postgres database",
    schedule='0 0 * * 1,3,5',
    start_date=datetime(2025, 4, 9),
    catchup=False,
    default_args=default_args
) as dag:

    def get_last_comic_from_db(ti):
        conn = connect_to_db()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT MAX(num) FROM raw_comics")
                last_comic_num = cur.fetchone()[0]  
                if last_comic_num is None:
                    last_comic_num = 0 
                    logging.info("No comics in the database. Starting from the first comic.")
                else:
                    logging.info(f"Last comic ID from DB: {last_comic_num}")
                ti.xcom_push(key="last_comic", value=int(last_comic_num))
            conn.close()
        else:
            raise ValueError("Failed to connect to database to fetch last comic ID")
  
    def check_new_comic_available(ti):
        last_comic = ti.xcom_pull(key="last_comic", task_ids="get_last_comic_from_db")
        current_comic = get_last_id()

        if last_comic < current_comic:
            logging.info(f"New comics found: Current={current_comic}, Last={last_comic}")
            ti.xcom_push(key="new_comic", value=current_comic)
            return True
        elif last_comic == 0 and current_comic >0:
            logging.info(f"First load scenario detected: Current={current_comic}, Last={last_comic}")
            ti.xcom_push(key="new_comic", value=current_comic)
            return True
        else:
            logging.info("No new comics available")
            return False
   
    def load_new_comics_to_db(ti):
        last_comic = ti.xcom_pull(key="last_comic", task_ids="get_last_comic_from_db")
        new_comic = ti.xcom_pull(key="new_comic", task_ids="wait_for_new_comic")
        conn = connect_to_db()
        
        if conn:
            for comic_id in range(last_comic + 1, new_comic + 1):
                comic = extract_comic_metadata(comic_id)
                if comic:
                    insert_comic_to_db(conn, comic)
                    logging.info(f"Inserted comic {comic_id} into the database")
            conn.close()
        else:
            raise ValueError("Failed to connect to database to load new comics")
    
    def transform_comics():
        logging.info("Running DBT transformations for comics data...")

    # create_table_task = PythonOperator(
    #     task_id="create_table",
    #     python_callable=create_table_if_not_exists,
    # )

    get_last_comic_task = PythonOperator(
        task_id="get_last_comic_from_db",
        python_callable=get_last_comic_from_db,
    )

    wait_for_new_comic = PythonSensor(
        task_id="wait_for_new_comic",
        python_callable=check_new_comic_available,
        poke_interval=600,  
        mode="reschedule",
    )
    load_new_comics_task = PythonOperator(
        task_id="load_new_comics_to_db",
        python_callable=load_new_comics_to_db,
    )

transform_comics_task = BashOperator(
    task_id="transform_comics",
    bash_command=(
        'export PATH=$PATH:/home/airflow/.local/bin && '
        'cd /opt/airflow/dags/xkcd_dbt && '
        'dbt run -s staging_comics && '
        'dbt run && '
        'dbt test'
    )
)


get_last_comic_task >> wait_for_new_comic >> load_new_comics_task >> transform_comics_task