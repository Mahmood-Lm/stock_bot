from flask import Flask, request
from matplotlib.cbook import pts_to_midstep
from matplotlib.style import context
import telegram
from mastermind import get_jsonparsed_data, get_related_companies, stockInfo, stockHistory, stockNews
from credetials import bot_token, bot_username, URL
from gtts import gTTS
import os
import matplotlib.pyplot as plt
import yfinance as yf
import mplfinance as mpf
import pandas as pd
import json

# import seaborn as sns
# from telegram.ext import *    #TEST
# from requests import * #TEST


global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    global rc_keyboard
    global news

    if update.callback_query != None:

        chat_id = update.callback_query.message.chat_id
        message_id = update.callback_query.message.message_id
        query = update.callback_query.data
        print("Query: ", query)
        if str(query)[0:2] == "P-":
            # bot.sendMessage(chat_id=chat_id, text="{}".format(query[2:]))

            bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
            info = stockInfo(query[2:])
            text = info.get("shortName")
            # bot.sendMessage(chat_id=chat_id, text=text)

            history = stockHistory(query[2:])
            fig = mpf.plot(history, type="candle", style="yahoo", volume=True, mav=(20, 50, 100), savefig="chart.png")
            with open("chart.png", "rb") as chart:
                bot.send_photo(photo=chart, caption=text, chat_id=chat_id, parse_mode="HTML")
            os.remove("chart.png")
            return 'OK'

        elif str(query)[0:2] == "V-":

            bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.RECORD_AUDIO)
            company = stockInfo(query[2:])
            text = f'{company.get("shortName")} is a company listed on {company.get("exchange")} currently worth {company.get("currentPrice")} dollars per share. They are part of the {company.get("industry")} industry and {company.get("sector")} sector.'
            voice = gTTS(text=text, lang="en", slow=False)
            voice.save("voice.ogg")
            with open("voice.ogg", "rb") as audio:
                bot.send_voice(chat_id=chat_id, voice=audio)
            os.remove("voice.ogg")
            return 'OK'


        # keyboard = [[telegram.InlineKeyboardButton("📈", callback_data="P-{}".format(company[0]["symbol"])), telegram.InlineKeyboardButton("🔊", callback_data="V-{}".format(company[0]["symbol"]))]]
        # keyboard.append(telegram.InlineKeyboardButton("Related Companies", callback_data="RL"))
        elif str(query)[0:3] == "RC-":
            company = stockInfo(query[3:])
            related_companies = get_related_companies(company.get("sector"), company.get("industry"))
            keyboard = []
            for rl in related_companies:
                if str(rl["companyName"]) != str(company.get("shortName")) and len(keyboard) < 4 and rl[
                    "companyName"] not in keyboard:
                    keyboard.append([telegram.InlineKeyboardButton("{}".format(rl["companyName"]),
                                                                   callback_data="{}".format(rl["symbol"]))])
            keyboard.append([telegram.InlineKeyboardButton("⬅️", callback_data="B-{}".format(company.get("symbol")))])

            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keys)
            rc_keyboard = keyboard  # Different back buttons depending on if the user has pressed the button or not to decrease delay
            rc_keyboard.pop()
            rc_keyboard.append(
                [telegram.InlineKeyboardButton("⬅️", callback_data="b-{}".format(company.get("symbol")))])
            print("RC Keyboard 1:", rc_keyboard)
            print("Keyboard: ", keyboard)
            return 'OK'


        elif str(query)[0:2] == "b-":
            company = stockInfo(query[2:])
            caption = "{} | <a href='{}'>Website</a>\nShare Price : {}$ ~ {}\nIndustry : {}\nSector : {}\n\nMore Info ⤵️".format(
                company.get("shortName"), company.get("website"), company.get("currentPrice"), company.get("exchange"),
                company.get("industry"), company.get("sector"))
            photo = company.get("logo_url")
            media = telegram.InputMediaPhoto(photo, caption=caption, parse_mode="HTML")

            keyboard = [[telegram.InlineKeyboardButton("📈", callback_data="P-{}".format(query[2:])),
                         telegram.InlineKeyboardButton("🔊", callback_data="V-{}".format(query[2:]))]]
            keyboard.append(
                [telegram.InlineKeyboardButton("Related Companies", callback_data="RC-{}".format(query[2:]))])
            keyboard.append([telegram.InlineKeyboardButton("Latest News", callback_data="N-{}".format(query[2:]))])

            keys = telegram.InlineKeyboardMarkup(keyboard)
            # bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keys)
            bot.edit_message_media(chat_id=chat_id, message_id=message_id, media=media, reply_markup=keys)
            return 'OK'


        elif str(query[0:2]) == "B-":
            keyboard = [[telegram.InlineKeyboardButton("📈", callback_data="P-{}".format(query[2:])),
                         telegram.InlineKeyboardButton("🔊", callback_data="V-{}".format(query[2:]))]]
            keyboard.append(
                [telegram.InlineKeyboardButton("Related Companies", callback_data="RC-{}".format(query[2:]))])
            keyboard.append([telegram.InlineKeyboardButton("Latest News", callback_data="N-{}".format(query[2:]))])
            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keys)
            return 'OK'



        elif str(query)[0:2] == "N-":
            news = stockNews(query[2:])
            keyboard = []
            for new in news[0:4]:
                keyboard.append(
                    [telegram.InlineKeyboardButton("{}".format(new["publisher"]), url="{}".format(new["link"]))])
            keyboard.append([telegram.InlineKeyboardButton("⬅️", callback_data="B-{}".format(query[2:])),
                             telegram.InlineKeyboardButton("➡️", callback_data="N2-{}".format(query[2:]))])
            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keys)
            return 'OK'


        elif str(query)[0:3] == "N2-":
            keyboard = []
            for new in news[4:]:
                keyboard.append(
                    [telegram.InlineKeyboardButton("{}".format(new["publisher"]), url="{}".format(new["link"]))])
            keyboard.append([telegram.InlineKeyboardButton("⬅️", callback_data="N-{}".format(query[3:]))])
            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keys)
            return 'OK'

        else:
            company = stockInfo(str(query))
            # keyboard = [[telegram.InlineKeyboardButton("📈", callback_data="P-{}".format(company.get("symbol"))), telegram.InlineKeyboardButton("🔊", callback_data="V-{}".format(company.get("symbol")))]]
            # keyboard.append([telegram.InlineKeyboardButton("Related Companies", callback_data="RC-{}".format(company.get("symbol")))])
            # keyboard.append([telegram.InlineKeyboardButton("Latest News", callback_data="N-{}".format(company.get("symbol")))])
            # keys = telegram.InlineKeyboardMarkup(keyboard)

            caption = "{} | <a href='{}'>Website</a>\nShare Price : {}$ ~ {}\nIndustry : {}\nSector : {}\n\nMore Info ⤵️".format(
                company.get("shortName"), company.get("website"), company.get("currentPrice"), company.get("exchange"),
                company.get("industry"), company.get("sector"))
            photo = company.get("logo_url")
            media = telegram.InputMediaPhoto(photo, caption=caption, parse_mode="HTML")
            # rc_keyboard.append([telegram.InlineKeyboardButton("🔙", callback_data="b-{}".format(company.get("symbol")))])
            keys = telegram.InlineKeyboardMarkup(rc_keyboard)
            print("RC key 2:", rc_keyboard)
            bot.edit_message_media(chat_id=chat_id, message_id=message_id, media=media, reply_markup=keys)
            # bot.send_photo(chat_id=chat_id, photo=photo, caption= caption, parse_mode="HTML", reply_markup=keys)
            return 'OK'
    else:

        try:
            chat_id = update.message.chat.id
            msg_id = update.message.message_id
        except Exception as Exc:
            print("Exc:", Exc)

        try:
            text = update.message.text.encode('utf-8').decode()
            if text == "/start":
                # bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                welcome = "Send a stock symbol to get up to date information about it\nFor example : GOOG, MSFT, NKE"
                bot.sendMessage(chat_id=chat_id, reply_to_message_id=msg_id, text=welcome)
                return 'Started'

            bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            get_info(text, chat_id, msg_id)
            # news = get_news(text)


        except Exception as e:

            print("Exception:", e)
            cpt = "Sorry, We couldn't find what you're looking for"
            bot.send_animation(chat_id=chat_id,
                               animation="https://i.pinimg.com/originals/13/7c/a9/137ca9e2a4de70b11d0ae475997e8004.gif",
                               caption=cpt, reply_to_message_id=msg_id)

        return 'OK'


def get_info(text, chat_id, msg_id):
    company = stockInfo(text.upper())
    # company = get_jsonparsed_data(text)
    # print("Company Name: ",company[0]["companyName"])
    keyboard = [[telegram.InlineKeyboardButton("📈", callback_data="P-{}".format(company.get("symbol"))),
                 telegram.InlineKeyboardButton("🔊", callback_data="V-{}".format(company.get("symbol")))]]
    keyboard.append(
        [telegram.InlineKeyboardButton("Related Companies", callback_data="RC-{}".format(company.get("symbol")))])
    keyboard.append([telegram.InlineKeyboardButton("Latest News", callback_data="N-{}".format(company.get("symbol")))])
    keys = telegram.InlineKeyboardMarkup(keyboard)

    caption = "{} | <a href='{}'>Website</a>\nShare Price : {}$ ~ {}\nIndustry : {}\nSector : {}\n\nMore Info ⤵️".format(
        company.get("shortName"), company.get("website"), company.get("currentPrice"), company.get("exchange"),
        company.get("industry"), company.get("sector"))
    photo = company.get("logo_url")
    bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_to_message_id=msg_id, parse_mode="HTML",
                   reply_markup=keys)


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return '.'


if __name__ == '__main__':
    app.run(threaded=True)