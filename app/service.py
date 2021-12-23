# python_basic_diploma/app/service.py
"""
Contain all system functions (bussiness logic)
"""
from os import environ
from telebot.types import ReplyKeyboardMarkup
from datetime import datetime, timedelta

from app.logger import get_logger
from app.classes import Session
from app.database import db
import app.rapidapi as r
from app.dialogs import DISPLAY_PHOTOS_TRUE, DISPLAY_PHOTOS_FALSE


# initialize logger
logger = get_logger(__name__)
# create session
session = Session()


def create_session(chat_id: str, command: str) -> bool:
    """
    Create session for chat_id.
    Return True if ok, else return False.
    """
    result = session.create(chat_id, command)
    logger.debug(f'Session: {session}')
    return result


def get_check_out_min_date(chat_id: str) -> str:
    """
    Get check_in date from session and return +1 day str.
    Return empty str if no check_in.
    """
    logger.debug(f'get_check_out_min_date(chat_id={chat_id}) start.')
    try:
        check_in = session._session_dist[chat_id]._check_in
        date_check_in = datetime.strptime(check_in, '%Y-%m-%d')
        date_check_out = date_check_in + timedelta(days=1)
        result = str(date_check_out.date())
        logger.debug(f'get_checl_out_min_date return {result}.')
        return result
    except Exception as e:
        logger.error(f'get_check_out_min_date error: {e}.')
        return str()


def proceccing_town_id(chat_id: str, town_name: str) -> set:
    """
    Get town_id by town_name and save it in session.
    Return 
        is_error: bool, 
        result_town: str, 
        markup: ReplyKeyboardMarkup | None
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
    elif len(town_id_result) > 1:
        # more then 1 result
        # compare first 64 chars
        find_in_list = False
        for _town in town_id_result:
            if town_name == _town['caption'][:64]:
                # one result
                town_id = _town['destinationId']
                markup = None
                result_town = _town['caption']
                find_in_list = True
                if not session.update(
                    chat_id=chat_id, attr='town_id', value=str(town_id)):
                    is_error = True # unknown error
                break
        
        if not find_in_list:
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


def proceccing_check_in_date(chat_id: str, check_in: str) -> bool:
    """
    Get check_in and seve it in session.
    Return True if ok, else return False
    """
    return session.update(chat_id, 'check_in', check_in)


def proceccing_check_out_date(chat_id: str, check_out: str) -> set:
    """
    Get check_out and save it in session, choose next_step by command.
    Return:
        session_update: bool
        next_step: str
    """
    session_update = session.update(chat_id, 'check_out', check_out)
    command = session._session_dist[chat_id]._command
    if command == '/bestdeal':
        next_step = 'min_price'
    else:
        next_step = 'results_num'
    return session_update, next_step


def proceccing_results_num(chat_id: str, results_num: str) -> set:
    """
    Get results_num and save it in session.
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
    display_photos_set = (
        DISPLAY_PHOTOS_TRUE, DISPLAY_PHOTOS_FALSE
    )
    if display_photos in display_photos_set:
        # is displaing photos
        if display_photos == DISPLAY_PHOTOS_FALSE:
            # no display photos
            display_photos = '0'
        else:
            display_photos = ''
    # photos_num
    if len(display_photos):
        if not session.update(chat_id, 'photos_num', display_photos):
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
            # add check_in and check_out dates to hotel url
            hotel_dict['check_in'] = user_session['check_in']
            hotel_dict['check_out'] = user_session['check_out']

            result_dict['description'] = hotel_dict
            if user_session['photos_num']:
                result_dict['photos'] = hotel_photos_list[
                        :user_session['photos_num']]
            else:
                result_dict['photos'] = list()
            result.append(result_dict)
    # clear session
    session.clear(chat_id)
    logger.debug(f'get_results return {len(result)} results.')
    return result
