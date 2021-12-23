# python_basic_diploma/app/handlers.py
"""
Contains Telebot and basic handlers
"""
from os import environ
from sys import exit
from telebot import TeleBot
from telebot.types import InlineKeyboardButton
from telebot.types import InlineKeyboardMarkup
from telebot.types import ReplyKeyboardMarkup
from telebot.types import InputMediaPhoto
from telegram_bot_calendar import WMonthTelegramCalendar
from telegram_bot_calendar import LSTEP
from datetime import datetime

import app.dialogs as d
import app.service as s
from app.logger import get_logger


# initialize logger
logger = get_logger(__name__)

BOT_TOKEN = environ.get('BOT_TOKEN')
if BOT_TOKEN:
    bot = TeleBot(token=BOT_TOKEN)
    bot.remove_webhook()
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
else:
    logger.critical('No BOT_TOKEN.')
    exit()


"""Basic handlers"""
@bot.message_handler(commands=['start'])
def start_message(message):
    """Start command"""
    logger.info(f'[{message.text}] handler from chat {message.chat.id}.')
    bot.send_message(
        message.from_user.id, d.START_MESSAGE, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def help_message(message):
    """Help command"""
    logger.info(f'[{message.text}] handler from chat {message.chat.id}.')
    bot.send_message(
        message.from_user.id, d.HELP_MEASSAGE, parse_mode='Markdown')


"""Bot handlers"""
@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def basic_commands(message):
    """
    Message handler for lowprice, highprice and bestdeal commands.
    Send command description message, create session and run pre_ask_town handler.
    """
    logger.info(f'[{message.text}] handler from chat {message.chat.id}.')
    msg_dict = {
        '/lowprice': d.LOWPRICE_MESSAGE,
        '/highprice': d.HIGHPRICE_MESSSAGE,
        '/bestdeal': d.BESTDEAL_MESSAGE,
    }
    if s.create_session(message.chat.id, message.text):
        bot.send_message(
            message.chat.id, 
            msg_dict[message.text.lower()], 
            parse_mode='Markdown')
        next_handler_pre_ask_town(message)
    else:
        bot.reply_to(message, d.UNKNOWN_ERROR_MESSAGE)


@bot.message_handler(commands=['history'])
def history_command(message):
    """Message handler for history command."""
    logger.info(f'[{message.text}] handler from chat {message.chat.id}.')
    pass


"""Error handlers"""
@bot.message_handler(content_types=[
    'audio', 
    'photo', 
    'voice', 
    'video', 
    'document',
    'location', 
    'contact', 
    'sticker',
    'text'
])
def error_message(message):
    """Any content without command"""
    logger.info(f'[{message.text}] handler from chat {message.chat.id}.')
    bot.reply_to(message, d.ERROR_CONTENT_MESSAGE)


"""Next handlers"""
def next_handler_pre_ask_town(message) -> None:
    """Send GET_TOWN_MESSAGE and register ask_town next handler."""
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_town] '
        f'from chat {message.chat.id}.'))
    msg = bot.send_message(
        message.chat.id, d.GET_TOWN_MESSAGE, parse_mode='Markdown')
    bot.register_next_step_handler(msg, next_handler_ask_town)


def next_handler_ask_town(message) -> None:
    """Get town name."""
    logger.info((
        f'[{message.text}] run [next_handler_ask_town] '
        f'from chat {message.chat.id}.'))
    bot.send_chat_action(message.chat.id, 'typing')
    is_error, return_town, markup, next_step = s.proceccing_town_id(
        message.chat.id, message.text)
    if is_error:
        bot.reply_to(message, d.UNKNOWN_ERROR_MESSAGE)
    else:
        if return_town:
            bot.send_message(
                message.chat.id, 
                f'{d.TOWN_SELECTED_MESSAGE}{return_town}', 
                parse_mode='Markdown')
            # next handler
            next_handler_pre_ask_check_in(message)
        else:
            if not markup:
                bot.send_message(
                    message.chat.id, 
                    d.WRONG_TOWN_MESSAGE, 
                    parse_mode='Markdown')
                next_handler_pre_ask_town(message)
            else:
                msg = bot.send_message(
                    message.chat.id,
                    d.SELECT_TOWN_MESSAGE,
                    reply_markup=markup,
                    parse_mode='Markdown')
                bot.register_next_step_handler(msg, next_handler_ask_town)


def next_handler_pre_ask_check_in(message):
    """Send GET_CHECK_IN message, generate calendar keyboard"""
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_check_in] '
        f'from chat {message.chat.id}.'))
    min_date = datetime.now().date()
    calendar, step = WMonthTelegramCalendar(
        calendar_id=0, 
        current_date=min_date, 
        min_date=min_date, 
        locale='ru').build()
    bot.send_message(
        message.chat.id, 
        f'{d.GET_CHECK_IN_MESSAGE} {LSTEP[step]}', 
        reply_markup=calendar)


@bot.callback_query_handler(func=WMonthTelegramCalendar.func(calendar_id=0))
def next_handler_ask_check_in(callback):
    """Callback function to get check_in date."""
    logger.debug('next_handler_ask_check_in start.')
    min_date = datetime.now().date()
    result, key, step = WMonthTelegramCalendar(
        calendar_id=0,
        current_date=min_date,
        min_date=min_date, 
        locale='ru').process(callback.data)
    if not result and key:
        bot.edit_message_text(
            f'{d.GET_CHECK_IN_MESSAGE} {LSTEP[step]}', 
            callback.message.chat.id, 
            callback.message.message_id, 
            reply_markup=key)
    elif result:
        if s.proceccing_check_in_date(callback.message.chat.id, str(result)):
            # next step
            next_handler_pre_ask_check_out(callback.message)
        else:
            bot.reply_to(callback.message, d.UNKNOWN_ERROR_MESSAGE)
            next_handler_pre_ask_check_in(callback.message)


def next_handler_pre_ask_check_out(message):
    """Send GET_CHECK_OUT message, generate calendar keyboard"""
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_check_out] '
        f'from chat {message.chat.id}.'))
    str_min_date = s.get_check_out_min_date(message.chat.id)
    if str_min_date:
        min_date = datetime.strptime(str_min_date, '%Y-%m-%d').date()
    else:
        min_date = datetime.now().date()
    
    calendar, step = WMonthTelegramCalendar(
        calendar_id=1, 
        current_date=min_date, 
        min_date=min_date, 
        locale='ru').build()
    bot.send_message(
        message.chat.id, 
        f'{d.GET_CHECK_OUT_MESSAGE} {LSTEP[step]}', 
        reply_markup=calendar)


@bot.callback_query_handler(func=WMonthTelegramCalendar.func(calendar_id=1))
def next_handler_ask_check_out(callback):
    """Callback function to get check_out date."""
    logger.debug('next_handler_ask_check_out start.')
    str_min_date = s.get_check_out_min_date(callback.message.chat.id)
    if str_min_date:
        min_date = datetime.strptime(str_min_date, '%Y-%m-%d').date()
    else:
        min_date = datetime.now().date()
    
    result, key, step = WMonthTelegramCalendar(
        calendar_id=1,
        current_date=min_date,
        min_date=min_date, 
        locale='ru').process(callback.data)
    if not result and key:
        bot.edit_message_text(
            f'{d.GET_CHECK_OUT_MESSAGE} {LSTEP[step]}', 
            callback.message.chat.id, 
            callback.message.message_id, 
            reply_markup=key)
    elif result:
        session_update, next_step = s.proceccing_check_out_date(
            callback.message.chat.id, str(result))
        if session_update:
            # next handler
            if next_step == 'results_num':
                next_handler_pre_ask_results_num(callback.message)
            elif next_step == 'min_price':
                next_handler_pre_ask_min_price(callback.message)
        else:
            bot.reply_to(callback.message, d.UNKNOWN_ERROR_MESSAGE)
            next_handler_pre_ask_check_in(callback.message)


def next_handler_pre_ask_min_price(message):
    """Send GET_MIN_PRICE message and register ask_min_price next handler."""
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_min_price] '
        f'from chat {message.chat.id}.'))
    msg = bot.send_message(
        message.chat.id, d.GET_MIN_PRICE, parse_mode='Markdown')
    bot.register_next_step_handler(msg, next_handler_ask_min_price)


def next_handler_ask_min_price(message):
    """Get min_price"""
    logger.info((
        f'[{message.text}] run [next_handler_ask_min_price] '
        f'from chat {message.chat.id}.'))
    user_error, is_error = s.process_int_values(
        message.chat.id, 'min_price', message.text)
    if user_error:
        bot.reply_to(message, d.WRONG_PRICE)
        next_handler_pre_ask_min_price(message)
    else:
        if is_error:
            bot.reply_to(message, d.UNKNOWN_ERROR_MESSAGE)
            next_handler_pre_ask_min_price(message)
        else:
            # next handler
            next_handler_pre_ask_max_price(message)


def next_handler_pre_ask_max_price(message):
    """Send GET_MAX_PRICE message and register ask_max_price next handler."""
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_max_price] '
        f'from chat {message.chat.id}.'))
    msg = bot.send_message(
        message.chat.id, d.GET_MAX_PRICE, parse_mode='Markdown')
    bot.register_next_step_handler(msg, next_handler_ask_max_price)


def next_handler_ask_max_price(message):
    """Get max_price."""
    logger.info((
        f'[{message.text}] run [next_handler_ask_max_price] '
        f'from chat {message.chat.id}.'))
    user_error, is_error = s.process_int_values(
        message.chat.id, 'max_price', message.text)
    if user_error:
        bot.reply_to(message, d.WRONG_PRICE)
        next_handler_pre_ask_max_price(message)
    else:
        if is_error:
            bot.reply_to(message, d.UNKNOWN_ERROR_MESSAGE)
            next_handler_pre_ask_min_price(message)
        else:
            # next handler
            next_handler_pre_ask_min_distance(message)


def next_handler_pre_ask_min_distance(message):
    """
    Send GET_MIN_DISTANCE message and register ask_min_distance next handler.
    """
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_min_distance] '
        f'from chat {message.chat.id}.'))
    msg = bot.send_message(
        message.chat.id, d.GET_MIN_DISTANCE, parse_mode='Markdown')
    bot.register_next_step_handler(msg, next_handler_ask_min_distance)


def next_handler_ask_min_distance(message):
    """Get min_distance."""
    logger.info((
        f'[{message.text}] run [next_handler_ask_min_distance] '
        f'from chat {message.chat.id}.'
    ))
    user_error, is_error = s.process_int_values(
        message.chat.id, 'min_distance', message.text
    )
    if user_error:
        bot.reply_to(message, d.WRONG_DISTANCE)
        next_handler_pre_ask_min_distance(message)
    else:
        if is_error:
            bot.reply_to(message, d.UNKNOWN_ERROR_MESSAGE)
            next_handler_pre_ask_min_distance(message)
        else:
            # next handler
            next_handler_pre_ask_max_distance(message)


def next_handler_pre_ask_max_distance(message):
    """
    Send GET_MAX_DISTANCE message and register ask_max_distance next handler.
    """
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_max_distance] '
        f'from chat {message.chat.id}.'
    ))
    msg = bot.send_message(
        message.chat.id, d.GET_MAX_DISTANCE, parse_mode='Markdown')
    bot.register_next_step_handler(msg, next_handler_ask_max_distance)


def next_handler_ask_max_distance(message):
    """Get max_distance."""
    logger.info((
        f'[{message.text}] run [next_handler_ask_max_distance] '
        f'from chat {message.chat.id}.'))
    user_error, is_error = s.process_int_values(
        message.chat.id, 'max_distance', message.text)
    
    if user_error:
        bot.reply_to(message, d.WRONG_DISTANCE)
        next_handler_pre_ask_max_distance(message)
    else:
        if is_error:
            bot.reply_to(message, d.UNKNOWN_ERROR_MESSAGE)
            next_handler_pre_ask_min_distance(message)
        else:
            # next handler
            next_handler_pre_ask_results_num(message)


def next_handler_pre_ask_results_num(message):
    """
    Send GET_RESULTS_NUM message and register ask_results_num next handler.
    """
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_results_num] '
        f'from chat {message.chat.id}.'))
    msg = bot.send_message(
        message.chat.id, d.GET_RESULTS_NUM_MESSAGE, parse_mode='Markdown')
    bot.register_next_step_handler(msg, next_handler_ask_results_num)


def next_handler_ask_results_num(message):
    """Get results_num."""
    logger.info((
        f'[{message.text}] run [next_handler_ask_results_num] '
        f'from chat {message.chat.id}.'
    ))
    user_error, is_error, num_results = s.proceccing_results_num(
        message.chat.id, message.text
    )
    if user_error:
        bot.reply_to(message, d.WRONG_RESULTS_NUM_MESSAGE)
        next_handler_pre_ask_results_num(message)
    else:
        if is_error:
            bot.reply_to(message, d.UNKNOWN_ERROR_MESSAGE)
            next_handler_pre_ask_results_num(message)
        else:
            bot.send_message(
                message.chat.id, 
                f'{d.SELECT_RESULTS_NUM_MESSAGE}{num_results}', 
                parse_mode='Markdown')
            # next handler
            next_handler_pre_ask_display_photos(message)



def next_handler_pre_ask_display_photos(message):
    """
    Send GET_DISPLAY_PHOTOS message, generate reply_keyboard and register ask_max_price next handler.
    """
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_display_photos] '
        f'from chat {message.chat.id}.'))
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 1
    markup.add(d.DISPLAY_PHOTOS_TRUE, d.DISPLAY_PHOTOS_FALSE)
    msg = bot.send_message(
        chat_id=message.chat.id,
        text=d.GET_DISPLAY_PHOTOS,
        reply_markup=markup,
        parse_mode='Markdown')
    bot.register_next_step_handler(msg, next_handler_ask_display_photos)


def next_handler_ask_display_photos(message):
    """Get display_photos."""
    logger.info((
        f'[{message.text}] run [next_handler_ask_display_photos] '
        f'from chat {message.chat.id}.'))
    is_error, display_photos = s.proceccing_display_photos(
        message.chat.id, message.text)
    if is_error:
        bot.reply_to(message, d.WRONG_DISPLAY_PHOTOS)
    else:
        if len(display_photos):
            # show results
            show_results(message)
        else:
            next_handler_pre_ask_photos_num(message)



def next_handler_pre_ask_photos_num(message):
    """
    Send GET_PHOTOS_NUM message and register ask_photos_num next handler.
    """
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_photos_num] '
        f'from chat {message.chat.id}.'))
    msg = bot.send_message(
        message.chat.id, d.GET_PHOTOS_NUM_MESSAGE , parse_mode='Markdown')
    bot.register_next_step_handler(msg, next_handler_ask_photos_num)


def next_handler_ask_photos_num(message):
    """Get photos_num."""
    logger.info((
        f'[{message.text}] run [next_handler_ask_photos_num] '
        f'from chat {message.chat.id}.'))
    is_error, display_photos = s.proceccing_display_photos(
        message.chat.id, message.text)
    if is_error:
        bot.reply_to(message, d.WRONG_PHOTOS_NUM_MESSAGE)
        next_handler_pre_ask_photos_num(message)
    else:
        bot.send_message(
            message.chat.id, 
            f'{d.SELECT_PHOTOS_NUM_MESSAGE}{display_photos}', 
            parse_mode='Markdown')
        # show results
        show_results(message)


def show_results(message):
    """Send search results."""
    bot.send_chat_action(message.chat.id, 'typing')
    result_list = s.get_results(message.chat.id)
    logger.debug(f'Search results list contain {len(result_list)} hotels.')
    if len(result_list) == 0:
        bot.send_message(
            message.chat.id, d.NO_RESULTS_MESSAGE, parse_mode='Markdown')
    else:
        bot.send_message(
            chat_id=message.chat.id, 
            text=f'{d.RESULTS_MESSAGE} {len(result_list)}', 
            parse_mode='Markdown'
        )
        for result in result_list:
            try:
                bot.send_chat_action(message.chat.id, 'typing')
                description = d.HOTEL_DESCRIPTION
                url = d.HOTEL_URL_SCHEMA
                for key, value in result['description'].items():
                    description = description.replace(f'[{key}]', str(value))
                    url = url.replace(f'[{key}]', str(value))
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(text=d.HOTEL_BOOK_MESSAGE, url=url))
                logger.debug(f'Display hotel: {description}.')
                if len(result['photos']) > 0:
                    # send hotel photos
                    media = list()
                    for photo in result['photos']:
                        media.append(InputMediaPhoto(media=photo))
                    bot.send_media_group(
                        chat_id=message.chat.id, media=media)
                # send hotel description
                bot.send_message(
                    chat_id=message.chat.id, 
                    text=description, 
                    parse_mode='Markdown',
                    reply_markup=markup)
            except Exception as e:
                logger.error(f'show_results error: {e}.')
                next
