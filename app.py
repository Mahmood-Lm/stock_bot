# from calendar import c
# from cmath import inf
# from email import message
# from turtle import st
from socket import timeout
from flask import Flask, request
from matplotlib.style import context
import telegram
from mastermind import get_jsonparsed_data, get_related_companies, stockInfo, stockHistory
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

    try:
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
            fig = mpf.plot(history, type="candle", style="yahoo", volume=True, mav=(20, 50, 100), savefig="Test2.png")
            with open("Test2.png", "rb") as chart:
                bot.send_photo(photo=chart, caption=text, chat_id=chat_id, parse_mode="HTML")
            os.remove("Test2.png")
            return 'OK'

        elif str(query)[0:2] == "V-":
            
            bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.RECORD_AUDIO)
            info = stockInfo(query[2:])
            text = f'{info.get("shortName")} is a company listed on {info.get("exchange")} currently worth {info.get("currentPrice")} dollars per share. They are part of the {info.get("industry")} industry and {info.get("sector")} sector.'
            voice = gTTS(text=text, lang="en", slow=False)
            voice.save("voice.ogg")
            with open("voice.ogg", "rb") as audio:
                bot.send_voice(chat_id=chat_id, voice=audio)
            os.remove("voice.ogg")
            return 'OK'
        
        
        # keyboard = [[telegram.InlineKeyboardButton("📈", callback_data="P-{}".format(company[0]["symbol"])), telegram.InlineKeyboardButton("🔊", callback_data="V-{}".format(company[0]["symbol"]))]]
        # keyboard.append(telegram.InlineKeyboardButton("Related Companies", callback_data="RL"))
        elif str(query)[0:3] == "RC-":
            company = get_jsonparsed_data(query[3:])
            related_companies = get_related_companies(company[0]["sector"], company[0]["industry"])
            keyboard = []
            for rl in related_companies:
                if str(rl["companyName"]) != str(company[0]["companyName"]) and len(keyboard) < 4 and rl["companyName"] not in keyboard:
                    keyboard.append([telegram.InlineKeyboardButton("{}".format(rl["companyName"]), callback_data="{}".format(rl["symbol"]))])
            keyboard.append([telegram.InlineKeyboardButton("🔙", callback_data="b-{}".format(company[0]["symbol"]))])
            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keys)
            return 'OK'

        
        elif str(query)[0:2] == "b-":
            company = get_jsonparsed_data(query[2:])
            # print("Company Name: ",company[0]["companyName"])
            keyboard = [[telegram.InlineKeyboardButton("📈", callback_data="P-{}".format(company[0]["symbol"])), telegram.InlineKeyboardButton("🔊", callback_data="V-{}".format(company[0]["symbol"]))]]
            keyboard.append([telegram.InlineKeyboardButton("Related Companies", callback_data="RC-{}".format(company[0]["symbol"]))])

            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keys)
            return 'OK'

        
        else:
            company = get_jsonparsed_data(str(query))
            # related_companies = get_related_companies(company[0]["sector"], company[0]["industry"])
            keyboard = [[telegram.InlineKeyboardButton("📈", callback_data="P-{}".format(company[0]["symbol"])), telegram.InlineKeyboardButton("🔊", callback_data="V-{}".format(company[0]["symbol"]))]]
            keyboard.append([telegram.InlineKeyboardButton("Related Companies", callback_data="RC-{}".format(company[0]["symbol"]))])

            keys = telegram.InlineKeyboardMarkup(keyboard)

            caption = "{} | <a href='{}'>Website</a>\nShare Price : {}$ ~ {}\nIndustry : {}\nSector : {}\nCeo : {}\n\nMore Info ⤵️".format(company[0]["companyName"], company[0]["website"], company[0]["price"], company[0]["exchangeShortName"], company[0]["industry"], company[0]["sector"], company[0]["ceo"])
            photo = company[0]["image"]
            bot.send_photo(chat_id=chat_id, photo=photo, caption= caption, parse_mode="HTML", reply_markup=keys)
            return 'OK'
    except Exception as ex:
        print("EX:", ex)


        try:
            chat_id = update.message.chat.id
            msg_id = update.message.message_id
        except Exception as Exc:
            print("Exc:", Exc)



        try:
            text = update.message.text.encode('utf-8').decode()
            if text == "/start":
                bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                welcome = "Send a stock symbol to get up to date information about it\nFor example : GOOG, MSFT, NKE"
                bot.sendMessage(chat_id=chat_id, reply_to_message_id=msg_id, text=welcome)
                # voice = gTTS(text=welcome, lang="en", slow=False)
                # voice.save("start_voice.ogg")
                # with open("start_voice.ogg", "rb") as audio:
                #     bot.send_voice(chat_id=chat_id, voice=audio)
                # os.remove("start_voice.ogg")
                return 'Started'

            get_info(text, chat_id, msg_id)
            # news = get_news(text)

            
        except Exception as e:
            
            print("Exception:", e)
            cpt = "Sorry, We couldn't find what you're looking for"
            bot.send_animation(chat_id=chat_id, animation="https://i.pinimg.com/originals/13/7c/a9/137ca9e2a4de70b11d0ae475997e8004.gif", caption= cpt, reply_to_message_id=msg_id)        
        
        return 'OK'


def get_info(text, chat_id, msg_id):
    company = get_jsonparsed_data(text)
    # print("Company Name: ",company[0]["companyName"])
    keyboard = [[telegram.InlineKeyboardButton("📈", callback_data="P-{}".format(company[0]["symbol"])), telegram.InlineKeyboardButton("🔊", callback_data="V-{}".format(company[0]["symbol"]))]]
    keyboard.append([telegram.InlineKeyboardButton("Related Companies", callback_data="RC-{}".format(company[0]["symbol"]))])

    keys = telegram.InlineKeyboardMarkup(keyboard)

    caption = "{} | <a href='{}'>Website</a>\nShare Price : {}$ ~ {}\nIndustry : {}\nSector : {}\nCeo : {}\n\nMore Info ⤵️".format(company[0]["companyName"], company[0]["website"], company[0]["price"], company[0]["exchangeShortName"], company[0]["industry"], company[0]["sector"], company[0]["ceo"])
    photo = company[0]["image"]
    bot.send_photo(chat_id=chat_id, photo=photo, caption= caption, reply_to_message_id=msg_id, parse_mode="HTML", reply_markup=keys)


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
