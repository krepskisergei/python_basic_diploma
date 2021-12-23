# python_basic_diploma/app/service.py
"""
Contain all system functions (bussiness logic)
"""
from os import environ
from telebot.types import ReplyKeyboardMarkup

from app.logger import get_logger
from app.classes import Session
from app.database import db
import app.rapidapi as r


# initialize logger
logger = get_logger(__name__)

session = Session()


def create_session(chat_id: str, command: str) -> bool:
    """
    Create session for chat_id.
    Return True if ok, else return False.
    """
    result = session.create(chat_id, command)
    logger.debug(f'Session: {session}')
    return result


def proceccing_town_id(chat_id: str, town_name: str) -> set:
    """
    Get town_id by town_name and save it in session.
    Return 
        is_error: bool, 
        result_town: str, 
        markup: ReplyKeyboardMarkup | None
        next_step: str TODO: перенести в CheckOutDate
    """
    logger.info(
        f'Running get_town_id(chat_id={chat_id}, town_name={town_name})')
    is_error = False
    result_town = str()
    next_step = str()
    # try to get town_id from database
    town_id_result = db.select_town(town_name)
    if town_id_result is not None and len(town_id_result) > 0:
        # town in database
        logger.info(f'Town {town_name} was found in database.')
    else:
        # no town in database, search town in rapidapi
        town_id_result = r.get_town_list(town_name)
        # save results in database
        if len(town_id_result) > 0:
            for entity in town_id_result:
                db.insert_town(entity)
    
    if len(town_id_result) == 0:
        # no such town in results
        logger.info(f'get_town_id({town_name}): No town_id to return.')
        is_error = False    # no results error
        markup = None
    elif len(town_id_result) == 1:
        # one result
        town_id = town_id_result[0]['destinationId']
        markup = None
        result_town = town_id_result[0]['caption']
        if not session.update(
            chat_id=chat_id, attr='town_id', value=str(town_id)):
            is_error = True # unknown error
        else:
            command = session._session_dist[chat_id]._command
            # TODO: перенести в CheckOutDate
            if command == '/bestdeal':
                next_step = 'min_price'
            else:
                next_step = 'results_num'
    elif len(town_id_result) > 1:
        # more then 1 result
        # TODO: сравнение результатов с первыми 64 символами
        logger.info(f'get_town_id({town_name}): generate keyboard.')
        # generate markup keyboard
        markup = ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = min(len(town_id_result), 3)
        for _i in range(markup.row_width):
            caption = town_id_result[_i]['caption'][:64]
            markup.add(caption)
            logger.debug(f'Markup: add [{caption}] to keyboard.')
    else:
        # unknown error
        logger.error(f'get_town_id({town_name}): Unknown error.')
        is_error = True     # unknown error
        markup = None
    
    logger.info((
        f'Result get_town_id: is_error={is_error}, '
        f'result_town={result_town}, '
        f'markup={markup}.'))
    return is_error, result_town, markup, next_step


def proceccing_results_num(chat_id: str, results_num: str) -> set:
    """
    Get results_num and save it in sesstion.
    Return
        user_error: bool,
        is_error: bool,
        num_results: str | None
    """
    user_error = False # not int
    is_error = False # UserQuery update error
    num_results = None
    try:
        results_num = int(results_num)

        max_results_num = int(environ.get('MAX_RESULTS'))
        if results_num == 0:
            logger.info('get_results_num is zero.')
            user_error = True
        else:
            num_results = str(min(results_num, max_results_num))
            if not session.update(chat_id, 'results_num', num_results):
                is_error = True
    except ValueError as e:
        logger.info(f'get_results_num({results_num}) error: {e}.')
        user_error = True
    
    return user_error, is_error, num_results


def proceccing_display_photos(chat_id: str, display_photos: str) -> set:
    """
    Get display_photos and save it in session.
    Return
        is_error: bool,
        display_photos: str
    """
    is_error = False
    if not session.update(chat_id, 'display_photos', display_photos):
        is_error = True
    else:
        is_error = False
    return is_error, display_photos


def process_int_values(chat_id: str, key: str, value: str) -> set:
    """
    Get min_price|max_price|min_distance|max_distance and save it in session.
    Return:
        user_error - if value not int
        is_error - if UserQuery update error.
    """
    user_error = False
    is_error = False
    try:
        int(value)
        if not session.update(chat_id, key, value):
            is_error = True
    except ValueError as e:
        logger.error(f'process_int_values({value}) error: {e}.')
        user_error = True
    
    return user_error, is_error


def get_results(chat_id: str) -> list:
    """
    Generate list of search results.
    List contains dict(keys: description, photos).
    Return empty list if error.
    """
    logger.debug(f'get_results(chat_id={chat_id}) start.')
    result = list()
    user_session = session.get_session_dict(chat_id)
    user_session_id = db.insert_session(user_session)
    # get checkIn and ckeckOut
    # TODO: get checkIn and CheckOut from session
    check_in_date = '2021-12-24'
    check_out_date = '2021-12-25'
    if not user_session_id:
        logger.debug('get_results error: no session.')
        return result
    else:
        hotels = r.get_hotels_list(user_session)
        for _hotel in hotels:
            result_dict = dict()

            hotel_dict = _hotel.dictionary
            hotel_price = _hotel.price
            hotel_id = hotel_dict['id']
            db.insert_hotel_and_search_result(
                user_session_id=user_session_id,
                hotel_dict=hotel_dict,
                price=hotel_price
            )
            # get_hotel_photos
            db_hotel_photos_list = db.get_hotel_photos(hotel_id)
            if db_hotel_photos_list:
                hotel_photos_list = list()
                for _db_photo in db_hotel_photos_list:
                    hotel_photos_list.append(_db_photo['url'])
            else:
                # no photos in database
                hotel_photos_list = r.get_hotel_photos(hotel_id)
                db.insert_hotel_photos(
                    hotel_id=hotel_id,
                    photos=hotel_photos_list
                )
            # generate hotel description dict
            hotel_dict['price'] = hotel_price
            # add checkIn and checkOut
            hotel_dict['check_in'] = check_in_date
            hotel_dict['check_out'] = check_out_date
            result_dict['description'] = hotel_dict
            if user_session['display_photos']:
                result_dict['photos'] = hotel_photos_list
            else:
                result_dict['photos'] = list()
            result.append(result_dict)
    # clear session
    session.clear(chat_id)
    logger.debug(f'get_results return {len(result)} results.')
    return result
