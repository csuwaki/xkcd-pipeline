import os
import logging
import psycopg2
from xkcd_scripts.logging_config import setup_logging

setup_logging()

def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "xkcd"),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "admin"),
            host=os.getenv("DB_HOST", "postgres_db"),  
            port=os.getenv("DB_PORT", "5432"), 
        )
        logging.info("Successfully connected to the database.")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        return None

def create_table():
    try:
        conn = connect_to_db()
        if conn is None:
            print("Could not connect.")

        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS public.raw_comics (
            month INTEGER,
            num INTEGER PRIMARY KEY,
            link VARCHAR(1000),
            year INTEGER,
            news VARCHAR(1000),
            safe_title VARCHAR(1000),
            transcript TEXT,
            alt TEXT,
            img VARCHAR(1000),
            title VARCHAR(1000),
            day INTEGER
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        logging.info("Table created successfully.")
    except Exception as e:
        logging.error(f"Error creating the table: {e}")
    finally:
        cursor.close()
        conn.close()

def insert_comic_to_db(conn, comic):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO raw_comics (
                    num, month, link, year, news, safe_title,
                    transcript, alt, img, title, day
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (num) DO NOTHING;
            """, (
                comic["num"],
                comic.get("month", ""),
                comic.get("link", ""),
                comic.get("year", ""),
                comic.get("news", ""),
                comic.get("safe_title", ""),
                comic.get("transcript", ""),
                comic.get("alt", ""),
                comic.get("img", ""),
                comic.get("title", ""),
                comic.get("day", ""),
            ))
            conn.commit()
            logging.info(f"Comic {comic['num']} inserted successfully.")
    except Exception as e:
        logging.error(f"Error inserting comic {comic['num']}: {e}")