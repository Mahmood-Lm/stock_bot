import psycopg2
from app.models.utils import get_db_connection

conn = get_db_connection()

# Open a cursor to perform database operations
cur = conn.cursor()


create_user_table = """
    CREATE TABLE stock_bot_user (
    id serial PRIMARY KEY,
    chat_id integer NOT NULL UNIQUE,
    active_hours_start TIME,
    active_hours_end TIME,
    news_teller_time TIME
    );
"""


create_user_company_table = """
    CREATE TABLE stock_bot_user_stock (
    id INT GENERATED ALWAYS AS IDENTITY,
    chat_id INT not null,
    stock_symbol VARCHAR(100) NOT NULL,
    PRIMARY KEY(id),
    CONSTRAINT fk_user
        FOREIGN KEY(chat_id) 
            REFERENCES stock_bot_user(chat_id)
            ON DELETE CASCADE
    --- CONSTRAINT fk_company
    ---     FOREIGN KEY(company_symbol) 
    ---         REFERENCES stock_bot_company(symbol)
    ---         ON DELETE CASCADE
    );
"""


try:
    # Execute a command: this creates a new table
    cur.execute('DROP TABLE IF EXISTS stock_bot_user CASCADE;')
    cur.execute(create_user_table)
    cur.execute('DROP TABLE IF EXISTS stock_bot_user_stock CASCADE;')
    cur.execute(create_user_company_table)
    conn.commit()

except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into mobile table", error)

finally:
    # closing database connection.
    if conn:
        cur.close()
        conn.close()
        print("PostgreSQL connection is closed")
