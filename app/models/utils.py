import psycopg2
from config.credetials import DB_NAME, DB_HOST, DB_PORT, DB_PASSWORD, DB_USERNAME


def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST,
                            port=DB_PORT,
                            database=DB_NAME,
                            user=DB_USERNAME,
                            password=DB_PASSWORD)
    return conn
