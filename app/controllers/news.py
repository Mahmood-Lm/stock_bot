from app.models.utils import get_db_connection, dict_fetchall
from datetime import datetime


def get_news(news_id):
    db_conn = get_db_connection()
    cur = db_conn.cursor()
    cur.execute(f"SELECT * FROM news where id={news_id};")
    result = dict_fetchall(cur)
    cur.close()
    db_conn.close()
    if result:
        news = result[0]
        news["tickers"] = news["tickers"].split("_,")
        return result[0]


def create_news(
    news_url,
    image_url,
    title,
    text,
    source_name,
    date,
    topics,
    sentiment,
    tickers,
    importance,
):
    if date is None:
        date = datetime.now()
    if importance not in ["ordinary", "high"]:
        importance = "ordinary"
    if not tickers:
        print("Please specify the stocks which this news is related to!")
        return
    if not sentiment:
        sentiment = "Neutral"
    tickers_str = "_,".join(tickers)

    db_conn = get_db_connection()
    user_insert_query = """
            INSERT INTO news (news_url, image_url, title, text, source_name, date, topics, sentiment, tickers, importance)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
            """
    user_data = (news_url, image_url, title, text, source_name, date, topics, sentiment, tickers_str, importance)
    cur = db_conn.cursor()
    cur.execute(user_insert_query, user_data)
    news_id = cur.fetchone()[0]
    db_conn.commit()
    cur.close()
    db_conn.close()
    return news_id


def get_local_stock_news(stock_symbol):
    db_conn = get_db_connection()
    cur = db_conn.cursor()
    cur.execute(f"SELECT * FROM news where tickers ilike '{stock_symbol}_';")
    result = dict_fetchall(cur)
    cur.close()
    db_conn.close()
    for news in result:
        news["tickers"] = news["tickers"].split("_,")
    return result
