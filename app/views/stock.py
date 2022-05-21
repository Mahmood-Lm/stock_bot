import telegram
import os
from app.controllers.stock import (
    get_stock_info,
    get_stocks_info,
    get_stock_news,
    get_stock_history,
    get_related_companies,
)
import mplfinance as mpf
from gtts import gTTS


def get_watch_list(update, context):
    # get the word info
    stock_info = get_stocks_info(update.message.text)
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text="Hello there. Provide any English word and I will give you a bunch "
        "of information about it.",
    )


def get_stock_chart(update, bot):
    query = update.callback_query.data
    stock_symbol = query[2:]
    chat_id = update.effective_chat.id
    bot.send_chat_action(
        chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO
    )
    info = get_stock_info(stock_symbol)
    text = info.get("shortName")
    # bot.sendMessage(chat_id=chat_id, text=text)

    history = get_stock_history(stock_symbol, "2y")
    mpf.plot(
        history,
        type="candle",
        style="yahoo",
        volume=True,
        mav=(20, 50, 100),
        savefig="chart.png",
    )
    with open("chart.png", "rb") as chart:
        bot.send_photo(
            photo=chart, caption=text, chat_id=chat_id, parse_mode="HTML"
        )
    os.remove("chart.png")
    return "OK"


def get_voice_description(update, context):
    chat_id = update.effective_chat.id
    query = update.callback_query.data
    stock_symbol = query[2:]
    context.bot.send_chat_action(
        chat_id=chat_id, action=telegram.ChatAction.RECORD_AUDIO
    )
    stock_info = get_stock_info(stock_symbol)
    text = f'{stock_info.get("shortName")} is a company listed on {stock_info.get("exchange")} currently worth {stock_info.get("currentPrice")} dollars per share. They are part of the {stock_info.get("industry")} industry and {stock_info.get("sector")} sector.'
    voice = gTTS(text=text, lang="en", slow=False)
    voice.save("voice.ogg")
    with open("voice.ogg", "rb") as audio:
        context.bot.send_voice(chat_id=chat_id, voice=audio)
    os.remove("voice.ogg")
    return "OK"
