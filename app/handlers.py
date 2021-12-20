# python_basic_diploma/app/handlers.py
"""
Contains Telebot and basic handlers
"""
from os import environ
from sys import exit
from telebot import TeleBot
import telebot
from telebot.types import ReplyKeyboardMarkup, InputMediaPhoto

import app.dialogs as d
import app.service as s
from app.logger import get_logger


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
    bot.send_message(message.from_user.id, d.START_MESSAGE)


@bot.message_handler(commands=['help'])
def help_message(message):
    """Help command"""
    logger.info(f'[{message.text}] handler from chat {message.chat.id}.')
    bot.send_message(message.from_user.id, d.HELP_MEASSAGE)


"""Bot handlers"""
@bot.message_handler(commands=['photo'])
def photo(message):
    from requests import request
    urls = ['https://exp.cdn-hotels.com/hotels/37000000/36790000/36789900/36789845/d4aada11_y.jpg',
    'https://exp.cdn-hotels.com/hotels/37000000/36790000/36789900/36789845/d4aada11_w.jpg'
    ]
    photos = list()
    for url in urls:
        if url == urls[0]:
            photos.append(telebot.types.InputMediaPhoto(url, caption='Caption'))
        else:
            photos.append(telebot.types.InputMediaPhoto(url))
    
    bot.send_media_group(message.chat.id, photos)
    #bot.send_photo(message.chat.id, photo=url, caption='Caption')

@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def basic_commands(message):
    logger.info(f'[{message.text}] handler from chat {message.chat.id}.')
    msg_dict = {
        '/lowprice': d.LOWPRICE_MESSAGE,
        '/highprice': d.HIGHPRICE_MESSSAGE,
        '/bestdeal': d.BESTDEAL_MESSAGE,
    }
    if s.create_session(message.chat.id, message.text):
        bot.send_message(message.chat.id, msg_dict[message.text.lower()])
        next_handler_pre_ask_town(message)
    else:
        bot.reply_to(message, d.UNKNOWN_ERROR_MESSAGE)


@bot.message_handler(commands=['history'])
def history_command(message):
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
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_town] '
        f'from chat {message.chat.id}.'
    ))
    msg = bot.send_message(message.chat.id, d.GET_TOWN_MESSAGE)
    bot.register_next_step_handler(msg, next_handler_ask_town)


def next_handler_ask_town(message) -> None:
    logger.info((
        f'[{message.text}] run [next_handler_ask_town] '
        f'from chat {message.chat.id}.'
    ))
    bot.send_chat_action(message.chat.id, 'typing')
    is_error, return_town, markup, next_step = s.proceccing_town_id(
        message.chat.id, message.text
    )
    if is_error:
        bot.reply_to(message, d.UNKNOWN_ERROR_MESSAGE)
    else:
        if return_town:
            bot.send_message(message.chat.id, f'{d.TOWN_SELECTED_MESSAGE}{return_town}')
            # next handler
            if next_step == 'results_num':
                next_handler_pre_ask_results_num(message)
            elif next_step == 'min_price':
                next_handler_pre_ask_min_price(message)
        else:
            if not markup:
                bot.send_message(message.chat.id, d.WRONG_TOWN_MESSAGE)
                next_handler_pre_ask_town(message)
            else:
                msg = bot.send_message(
                    message.chat.id,
                    d.SELECT_TOWN_MESSAGE,
                    reply_markup=markup
                )
                bot.register_next_step_handler(msg, next_handler_ask_town)


def next_handler_pre_ask_min_price(message):
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_min_price] '
        f'from chat {message.chat.id}.'
    ))
    msg = bot.send_message(message.chat.id, d.GET_MIN_PRICE)
    bot.register_next_step_handler(msg, next_handler_ask_min_price)


def next_handler_ask_min_price(message):
    logger.info((
        f'[{message.text}] run [next_handler_ask_min_price] '
        f'from chat {message.chat.id}.'
    ))
    user_error, is_error = s.process_int_values(
        message.chat.id, 'min_price', message.text
    )
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
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_max_price] '
        f'from chat {message.chat.id}.'
    ))
    msg = bot.send_message(message.chat.id, d.GET_MAX_PRICE)
    bot.register_next_step_handler(msg, next_handler_ask_max_price)


def next_handler_ask_max_price(message):
    logger.info((
        f'[{message.text}] run [next_handler_ask_max_price] '
        f'from chat {message.chat.id}.'
    ))
    user_error, is_error = s.process_int_values(
        message.chat.id, 'max_price', message.text
    )
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
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_min_distance] '
        f'from chat {message.chat.id}.'
    ))
    msg = bot.send_message(message.chat.id, d.GET_MIN_DISTANCE)
    bot.register_next_step_handler(msg, next_handler_ask_min_distance)


def next_handler_ask_min_distance(message):
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
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_max_distance] '
        f'from chat {message.chat.id}.'
    ))
    msg = bot.send_message(message.chat.id, d.GET_MAX_DISTANCE)
    bot.register_next_step_handler(msg, next_handler_ask_max_distance)


def next_handler_ask_max_distance(message):
    logger.info((
        f'[{message.text}] run [next_handler_ask_max_distance] '
        f'from chat {message.chat.id}.'
    ))
    user_error, is_error = s.process_int_values(
        message.chat.id, 'max_distance', message.text
    )
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
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_results_num] '
        f'from chat {message.chat.id}.'
    ))
    msg = bot.send_message(message.chat.id, d.GET_RESULTS_NUM_MESSAGE)
    bot.register_next_step_handler(msg, next_handler_ask_results_num)


def next_handler_ask_results_num(message):
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
                f'{d.SELECT_RESULTS_NUM_MESSAGE}{num_results}'
            )
            # next handler
            next_handler_pre_ask_display_photos(message)



def next_handler_pre_ask_display_photos(message):
    logger.info((
        f'[{message.text}] run [next_handler_pre_ask_display_photos] '
        f'from chat {message.chat.id}.'
    ))
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 1
    markup.add(d.DISPLAY_PHOTOS_TRUE, d.DISPLAY_PHOTOS_FALSE)
    msg = bot.send_message(
        chat_id=message.chat.id,
        text=d.GET_DISPLAY_PHOTOS,
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, next_handler_ask_display_photos)


def next_handler_ask_display_photos(message):
    logger.info((
        f'[{message.text}] run [next_handler_ask_display_photos] '
        f'from chat {message.chat.id}.'
    ))
    is_error, display_photos = s.proceccing_display_photos(
        message.chat.id, message.text
    )
    if is_error:
        bot.reply_to(message, d.WRONG_DISPLAY_PHOTOS)
    else:
        bot.send_message(
            message.chat.id, 
            f'{d.SELECT_DISPLAY_PHOTOS}{display_photos}'
        )
        # show results
        show_results(message)


def show_results(message):
    bot.send_chat_action(message.chat.id, 'typing')
    result_list = s.get_results(message.chat.id)
    logger.debug(f'Search results list contain {len(result_list)} hotels.')
    if len(result_list) == 0:
        bot.send_message(message.chat.id, d.NO_RESULTS_MESSAGE)
    else:
        bot.send_message(
            chat_id=message.chat.id, 
            text=f'{d.RESULTS_MESSAGE} {len(result_list)}', 
            parse_mode='Markdown'
        )
        for result in result_list:
            bot.send_chat_action(message.chat.id, 'typing')
            description = d.HOTEL_DESCRIPTION
            for key, value in result['description'].items():
                description = description.replace(f'[{key}]', str(value))
            logger.debug(f'Display hotel: {description}.')
            if len(result['photos']) > 0:
                # display photos
                media = list()
                for photo in result['photos']:
                    if len(media) == 0:
                        media.append(InputMediaPhoto(
                            media=photo, 
                            caption=description, 
                            parse_mode='Markdown'
                        ))
                    else:
                        media.append(InputMediaPhoto(media=photo))
                bot.send_media_group(message.chat.id, media)
            else:
                # do not display photos
                bot.send_message(
                    chat_id=message.chat.id, 
                    text=description, 
                    parse_mode='Markdown'
                )
    
