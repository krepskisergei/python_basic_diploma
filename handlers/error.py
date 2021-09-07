from handlers import bot
import messages


@bot.message_handler(content_types=['text'])
def text_message(message):
    bot.send_message(message.from_user.id, 'Текст.')


@bot.message_handler(content_types=[
    'audio', 
    'photo', 
    'voice', 
    'video', 
    'document',
    'location', 
    'contact', 
    'sticker'
])
def error_message(message):
    bot.send_message(message.from_user.id, messages.ERROR_CONTENT_MESSAGE)
