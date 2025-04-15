import logging
from xkcd_scripts.database import connect_to_db, create_table
from xkcd_scripts.logging_config import setup_logging

setup_logging()

def create_table_if_not_exists():
    conn = connect_to_db()
    if conn:
        try:
            create_table()  
            logging.info("Checked/created the table.")
        finally:
            conn.close()
    else:
        logging.error("Could not connect to DB to ensure table exists.")
        raise ConnectionError("DB connection failed")

