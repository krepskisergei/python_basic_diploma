import sys, os
import telebot


# Add parent directory path for importing messages, rapidapi, db
sys.path.insert(1, os.path.abspath('.'))


import config


class Query:
    """
    Класс запроса пользователя
    """
    def __init__(self, type: str) -> None:
        self.type = type
        self.town = None
        self.result_count = None
    
    @property
    def type(self) -> str:
        return None if self.type == None else self.type
    
    @property
    def town(self) -> str:
        return None if self.town == None else self.town
    
    @property
    def result_count(self) -> int:
        return None if self.result_count == None else self.result_count
    
    @town.setter
    def town(self, town: str):
        self.town = town
    
    @result_count.setter
    def result_count(self, result_count: int) -> None:
        self.result_count = result_count \
            if result_count < config.RESULT_MAX_COUNT \
            else config.RESULT_MAX_COUNT


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
