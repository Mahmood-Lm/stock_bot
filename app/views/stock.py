import telegram
import os
from app.controllers.profile import get_chat, get_chat_watchlist
from app.controllers.stock import (
    get_stock_info,
    get_stock_recommendations,
    get_stocks_info,
    get_stock_news,
    get_stock_history,
    get_related_companies,
)
import mplfinance as mpf
from gtts import gTTS


def get_watch_list(update, bot):
    # get the word info
    # stock_info = get_stocks_info(update.message.text)
    chat_id = update.effective_chat.id
    # # text = ""
    # for stock in get_chat_watchlist(chat_id=chat_id):
    #     text = text + "\n" + stock
    watchlist = get_chat_watchlist(chat_id=chat_id)
    print("Watchlist:", watchlist, type(watchlist))
    watchlist_str = " ".join(watchlist)
    print(watchlist_str)
    if watchlist != []:
        text = get_stocks_info(watchlist_str)
        photo = "https://i.imgur.com/rCtCzim.png"
        keyboard = []
        for stock in watchlist:
            keyboard.append(
                [telegram.InlineKeyboardButton("{}".format(str(stock)), callback_data="S-{}".format(str(stock)))])
        keys = telegram.InlineKeyboardMarkup(keyboard)
        bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=text,
            parse_mode="HTML",
            reply_markup=keys,
        )
    else:
        text = "Your Watchlist is empty.\nTry adding some stocks to your watchlist to get daily updates."
        bot.send_animation(
            chat_id=chat_id,
            animation="https://c.tenor.com/fyf6FMrdkOIAAAAd/john-travolta-what.gif",
            caption=text,
        )
    print("*** Halaale ***")

    return 'OK'


def get_stock_chart(update, bot):
    chat_id = update.effective_chat.id
    query = update.callback_query.data
    msg_id = update.callback_query.message.message_id
    message = update.callback_query.message.caption
    # print("Message: ", message)
    splitted_message = message.split("\n")
    # print("Splitted Message:" ,splitted_message)
    bot.send_chat_action(
        chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO
    )
    splitted = query.split("-")
    x = 0
    for p in splitted_message:
        if "Period" in p:
            per = p.replace("Period: ", "")
            print("Period:", per)
        if "Moving average" in p:
            mav = p.replace("Moving average: [", "").replace("]", "")
            # print("MAV:{}, type:{}".format(mav, type(mav)))
            ma = [int(c) for c in mav.split(", ") if c != ""]
            # print("MA:{}, type:{}".format(ma, type(ma)))
        if "Interval" in p:
            I = p.replace("Interval: ", "")
            # print("Interval:", I)

    if splitted[0] == "I":
        I = splitted[1]
    elif splitted[0] == "P":
        if query.count("-") == 2:
            per = splitted[1]
            ma = []
            # I = "1h"
        else:
            x = 1
            per = "2y"
            ma = []
            I = "1wk"
    else:
        if int(splitted[1]) not in ma:
            ma.append(int(splitted[1]))
        else:
            ma.remove(int(splitted[1]))
    stock_symbol = splitted[-1]
    # print(stock_symbol)
    info = get_stock_info(stock_symbol)
    text = "{}\nPeriod: {}\nMoving average: {}\nInterval: {}".format(info.get("shortName"), per, ma, I)

    # TODO adding time interval as input and the ability to define start and finish period date

    history = get_stock_history(stock_symbol, period=per, interval=I)
    mpf.plot(
        history,
        type="candle",
        title="{}".format(info.get("shortName")),
        style="yahoo",
        volume=True,
        mav=ma,
        scale_padding={'left': 0.2, 'top': 0.8, 'right': 1, 'bottom': 1},
        savefig="chart.png",
    )
    # print("Mav2:", ma, type(ma))
    keyboard = [[telegram.InlineKeyboardButton("1D", callback_data="P-1d-{}".format(stock_symbol)),
                 telegram.InlineKeyboardButton("1W", callback_data="P-7d-{}".format(stock_symbol)),
                 telegram.InlineKeyboardButton("1M", callback_data="P-1mo-{}".format(stock_symbol)),
                 telegram.InlineKeyboardButton("1Y", callback_data="P-12mo-{}".format(stock_symbol))],
                [telegram.InlineKeyboardButton("MA7", callback_data="M-7-{}".format(stock_symbol)),
                 telegram.InlineKeyboardButton("MA30", callback_data="M-30-{}".format(stock_symbol)),
                 telegram.InlineKeyboardButton("MA60", callback_data="M-60-{}".format(stock_symbol)),
                 telegram.InlineKeyboardButton("MA100", callback_data="M-100-{}".format(stock_symbol))],
                [telegram.InlineKeyboardButton("5 Min", callback_data="I-5m-{}".format(stock_symbol)),
                 telegram.InlineKeyboardButton("1 Hour", callback_data="I-1h-{}".format(stock_symbol)),
                 telegram.InlineKeyboardButton("1 Day", callback_data="I-1d-{}".format(stock_symbol)),
                 telegram.InlineKeyboardButton("1 Week", callback_data="I-1wk-{}".format(stock_symbol))]]
    keys = telegram.InlineKeyboardMarkup(keyboard)
    with open("chart.png", "rb") as chart:
        if x == 1:
            bot.send_photo(
                photo=chart, caption=text, chat_id=chat_id, parse_mode="HTML", reply_markup=keys)
        else:
            media = telegram.InputMediaPhoto(chart, caption=text, parse_mode="HTML")
            bot.edit_message_media(
                chat_id=chat_id, message_id=msg_id, media=media, reply_markup=keys)
    os.remove("chart.png")
    return "OK"


def get_voice_description(update, bot):
    chat_id = update.effective_chat.id
    query = update.callback_query.data
    stock_symbol = query[2:]
    bot.send_chat_action(
        chat_id=chat_id, action=telegram.ChatAction.RECORD_AUDIO
    )
    stock_info = get_stock_info(stock_symbol)
    if query[0:2] == "V-":
        overall_sentiment, latest_recommendations = get_stock_recommendations(stock_symbol)
        if overall_sentiment == "buy":
            x = "to buy"
        elif overall_sentiment == "sell":
            x = "to sell"
        else:
            x = "neutral"
        print("Latest Recoms:", latest_recommendations)
        keyboard = [[telegram.InlineKeyboardButton(
            "Full Description", callback_data="D-{}".format(stock_symbol)
        )]]
        text = f'{stock_info.get("shortName")} is a company listed on {stock_info.get("exchange")} currently worth {stock_info.get("currentPrice")} dollars per share. They are part of the {stock_info.get("industry")} industry and {stock_info.get("sector")} sector. The overall recommendation of financial firms in the past month is {x}. Press the button below to recieve the full description.'
    elif query[0:2] == "D-":
        text = str(stock_info.get("longBusinessSummary"))
        keyboard = []
    keys = telegram.InlineKeyboardMarkup(keyboard)
    voice = gTTS(text=text, lang="en", slow=False)
    voice.save("voice.ogg")
    with open("voice.ogg", "rb") as audio:
        bot.send_voice(chat_id=chat_id, voice=audio, reply_markup=keys)
    os.remove("voice.ogg")
    return "OK"


def get_preference(update, bot):
    chat_id = update.effective_chat.id
    msg_id = update.message.message_id
    Time = get_chat(chat_id).get("news_teller_time")
    setting = "This is your current setting: {}\nSend your new prefered time if you want to change it.".format(Time)
    bot.sendMessage(
        chat_id=chat_id, reply_to_message_id=msg_id, text=setting
    )
    return 'OK'