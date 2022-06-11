from app.models.utils import get_db_connection, dict_fetchall
import json


def get_chat(chat_id):
    db_conn = get_db_connection()
    cur = db_conn.cursor()
    cur.execute(f"SELECT * FROM chat where chat_id='{chat_id}';")
    result = dict_fetchall(cur)
    cur.close()
    db_conn.close()
    if result:
        return result[0]


def create_chat(chat_id):
    db_conn = get_db_connection()
    user_insert_query = """
            INSERT INTO chat (chat_id, active_hours_start, active_hours_end, news_teller_time, watchlist, timezone)
            VALUES (%s,%s,%s,%s,%s,%s) RETURNING chat_id
            """
    user_data = (chat_id, None, None, None, "", "")
    cur = db_conn.cursor()
    cur.execute(user_insert_query, user_data)
    chat_id = cur.fetchone()[0]
    db_conn.commit()
    # close communication with the database
    cur.close()
    db_conn.close()
    return chat_id


def update_chat(chat_id, **kwargs):
    update_str = ""
    for key, value in kwargs.items():
        if update_str != "":
            update_str += ", "
        if value is None:
            update_str += f"{key}=NULL"
        else:
            update_str += f"{key}='{value}'"
    db_conn = get_db_connection()
    update_watchlist_query = f"""
                        UPDATE chat SET {update_str}
                        WHERE chat_id = '{chat_id}' RETURNING chat_id
                        """
    # create a new cursor
    cur = db_conn.cursor()
    cur.execute(update_watchlist_query)
    chat_id = cur.fetchone()[0]
    db_conn.commit()
    cur.close()
    db_conn.close()
    return chat_id


def update_chat_settings(
    chat_id,
    active_hours_start="no-change",
    active_hours_end="no-change",
    news_teller_time="no-change",
    timezone="no-change",
):
    kwargs = {}
    if active_hours_start != "no-change":
        kwargs["active_hours_start"] = active_hours_start
    if active_hours_end != "no-change":
        kwargs["active_hours_end"] = active_hours_end
    if news_teller_time != "no-change":
        kwargs["news_teller_time"] = news_teller_time
    if timezone != "no-change":
        kwargs["timezone"] = timezone
    return update_chat(chat_id, **kwargs)


def get_chat_watchlist(chat_id):
    db_conn = get_db_connection()
    cur = db_conn.cursor()
    cur.execute(f"SELECT watchlist FROM chat where chat_id='{chat_id}';")
    result = dict_fetchall(cur)
    cur.close()
    db_conn.close()
    if result:
        watchlist_str = result[0]["watchlist"]
        if watchlist_str == "":
            watchlist = []
        else:
            watchlist = watchlist_str.split(",")
        return watchlist


def add_stock_to_watchlist(chat_id, stock_symbol):
    watchlist = get_chat_watchlist(chat_id)
    if stock_symbol not in watchlist:
        watchlist.append(stock_symbol)
    watchlist_str = ",".join(filter(None, watchlist))
    return update_chat(chat_id, watchlist=watchlist_str)


def remove_stock_from_watchlist(chat_id, stock_symbol):
    watchlist = get_chat_watchlist(chat_id)
    if stock_symbol in watchlist:
        watchlist.remove(stock_symbol)
    watchlist_str = ",".join(filter(None, watchlist))
    return update_chat(chat_id, watchlist=watchlist_str)


def clear_watchlist(chat_id):
    return update_chat(chat_id, watchlist="")
