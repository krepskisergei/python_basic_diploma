from handlers import bot
import messages


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.from_user.id, messages.START_MESSAGE)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.from_user.id, messages.HELP_MEASSAGE)
