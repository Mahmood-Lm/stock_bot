from app.models.utils import get_db_connection


def get_user(chat_id):
    db_conn = get_db_connection()
    cur = db_conn.cursor()
    cur.execute(f'SELECT * FROM stock_bot_user where chat_id={chat_id};')
    user = cur.fetchall()
    cur.close()
    db_conn.close()
    return user


def create_user(chat_id, active_hours_start, active_hours_end, news_teller_time):
    db_conn = get_db_connection()
    user_insert_query = """
            INSERT INTO stock_bot_user (chat_id, active_hours_start, active_hours_end, news_teller_time)
            VALUES (%s,%s,%s,%s) RETURNING id
            """
    user_data = (chat_id, active_hours_start, active_hours_end, news_teller_time)
    # create a new cursor
    cur = db_conn.cursor()
    # execute the INSERT statement
    cur.execute(user_insert_query, user_data)
    # get the generated id back
    user_id = cur.fetchone()[0]
    # commit the changes to the database
    db_conn.commit()
    # close communication with the database
    cur.close()
    db_conn.close()
    return user_id


def create_user_stock(chat_id, stock_symbol):
    db_conn = get_db_connection()
    user_insert_query = """
                INSERT INTO stock_bot_user_stock (chat_id, stock_symbol)
                VALUES (%s,%s) RETURNING id
                """
    user_data = (chat_id, stock_symbol)
    # create a new cursor
    cur = db_conn.cursor()
    # execute the INSERT statement
    cur.execute(user_insert_query, user_data)
    # get the generated id back
    user_id = cur.fetchone()[0]
    # commit the changes to the database
    db_conn.commit()
    # close communication with the database
    cur.close()
    db_conn.close()
    return user_id


def get_user_stocks(chat_id):
    db_conn = get_db_connection()
    cur = db_conn.cursor()
    cur.execute(f'SELECT stock_symbol FROM stock_bot_user_stock where chat_id={chat_id};')
    stock_symbols = cur.fetchall()
    cur.close()
    db_conn.close()
    return stock_symbols
