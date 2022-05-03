from calendar import c
from email import message
from flask import Flask, request
import telegram
from mastermind import get_jsonparsed_data, get_related_companies
from credetials import bot_token, bot_username, URL
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
        query = update.callback_query.data
        print("Query: ", query)
        company = get_jsonparsed_data(query)  
        related_companies = get_related_companies(company[0]["sector"], company[0]["industry"])
        keyboard = []
        for rl in related_companies:
            if str(rl["companyName"]) != str(company[0]["companyName"]) and len(keyboard) < 3 and rl["companyName"] not in keyboard:
                keyboard.append([telegram.InlineKeyboardButton("{}".format(rl["companyName"]), callback_data="{}".format(rl["symbol"]))])
    
        keys = telegram.InlineKeyboardMarkup(keyboard)
        caption = "{} | <a href='{}'>Website</a>\nShare Price : {}$ ~ {}\nIndustry : {}\nSector : {}\nCeo : {}\n\nRelated Companies ⤵️".format(company[0]["companyName"], company[0]["website"], company[0]["price"], company[0]["exchangeShortName"], company[0]["industry"], company[0]["sector"], company[0]["ceo"])
        photo = company[0]["image"]
        bot.send_photo(photo=photo, caption= caption, parse_mode="HTML", reply_markup=keys, chat_id=chat_id)
        return 'OK'
    except Exception as ex:
        print("EX:", ex)


        try:
            chat_id = update.message.chat.id
            msg_id = update.message.message_id
        except Exception as Exc:
            print("Exc:", Exc)
            pass



        try:
            text = update.message.text.encode('utf-8').decode()
            if text == "/start":
                welcome = "Send a stock symbol to get up to date information about it\nFor example : GOOG, MSFT, NKE"
                bot.sendMessage(chat_id=chat_id, reply_to_message_id=msg_id, text=welcome)
                return 'Started'

            get_info(text, chat_id, msg_id)
            # news = get_news(text)

            
        except Exception as e:
            
            print("Exception:", e)
            cpt = "Sorry, We couldn't find what you're looking for"
            bot.send_animation(chat_id=chat_id, animation="https://i.pinimg.com/originals/13/7c/a9/137ca9e2a4de70b11d0ae475997e8004.gif", caption= cpt, reply_to_message_id=msg_id)        
        
        return 'OK'


def get_info(text , chat_id, msg_id):
    company = get_jsonparsed_data(text)  
    related_companies = get_related_companies(company[0]["sector"], company[0]["industry"])
    keyboard = []

    
    for rl in related_companies:
        if str(rl["companyName"]) != str(company[0]["companyName"]) and len(keyboard) < 3 and rl["companyName"] not in keyboard:
            keyboard.append([telegram.InlineKeyboardButton("{}".format(rl["companyName"]), callback_data="{}".format(rl["symbol"]))])

    keys = telegram.InlineKeyboardMarkup(keyboard)

    caption = "{} | <a href='{}'>Website</a>\nShare Price : {}$ ~ {}\nIndustry : {}\nSector : {}\nCeo : {}\n\nRelated Companies ⤵️".format(company[0]["companyName"], company[0]["website"], company[0]["price"], company[0]["exchangeShortName"], company[0]["industry"], company[0]["sector"], company[0]["ceo"])
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
