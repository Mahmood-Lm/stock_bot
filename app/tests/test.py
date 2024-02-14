import yfinance as yf

# stock = yf.Ticker("V")
# info = stock.info
# print(list(info.keys()))
# print(yf.Ticker("GOOG").fast_info)

print(yf.Ticker("GOOG").info.get("symbol", "KIRekhar"))