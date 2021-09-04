import sys, os
import telebot


# Add parent directory path for importing config, rapidapi, db
sys.path.insert(1, os.path.abspath('.'))


import config


bot = telebot.TeleBot(token=config.BOT_TOKEN)


# common command handlers (start, help)
from handlers import common
# lowprice handler
# highprice handler
# bestdeal handler
# history handler
# error messages handler
from handlers import error
