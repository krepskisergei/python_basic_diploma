from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import WMonthTelegramCalendar as TCal

from app.app_logger import get_logger
from app.config import TOKEN
import app.service as s
import bot.dialog as d
from classes.tbot import TBot


# initiate logger
logger = get_logger(__name__)
# initiate bot
bot = TBot(token=TOKEN, parse_mode='Markdown')
bot.remove_webhook()
bot.enable_save_next_step_handlers(delay=120)
bot.load_next_step_handlers()


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
def error(message: Message):
    """Any content without command"""
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, d.ERROR_CONTENT)


# Commands handlers
@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    """Send start command message."""
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, d.COMMAND_START)


@bot.message_handler(commands=['help'])
def help(message: Message) -> None:
    """Send help command message."""
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, d.COMMAND_HELP)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def main_commands(message: Message) -> None:
    """Process main commands."""
    bot.send_chat_action(message.chat.id, 'typing')
    replies = s.command_replies(message.chat.id, message.text)
    bot.send_reply_messages(replies)
    if len(replies) > 0:
        if replies[-1].next_handler:
            bot.register_next_step_handler_by_chat_id(
                message.chat.id, bot_next_handler)


@bot.message_handler(commands=['history'])
def history_command(message: Message) -> None:
    """Process history command."""
    bot.send_chat_action(message.chat.id, 'typing')
    replies = s.get_user_history(message.chat.id)
    bot.send_reply_messages(replies)


# Callback handlers
@bot.callback_query_handler(func=TCal.func(calendar_id=0))
@bot.callback_query_handler(func=TCal.func(calendar_id=1))
def calendar_check_in(callback: CallbackQuery) -> None:
    """"""
    replies = s.callback_replies(callback.message.chat.id, callback)
    bot.send_reply_messages(replies)
    if len(replies) > 0:
        if replies[-1].next_handler:
            bot.register_next_step_handler_by_chat_id(
                callback.message.chat.id, bot_next_handler)


# Next handlers and text messages handlers
@bot.message_handler(content_types=['text'])
def bot_next_handler(message: Message) -> None:
    """Next handler for all proceccing commands."""
    bot.send_chat_action(message.chat.id, 'typing')
    replies = s.message_replies(message.chat.id, message.text)
    bot.send_reply_messages(replies)
    if len(replies) > 0:
        if replies[-1].next_handler:
            bot.register_next_step_handler_by_chat_id(
                message.chat.id, bot_next_handler)
