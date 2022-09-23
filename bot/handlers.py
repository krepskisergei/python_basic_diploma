from telebot import TeleBot
from telebot.types import Message
# from telebot.types import InlineKeyboardButton
# from telebot.types import InlineKeyboardMarkup
# from telebot.types import ReplyKeyboardMarkup
# from telebot.types import InputMediaPhoto

# from telegram_bot_calendar import WMonthTelegramCalendar
# from telegram_bot_calendar import LSTEP
# from datetime import datetime

from app.logger import get_logger
from app.config import TOKEN
import app.service as s
import bot.messages as m


# initiate
logger = get_logger(__name__)

bot = TeleBot(token=TOKEN)
bot.remove_webhook()
bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.parse_mode = 'Markdown'


# Basic handlers
@bot.message_handler(commands=['start'])
def start_message(message: Message):
    """Process Start command."""
    bot.send_message(message.chat.id, m.START_MESSAGE)


@bot.message_handler(commands=['help'])
def help_message(message: Message):
    """Process Help command."""
    bot.send_message(message.chat.id, m.HELP_MESSAGE)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def basic_commands(message: Message):
    """Process Lowprice, Highprice and Bestdeal commands."""
    s.process_command(message.chat.id, message.text)


@bot.message_handler(commands=['history'])
def history_command(message: Message):
    """Process History command."""
    pass


@bot.message_handler(content_types=['text'])
def check_text(message: Message):
    """Process unknown text."""
    pass


# Error handlers
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
    """Any content without command"""
    bot.reply_to(message, m.BAD_CONTENT_MESSAGE)


# Next handlers
