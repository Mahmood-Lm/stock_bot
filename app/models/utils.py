import psycopg2
import decimal
from config.credetials import DB_NAME, DB_HOST, DB_PORT, DB_PASSWORD, DB_USERNAME


def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST,
                            port=DB_PORT,
                            database=DB_NAME,
                            user=DB_USERNAME,
                            password=DB_PASSWORD)
    return conn


def dict_fetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(
            zip(
                columns,
                [
                    int(value) if isinstance(value, decimal.Decimal) else value
                    for value in row
                ],
            )
        )
        for row in cursor.fetchall()
    ]
