from urllib.request import urlopen
import urllib.parse
import json
from credetials import FMP_key
import certifi
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import mplfinance as mpf

# import http.client, urllib.parse


def get_jsonparsed_data(symbol):
    """
    Receive the content of ``url``, parse it as JSON and return the object.
    Parameters
    ----------
    url : str
    Returns
    -------
    dict
    """
    url = ("https://financialmodelingprep.com/api/v3/profile/{}?apikey={}".format(symbol.upper(), FMP_key))
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)


def get_related_companies(sector , industry):

    url = ("https://financialmodelingprep.com/api/v3/stock-screener?sector={}&industry={}&limit=6&apikey={}".format(urllib.parse.quote(sector), urllib.parse.quote(industry), FMP_key))
    # print("URL: " ,url)  #MONITORING
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    # print("Related Companies: ", json.loads(data))  #MONITORING
    return json.loads(data)

def stockInfo(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    return info


def stockHistory(symbol):
    stock = yf.Ticker(symbol.upper())
    history = stock.history("2y")
    return history


def stockNews(symbol):
    stock = yf.Ticker(symbol.upper())
    news = stock.news
    return news


# def get_article(symbol):
#     """
#     Receive the content of ``url``, parse it as JSON and return the object.

#     Parameters
#     ----------
#     url : str

#     Returns
#     -------
#     dict
#     """

#     conn = http.client.HTTPSConnection('api.marketaux.com')
#     params = urllib.parse.urlencode({
#     'api_token': Marketaux_Key,
#     'symbols': symbol.upper(),
#     'limit': 3,
#     'filter_entities': "true",
#     'language': 'en',
#     })

#     conn.request('GET', '/v1/news/all?{}'.format(params))
#     res = conn.getresponse()
#     data = res.read()
#     print(data.decode("utf-8"))  #TEST
#     return json.loads(data)


# def get_news(symbol):
#     """
#     Receive the content of ``url``, parse it as JSON and return the object.

#     Parameters
#     ----------
#     url : str

#     Returns
#     -------
#     dict
#     """

#     url = ("https://financialmodelingprep.com/api/v3/stock_news?tickers={}&limit=3&apikey={}".format(symbol.upper(), FMP_key))
#     response = urlopen(url, cafile=certifi.where())
#     data = response.read().decode("utf-8")
#     return json.loads(data)