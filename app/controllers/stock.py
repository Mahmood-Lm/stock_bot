from urllib.request import urlopen
import urllib.parse
import json
from config.credetials import FMP_KEY
import certifi
import yfinance as yf
import pandas as pd


def get_stock_info(symbol: str) -> pd.DataFrame:
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
    info = stock.info
    return info


def get_stocks_info(symbols):
    stocks_info = [yf.Ticker(symbol).info for symbol in symbols]
    return stocks_info


def get_stock_history(symbol, period):
    stock = yf.Ticker(symbol.upper())
    history = stock.history(period)
    return history


def get_stock_news(symbol):
    stock = yf.Ticker(symbol.upper())
    news = stock.news
    return news


def get_related_companies(sector, industry):
    url = "https://financialmodelingprep.com/api/v3/stock-screener?sector={}&industry={}&limit=6&apikey={}".format(
        urllib.parse.quote(sector), urllib.parse.quote(industry), FMP_KEY
    )
    # print("URL: " ,url)  #MONITORING
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    # print("Related Companies: ", json.loads(data))  #MONITORING
    return json.loads(data)
