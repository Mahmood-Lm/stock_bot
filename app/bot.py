# from curses.panel import bottom_panel
# from unicodedata import numeric
from flask import Flask, request
from matplotlib.pyplot import text
from matplotlib.style import context
from pytz import timezone
import telegram
import telegram.ext
import datetime
from app.controllers.profile import create_chat, get_chat, update_chat_settings, get_chat_watchlist, \
    add_stock_to_watchlist, remove_stock_from_watchlist
from app.controllers.stock import (
    get_related_companies,
    get_stock_info,
    get_stock_history,
    get_stock_news,
    get_stock_recommendations,
    get_stocks_info,

)
from config.credetials import BOT_TOKEN, SERVER_URL
from app.views.stock import get_preference, get_stock_chart, get_voice_description, get_watch_list
import logging
from app.models.init_db import initialize
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)
sched = BackgroundScheduler()
sched.start()


@app.route("/{}".format(BOT_TOKEN), methods=["POST"])
def respond():
    # Try
    global sched
    global bot
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    print(update)
    global rc_keyboard
    global news

    if update.callback_query is not None:

        chat_id = update.callback_query.message.chat_id
        message_id = update.callback_query.message.message_id
        query = update.callback_query.data
        print("Query: ", query)
        if str(query)[0:2] == "P-" or str(query)[0:2] == "M-" or str(query)[0:2] == "I-":
            return get_stock_chart(update, bot)
        elif str(query)[0:2] == "V-" or str(query)[0:2] == "D-":
            return get_voice_description(update, bot)
        elif str(query)[0:3] == "RC-":
            company = get_stock_info(query[3:])
            related_companies = get_related_companies(
                company.get("sector"), company.get("industry")
            )
            keyboard = []
            for rl in related_companies:
                if (
                        str(rl["companyName"]) != str(company.get("shortName"))
                        and len(keyboard) < 4
                        and rl["companyName"] not in keyboard
                ):
                    keyboard.append(
                        [
                            telegram.InlineKeyboardButton(
                                "{}".format(rl["companyName"]),
                                callback_data="{}".format(rl["symbol"]),
                            )
                        ]
                    )
            keyboard.append(
                [
                    telegram.InlineKeyboardButton(
                        "⬅️", callback_data="B-{}".format(company.get("symbol"))
                    )
                ]
            )

            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(
                chat_id=chat_id, message_id=message_id, reply_markup=keys
            )
            # Different back buttons depending on if the user has pressed the button or not to decrease delay
            rc_keyboard = keyboard
            rc_keyboard.pop()
            rc_keyboard.append(
                [
                    telegram.InlineKeyboardButton(
                        "⬅️", callback_data="b-{}".format(company.get("symbol"))
                    )
                ]
            )
            # print("RC Keyboard 1:", rc_keyboard)
            # print("Keyboard: ", keyboard)
            return "OK"

        elif str(query)[0:2] == "b-":
            company = get_stock_info(query[2:])
            caption = "{} | <a href='{}'>Website</a>\nShare Price : {}$ ~ {}\nIndustry : {}\nSector : {}\n\nMore Info ⤵️".format(
                company.get("shortName"),
                company.get("website"),
                company.get("currentPrice"),
                company.get("exchange"),
                company.get("industry"),
                company.get("sector"),
            )
            photo = company.get("logo_url")
            media = telegram.InputMediaPhoto(photo, caption=caption, parse_mode="HTML")
            if company.get("symbol") not in get_chat_watchlist(chat_id):
                watchlist_button = [telegram.InlineKeyboardButton(
                    "Add to Watchlist ⭐", callback_data="W-{}".format(company.get("symbol"))
                )]
            else:
                watchlist_button = [telegram.InlineKeyboardButton(
                    "Remove from Watchlist", callback_data="R-{}".format(company.get("symbol"))
                )]

            keyboard = [
                [
                    telegram.InlineKeyboardButton(
                        "📈", callback_data="P-{}".format(query[2:])
                    ),
                    telegram.InlineKeyboardButton(
                        "📝", callback_data="Re-{}".format(query[2:])
                    ),
                    telegram.InlineKeyboardButton(
                        "🔊", callback_data="V-{}".format(query[2:])
                    ),
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Related Companies", callback_data="RC-{}".format(query[2:])
                    )
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Latest News", callback_data="N-{}".format(query[2:])
                    )
                ],
                watchlist_button,
            ]

            keys = telegram.InlineKeyboardMarkup(keyboard)
            # bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keys)
            bot.edit_message_media(
                chat_id=chat_id, message_id=message_id, media=media, reply_markup=keys
            )
            return "OK"

        elif str(query[0:2]) == "B-":
            if query[2:].upper() not in get_chat_watchlist(chat_id):
                watchlist_button = [telegram.InlineKeyboardButton(
                    "Add to Watchlist ⭐", callback_data="W-{}".format(query[2:])
                )]
            else:
                watchlist_button = [telegram.InlineKeyboardButton(
                    "Remove from Watchlist", callback_data="R-{}".format(query[2:])
                )]
            keyboard = [
                [
                    telegram.InlineKeyboardButton(
                        "📈", callback_data="P-{}".format(query[2:])
                    ),
                    telegram.InlineKeyboardButton(
                        "📝", callback_data="Re-{}".format(query[2:])
                    ),
                    telegram.InlineKeyboardButton(
                        "🔊", callback_data="V-{}".format(query[2:])
                    ),
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Related Companies", callback_data="RC-{}".format(query[2:])
                    )
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Latest News", callback_data="N-{}".format(query[2:])
                    )
                ],
                watchlist_button,
            ]
            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(
                chat_id=chat_id, message_id=message_id, reply_markup=keys
            )
            return "OK"

        elif str(query)[0:2] == "N-":
            news = get_stock_news(query[2:])
            keyboard = []
            for new in news[0:4]:
                keyboard.append(
                    [
                        telegram.InlineKeyboardButton(
                            "{}".format(new["publisher"]), url="{}".format(new["link"])
                        )
                    ]
                )
            keyboard.append(
                [
                    telegram.InlineKeyboardButton(
                        "⬅️", callback_data="B-{}".format(query[2:])
                    ),
                    telegram.InlineKeyboardButton(
                        "➡️", callback_data="N2-{}".format(query[2:])
                    ),
                ]
            )
            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(
                chat_id=chat_id, message_id=message_id, reply_markup=keys
            )
            return "OK"

        elif str(query)[0:3] == "N2-":
            keyboard = []
            for new in news[4:]:
                keyboard.append(
                    [
                        telegram.InlineKeyboardButton(
                            "{}".format(new["publisher"]), url="{}".format(new["link"])
                        )
                    ]
                )
            keyboard.append(
                [
                    telegram.InlineKeyboardButton(
                        "⬅️", callback_data="N-{}".format(query[3:])
                    )
                ]
            )
            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(
                chat_id=chat_id, message_id=message_id, reply_markup=keys
            )
            return "OK"

        elif str(query)[0:2] == "W-":
            add_stock_to_watchlist(chat_id=chat_id, stock_symbol=query[2:])
            keyboard = [
                [
                    telegram.InlineKeyboardButton(
                        "📈", callback_data="P-{}".format(query[2:])
                    ),
                    telegram.InlineKeyboardButton(
                        "📝", callback_data="Re-{}".format(query[2:])
                    ),
                    telegram.InlineKeyboardButton(
                        "🔊", callback_data="V-{}".format(query[2:])
                    ),
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Related Companies", callback_data="RC-{}".format(query[2:])
                    )
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Latest News", callback_data="N-{}".format(query[2:])
                    )
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Remove from Watchlist", callback_data="R-{}".format(query[2:])
                    )
                ],
            ]
            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(
                chat_id=chat_id, message_id=message_id, reply_markup=keys
            )
            return "OK"

        elif str(query)[0:2] == "R-":
            remove_stock_from_watchlist(chat_id=chat_id, stock_symbol=query[2:])
            keyboard = [
                [
                    telegram.InlineKeyboardButton(
                        "📈", callback_data="P-{}".format(query[2:])
                    ),
                    telegram.InlineKeyboardButton(
                        "📝", callback_data="Re-{}".format(query[2:])
                    ),
                    telegram.InlineKeyboardButton(
                        "🔊", callback_data="V-{}".format(query[2:])
                    ),
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Related Companies", callback_data="RC-{}".format(query[2:])
                    )
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Latest News", callback_data="N-{}".format(query[2:])
                    )
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Add to Watchlist ⭐", callback_data="W-{}".format(query[2:])
                    )
                ],
            ]
            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(
                chat_id=chat_id, message_id=message_id, reply_markup=keys
            )
            return 'OK'

        elif str(query)[0:2] == "C-":
            splitted = query.split("-")
            update_chat_settings(chat_id, active_hours_start="00:00", active_hours_end="00:00",
                                 news_teller_time=str(splitted[1]), timezone=str(splitted[2]))
            keyboard = [[telegram.InlineKeyboardButton("Remove", callback_data="Remove")]]
            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_text(text="{} set as your prefered time".format(str(splitted[1])), chat_id=chat_id,
                                  message_id=message_id, reply_markup=keys)
            print("*** Mohaghagh ***")
            try:
                try:
                    sched.remove_job(str(chat_id))
                except Exception as e:
                    print(e)
                sched.add_job(get_watch_list, 'cron', hour=splitted[1][:2], minute=splitted[1][3:],
                              timezone=splitted[2], args=[update, bot], id=str(chat_id))
                print("*** Meske OKe ***")
            except Exception as e:
                print(e)
            return 'OK'

        elif str(query) == "Remove":
            sched.remove_job(str(chat_id))
            print("*** Shod ***")
            update_chat_settings(chat_id, active_hours_start="00:00", active_hours_end="00:00", news_teller_time=None,
                                 timezone="")
            bot.edit_message_text(text="Prefered Time removed.\nSend your new prefered time.", chat_id=chat_id,
                                  message_id=message_id)
            return 'OK'

        elif str(query)[:2] == "S-":
            bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            text = str(query[2:])
            get_info(text=text, chat_id=chat_id)
            return 'OK'

        elif str(query)[:3] == "Re-":
            overall_sentiment, latest_recommendations = get_stock_recommendations(query[3:])
            if overall_sentiment == "buy":
                x = "👍🏻"
            elif overall_sentiment == "neutral":
                x = "😐"
            else:
                x = "👎🏻"

            if query[3:].upper() not in get_chat_watchlist(chat_id):
                watchlist_button = [telegram.InlineKeyboardButton(
                    "Add to Watchlist ⭐", callback_data="W-{}".format(query[3:])
                )]
            else:
                watchlist_button = [telegram.InlineKeyboardButton(
                    "Remove from Watchlist", callback_data="R-{}".format(query[3:])
                )]

            keyboard = [
                [
                    telegram.InlineKeyboardButton(
                        "📈", callback_data="P-{}".format(query[3:])
                    ),
                    telegram.InlineKeyboardButton(
                        x, callback_data="NOTHING"
                    ),
                    telegram.InlineKeyboardButton(
                        "🔊", callback_data="V-{}".format(query[3:])
                    ),
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Related Companies", callback_data="RC-{}".format(query[3:])
                    )
                ],
                [
                    telegram.InlineKeyboardButton(
                        "Latest News", callback_data="N-{}".format(query[3:])
                    )
                ],
                watchlist_button,
            ]

            keys = telegram.InlineKeyboardMarkup(keyboard)
            bot.edit_message_reply_markup(
                chat_id=chat_id, message_id=message_id, reply_markup=keys
            )
            return 'OK'


        elif str(query) == "NOTHING":
            return 'OK'


        else:
            company = get_stock_info(str(query))

            caption = """
                {} | <a href='{}'>Website</a>\nShare Price : {}$ ~ {}\nIndustry : {}\nSector : {}\n\nMore Info ⤵️
            """.format(
                company.get("shortName"),
                company.get("website"),
                company.get("currentPrice"),
                company.get("exchange"),
                company.get("industry"),
                company.get("sector"),
            )
            photo = company.get("logo_url")
            media = telegram.InputMediaPhoto(photo, caption=caption, parse_mode="HTML")
            keys = telegram.InlineKeyboardMarkup(rc_keyboard)
            # print("RC key 2:", rc_keyboard)
            bot.edit_message_media(
                chat_id=chat_id, message_id=message_id, media=media, reply_markup=keys
            )
            # bot.send_photo(chat_id=chat_id, photo=photo, caption= caption, parse_mode="HTML", reply_markup=keys)
            return "OK"
    else:

        try:
            chat_id = update.message.chat.id
            msg_id = update.message.message_id
        except Exception as Exc:
            print("Exc:", Exc)

        try:
            text = update.message.text.encode("utf-8").decode()

            if text == "/start":
                # initialize()
                try:
                    create_chat(chat_id)
                except Exception:
                    pass
                first_name = update.message.chat.first_name
                welcome = f"Hello {first_name},\n\nSend a stock symbol to get up to date information about it\nFor example : GOOG, MSFT, NKE\n\nSend your prefered time in this format to receive daily updates: Time Timezone\ne.g. : 10:50 Europe/Rome\n\nSend /setting command to check your current time setting.\n\nSend /watchlist command to receive your watchlist"
                bot.sendMessage(
                    chat_id=chat_id, reply_to_message_id=msg_id, text=welcome
                )
                # print("Chat ID: ", chat_id)
                return "Started"

            elif text == "/setting":
                return get_preference(update, bot)

            elif text == "/watchlist":
                try:
                    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    get_watch_list(update, bot)
                except Exception:
                    bot.sendMessage(
                        chat_id=chat_id, reply_to_message_id=msg_id,
                        text="Your Watchlist is empty.\nTry adding some stocks to your watchlist to get daily updates."
                    )
                return 'OK'
            elif any(char.isdigit() for char in text):
                try:
                    time = datetime.datetime.strptime(text[:5], "%H:%M")
                    tz = timezone(text[6:])
                    print(str(tz))
                    keyboard = [
                        [
                            telegram.InlineKeyboardButton(
                                "Confirm", callback_data="C-{}-{}".format(time.strftime("%H:%M"), str(tz))
                            )
                        ]
                    ]
                    keys = telegram.InlineKeyboardMarkup(keyboard)
                    bot.sendMessage(
                        chat_id=chat_id, reply_to_message_id=msg_id,
                        text="This is the time you've chosen: {} in {} timezone.".format(time.strftime("%H:%M"),
                                                                                         str(tz)), reply_markup=keys
                    )
                except Exception:
                    bot.sendMessage(
                        chat_id=chat_id, reply_to_message_id=msg_id,
                        text="Please enter time in the correct format\ne.g: 12:25 Europe/Rome")

                return 'OK'

            bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            get_info(text, chat_id)
            return 'OK'

        except Exception as e:

            print("Exception:", e)
            cpt = "Sorry, We couldn't find what you're looking for"
            bot.send_animation(
                chat_id=chat_id,
                animation="https://i.pinimg.com/originals/13/7c/a9/137ca9e2a4de70b11d0ae475997e8004.gif",
                caption=cpt,
                reply_to_message_id=msg_id,
            )

        return "OK"


def get_info(text, chat_id):
    company = get_stock_info(text.upper())
    if company.get("symbol") not in get_chat_watchlist(chat_id):
        watchlist_button = [telegram.InlineKeyboardButton(
            "Add to Watchlist ⭐", callback_data="W-{}".format(company.get("symbol"))
        )]
    else:
        watchlist_button = [telegram.InlineKeyboardButton(
            "Remove from Watchlist", callback_data="R-{}".format(company.get("symbol"))
        )]
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                "📈", callback_data="P-{}".format(company.get("symbol"))
            ),
            telegram.InlineKeyboardButton(
                "📝", callback_data="Re-{}".format(company.get("symbol"))
            ),
            telegram.InlineKeyboardButton(
                "🔊", callback_data="V-{}".format(company.get("symbol"))
            ),
        ],
        [
            telegram.InlineKeyboardButton(
                "Related Companies", callback_data="RC-{}".format(company.get("symbol"))
            )
        ],
        [
            telegram.InlineKeyboardButton(
                "Latest News", callback_data="N-{}".format(company.get("symbol"))
            )
        ],
        watchlist_button,
    ]
    keys = telegram.InlineKeyboardMarkup(keyboard)

    caption = """
            {} | <a href='{}'>Website</a>\nShare Price : {}$ ~ {}\nIndustry : {}\nSector : {}\n\nMore Info ⤵️
        """.format(
        company.get("shortName"),
        company.get("website"),
        company.get("currentPrice"),
        company.get("exchange"),
        company.get("industry"),
        company.get("sector"),
    )
    photo = company.get("logo_url")
    bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keys,
    )


@app.route("/set_webhook", methods=["GET", "POST"])
def set_webhook():
    s = bot.setWebhook("{URL}{HOOK}".format(URL=SERVER_URL, HOOK=BOT_TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route("/")
def index():
    return "."


if __name__ == "__main__":
    app.run(threaded=True)
