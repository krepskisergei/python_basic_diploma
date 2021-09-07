import sys, os
import telebot


# Add parent directory path for importing messages, rapidapi, db
sys.path.insert(1, os.path.abspath('.'))


BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise EnvironmentError
else:
    bot = telebot.TeleBot(token=BOT_TOKEN)


# common command handlers (start, help)
from handlers import common
# lowprice handler
# highprice handler
# bestdeal handler
# history handler
# error messages handler
from handlers import error
