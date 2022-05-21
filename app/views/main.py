from telegram import Update


# set up the introductory statement for the bot when the /start command is invoked
def start(update: Update, bot):
    bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
