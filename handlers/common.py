from handlers import bot


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.from_user.id, 'Привет')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.from_user.id, 'Помощь')
