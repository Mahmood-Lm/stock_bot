import path
import sys
import psycopg2
# directory reach
directory = path.Path(__file__).abspath()

# setting path
sys.path.append(directory.parent.parent.parent)
from app.models.utils import get_db_connection

conn = get_db_connection()

# Open a cursor to perform database operations
cur = conn.cursor()


create_chat_table = """
    CREATE TABLE chat (
    chat_id VARCHAR(20) PRIMARY KEY,
    active_hours_start TIME,
    active_hours_end TIME,
    news_teller_time TIME,
    watchlist TEXT NOT NULL,
    timezone TEXT NOT NULL
    );
"""

create_news_table = """
    CREATE TABLE news (
    id serial PRIMARY KEY,
    news_url TEXT,
    image_url TEXT,
    title TEXT,
    text TEXT,
    source_name TEXT,
    date TIMESTAMP,
    topics TEXT,
    sentiment TEXT,
    tickers TEXT,
    importance TEXT
    );
"""

create_chat_news_table = """
    CREATE TABLE chat_news (
    id INT GENERATED ALWAYS AS IDENTITY,
    chat_id varchar(20) NOT NULL,
    news_id INT NOT NULL,
    acknowledged BOOLEAN NOT NULL DEFAULT 't',
    CONSTRAINT fk_chat
        FOREIGN KEY(chat_id) 
            REFERENCES chat(chat_id)
            ON DELETE CASCADE,
    CONSTRAINT fk_news
        FOREIGN KEY(news_id) 
            REFERENCES news(id)
            ON DELETE CASCADE
    );
"""


"""
a news example:
    "news_url": "https://www.reuters.com/business/autos-transportation/teslas-china-output-decline-trending-deeper-than-musk-forecast-data-internal-2022-06-09/",
    "image_url": "https://cdn.snapi.dev/images/v1/i/3/m02d20220609t2i1601422127w940fhfwllplsqrlynxmpei580cb-1409396.jpg",
    "title": "Tesla's China output decline trending deeper than Musk forecast, data and internal memos show",
    "text": "Production at Tesla Inc's Shanghai factory is on track to fall by over a third this quarter from the first three months of the year as China's zero-COVID lockdowns caused deeper disruptions to output than Elon Musk had predicted.",
    "source_name": "Reuters",
    "date": "Thu, 09 Jun 2022 05:14:00 -0400",
    "topics": [
        "CEO"
    ],
    "sentiment": "Neutral",
    "type": "Article",
    "tickers": [
        "TSLA"
    ]
    "importance": "high"
"""


def initialize():
    try:
        # Execute a command: this creates a new table
        cur.execute('DROP TABLE IF EXISTS chat CASCADE;')
        cur.execute(create_chat_table)
        cur.execute('DROP TABLE IF EXISTS news CASCADE;')
        cur.execute(create_news_table)
        cur.execute(create_chat_news_table)
        conn.commit()
        print("Database Initialized")

    except (Exception, psycopg2.Error) as error:
        print("Failed to create chat table", error)

    finally:
        # closing database connection.
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")
