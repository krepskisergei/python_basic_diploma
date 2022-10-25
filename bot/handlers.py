from datetime import timedelta, date
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
# from telebot.types import InputMediaPhoto

from telegram_bot_calendar import WMonthTelegramCalendar

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


def get_next_handler(current_step: str) -> object:
    """Define next handler by current_step."""
    return handler


# Basic handlers
@bot.message_handler(commands=['start'])
def start_message(message: Message):
    """Process Start command."""
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, m.START_MESSAGE)


@bot.message_handler(commands=['help'])
def help_message(message: Message):
    """Process Help command."""
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, m.HELP_MESSAGE)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def basic_commands(message: Message):
    """Process Lowprice, Highprice and Bestdeal commands."""
    bot.send_chat_action(message.chat.id, 'typing')
    msgs, step = s.process_command(
        message.chat.id, message.text)
    for msg in msgs:
        _m = bot.send_message(
            message.chat.id, msg.msg, reply_markup=msg.markup)
    if step:
        bot.register_next_step_handler(_m, get_next_handler(step))


@bot.message_handler(commands=['history'])
def history_command(message: Message):
    """Process History command."""
    bot.send_chat_action(message.chat.id, 'typing')
    pass


@bot.message_handler(content_types=['text'])
def check_text(message: Message):
    """Process unknown text."""
    bot.send_chat_action(message.chat.id, 'typing')
    msgs, step = s.process_command(message.chat.id, message.text)
    for msg in msgs:
        _m = bot.send_message(
            message.chat.id, msg.msg, reply_markup=msg.markup)
    if step:
        bot.register_next_step_handler(_m, get_next_handler(step))


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
def error_message(message: Message):
    """Any content without command"""
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, m.BAD_CONTENT_MESSAGE)


# Next handlers
def handler(message: Message):
    """Handler to process user messages."""
    bot.send_chat_action(message.chat.id, 'typing')
    msgs, step = s.process_command(
        message.chat.id, message.text)
    for msg in msgs:
        _m = bot.send_message(
            message.chat.id, msg.msg, reply_markup=msg.markup)
    if step:
        bot.register_next_step_handler(_m, get_next_handler(step))


@bot.callback_query_handler(func=WMonthTelegramCalendar.func(calendar_id=0))
def callback_check_in(callback: CallbackQuery):
    """Process checkIn callback."""
    min_date = date.today()
    chat_id = callback.message.chat.id
    result, key, step = WMonthTelegramCalendar(
        calendar_id=0,
        current_date=min_date,
        min_date=min_date,
        locale='ru'
    ).process(callback.data)
    if not result and key:
        bot.edit_message_text(
            m.CHECK_IN_START_MESSAGE,
            chat_id,
            callback.message.message_id,
            reply_markup=key
        )
    if result:
        msgs, step = s.process_command(chat_id, result)
        for msg in msgs:
            _m = bot.send_message(chat_id, msg.msg, reply_markup=msg.markup)
        if step:
            bot.register_next_step_handler(_m, get_next_handler(step))


@bot.callback_query_handler(func=WMonthTelegramCalendar.func(calendar_id=1))
def callback_check_out(callback: CallbackQuery):
    """Process checkOut callback."""
    chat_id = callback.message.chat.id
    # get min date
    history = s.get_history(chat_id)
    try:
        min_date = history.checkIn
    except AttributeError:
        min_date = date.today()
    min_date += timedelta(days=1)
    result, key, step = WMonthTelegramCalendar(
        calendar_id=1,
        current_date=min_date,
        min_date=min_date,
        locale='ru'
    ).process(callback.data)
    if not result and key:
        bot.edit_message_text(
            m.CHECK_OUT_START_MESSAGE,
            chat_id,
            callback.message.message_id,
            reply_markup=key
        )
    if result:
        msgs, step = s.process_command(chat_id, result)
        for msg in msgs:
            _m = bot.send_message(chat_id, msg.msg, reply_markup=msg.markup)
        if step:
            bot.register_next_step_handler(_m, get_next_handler(step))
