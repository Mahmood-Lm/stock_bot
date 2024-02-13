from urllib.request import urlopen
import urllib.parse
import json
from config.credetials import FMP_KEY
import certifi
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd


def get_stock_info(symbol: str):
    """
    Retrieves information of a stock based on its symbol.
    Parameters
    ----------
    symbol : string containing stock symbol
    Returns
    -------
    a pandas data frame
    """
    stock = yf.Ticker(symbol)
    print("stock: ", stock)
    info = stock.info
    print("info: ", info)
    return info


def get_stocks_info(symbols):
    print("Oomad toosh, symbols:", symbols)
    # for symbol in symbols:
    #     overall_sentiment, latest_recommendations = get_stock_recommendations(symbol)
    tickers = yf.Tickers(str(symbols))
    text = ""
    for stock in tickers.tickers.values():
        if text != "":
            text += "\n"
        text += (
            str(stock.info.get("shortName"))
            + ": "
            + str(stock.info.get("currentPrice"))
            + "$"
        )
    print("Text:", text)
    return text


def get_stock_history(symbol, period, interval):
    stock = yf.Ticker(symbol.upper())
    history = stock.history(period, interval)
    return history


def get_stock_news(symbol):
    stock = yf.Ticker(symbol.upper())
    news = stock.news
    return news


def get_related_companies(sector, industry):
    url = "https://financialmodelingprep.com/api/v3/stock-screener?sector={}&industry={}&limit=6&apikey={}".format(
        urllib.parse.quote(sector), urllib.parse.quote(industry), FMP_KEY
    )
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)


sentiment_points = {
    "sector outperform": 1,
    "hold": 1,
    "market perform": 0,
    "strong buy": 3,
    "long-term buy": 1,
    "sell": -3,
    "market outperform": 0,
    "positive": 1,
    "equal-weight": 0,
    "perform": 0,
    "negative": -1,
    "reduce": -2,
    "underweight": -1,
    "underperform": -1,
    "sector weight": 0,
    "peer perform": -1,
    "buy": 2,
}


def get_stock_recommendations(symbol):
    stock = yf.Ticker(symbol)
    recommendations = stock.recommendations

    period = 30
    start_of_period = datetime.now() - timedelta(days=period)

    period_condition = recommendations.index.to_series().between(start_of_period, datetime.now())

    latest_recommendations = recommendations[period_condition].to_dict("records")

    overall_sentiment_point = 0
    for recommendation in latest_recommendations:
        sentiment = recommendation.get("To Grade")
        overall_sentiment_point += sentiment_points.get(sentiment.lower(), 0)

    if overall_sentiment_point > 1:
        overall_sentiment = "buy"
    elif 0 <= overall_sentiment_point <= 1:
        overall_sentiment = "neutral"
    else:
        overall_sentiment = "sell"

    return overall_sentiment, latest_recommendations
