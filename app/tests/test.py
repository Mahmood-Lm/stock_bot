import yfinance as yf

stock = yf.Ticker("GOOG")
info = stock.info
print(info)