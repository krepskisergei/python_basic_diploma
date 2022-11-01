from datetime import date, timedelta
from telebot.types import (
    ReplyKeyboardMarkup, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto)
from telegram_bot_calendar import WMonthTelegramCalendar as TCal

from app.app_logger import get_logger
from app.config import (
    API_LOCALE, API_CURRENCY, DB_ENGINE, MAX_HISTORY, MAX_RESULTS,
    MAX_PHOTOS, IMAGE_SUFFIX)

import bot.dialog as d
from classes.basic import Hotel, HotelPhoto, Location
from classes.database import DB
from classes.hotels_api import ApiSearchResult, HotelsApi
from classes.tbot import ReplyMessage
from classes.user_session import UserSession


# initiate logger
logger = get_logger(__name__)
# initiate database and api
db = DB(DB_ENGINE)
api = HotelsApi()
# fix constants
BTN_MAX = 3  # max button number in ReplyKeyboard
UNITS = {
    'price': API_CURRENCY,
    'distance': 'км'
}
CAL_IDS = {
    'check_in': 0,
    'check_out': 1
}
PHOTOS_SHOW_BTNS = {
    'да': 1,
    'нет': 0
}


# dialogs
def _get_dialog(attr_name: str, placeholder: list | tuple = None) -> str:
    """Return dialog bt attr_name formated by placeholder."""
    try:
        dialog: str = d.__getattribute__(attr_name.upper())
        if placeholder is None:
            return dialog
        return dialog.format(*placeholder)
    except AttributeError as e:
        logger.debug(f"_get_dialog error [{' '.join(map(str, *e.args))}]")
        return d.UNKNOWN_ERROR


def _display_api_search_result(
        session: UserSession, result: ApiSearchResult) -> ReplyMessage:
    """Return ReplyMessage by ApiSearchResult instance."""
    placeholder = [
        result.hotel.name, '⭐' * result.hotel.star_rating,
        result.hotel.address,
        result.hotel.distance, 'км',
        result.search_result.price, API_CURRENCY
    ]
    photos = []
    if session.photos_num > 0:
        photos = _get_hotel_photos(result.hotel, session.photos_num)
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(
        d.HOTEL_BOOK, url=result.search_result.url))
    media = None
    if len(photos) > 0:
        media = [InputMediaPhoto(
            x.formated_url(IMAGE_SUFFIX)) for x in photos]
    return ReplyMessage(
        session.chat_id, _get_dialog('HOTEL_MESSAGE', placeholder),
        markup=markup, media=media, next_handler=False)


# Api and database unify methods
def _get_locations(location_name: str, limit: int = 0) -> list[Location]:
    """Return Location instances list by database and Api responces."""
    # search in database
    locations = db.get_locations_byname(location_name, limit)
    if len(locations) > 0:
        return locations
    # search by Api
    locations = api.get_locations(location_name)
    if len(locations) == 0:
        return []
    # save locations to database
    for location in locations:
        if not db.add_location(location):
            logger.debug('_get_locations error.')
    # return locations
    if 0 < limit < len(locations):
        return locations[:limit]
    return locations


def _get_hotel_photos(hotel: Hotel, limit: int = 0) -> list[HotelPhoto]:
    """Return HotelPhoto instances list by database and Api responces."""
    # search in database
    photos = db.get_hotel_photos(hotel, limit)
    if len(photos) > 0:
        return photos
    # search by Api
    photos = api.get_hotel_photos(hotel, limit=0)
    if len(photos) == 0:
        return []
    # save hotel photos to database
    if not db.add_hotel_photos(hotel, photos):
        logger.debug('_get_hotel_photos error.')
    # return photos
    if 0 < limit < len(photos):
        return photos[:limit]
    return photos


# Session methods
def _get_session_bychatid(chat_id: int, command: str = None) -> UserSession:
    """
    Return UserSession by chat_id from database.
    Create new UserSession instance if command is None and is correct.
    """
    session = db.get_active_session(chat_id)
    if session is not None:
        return session
    # no active session in database
    if command is None:
        logger.warning(f'_get_session_bychatid error: [{chat_id} {command}]')
        return None
    session_attrs = {'command': command}
    session = UserSession(chat_id, **session_attrs)
    return db.add_session(session)


def _update_session_byvalue(
        session: UserSession, value: object) -> UserSession:
    """
    Return updated by value UserSession instance.
    Raise ValueError on update failed.
    """
    current_step = session.current_step
    attrs = {current_step: value}
    updated_attrs = session.set_attrs(attrs)
    if len(updated_attrs) == 0:
        logger.warning(f"update_session error: {session.chat_id} {str(value)}")
        raise ValueError(attrs)
    return db.update_session(session, updated_attrs)


def _finish_session(session: UserSession) -> None:
    """Finish active user session."""
    session = db.update_session(session, {'complete': True})
    if session is not None:
        logger.error(f'_finish_session error [{session}]')


def _get_results(session: UserSession) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances with results."""
    chat_id = session.chat_id
    # check is session's attributes are filled
    """
    try:
         session.__getattribute__(session.attrs.keys()[-1])
    except AttributeError:
        return [ReplyMessage(chat_id, d.UNKNOWN_ERROR, next_handler=False)]
    """
    api_search_results = api.get_search_results(session)
    if len(api_search_results) == 0:
        _finish_session(session)
        return [ReplyMessage(chat_id, d.COMPLETE_WRONG, next_handler=False)]
    replies = [ReplyMessage(chat_id, _get_dialog(
        'COMPLETE_START', [len(api_search_results)]), next_handler=False)]
    for result in api_search_results:
        # save hotel and search reslut to datebase
        result.add_session(session)
        db.add_hotel(result.hotel)
        db.add_search_result(result.search_result)
        # placeholder
        replies.append(_display_api_search_result(session, result))
    _finish_session(session)
    return replies


# skipers
def _skip_attrs(session: UserSession) -> None:
    """Fill some attributes by 0 by command."""
    skip_commands = ('/lowprice', '/highprice')
    skip_steps = {
        'price_min': 0.0,
        'price_max': 0.0,
        'distance_min': 0.0,
        'distance_max': 0.0,
    }
    if session.command in skip_commands:
        chat_id = session.chat_id
        session = _get_session_bychatid(chat_id)
        if session.current_step in skip_steps.keys():
            for _, value in skip_steps.items():
                try:
                    session = _update_session_byvalue(session, value)
                except ValueError as e:
                    logger.warning((
                        '_skip_attrs error '
                        f"[{' '.join(map(str, *e.args))}]"
                    ))


# starts
def _gen_calendar(session: UserSession) -> TCal:
    """Return TCal instance for session's current step."""
    current_step = session.current_step
    cal_id = CAL_IDS.get(current_step, None)
    if cal_id is None:
        logger.warning(f'_gen_calendar error: invalid step {current_step}.')
        return None
    min_date = date.today()
    if cal_id > 0:
        min_date = session.check_in + timedelta(days=1)
    return TCal(
        calendar_id=cal_id,
        current_date=min_date, min_date=min_date,
        locale=API_LOCALE.split('_')[0])


def _starts(session: UserSession) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances by session."""
    chat_id = session.chat_id
    session = _get_session_bychatid(chat_id)
    current_step = session.current_step
    text = _get_dialog(f'{current_step}_START')
    match current_step:
        case 'check_in' | 'check_out':
            markup, step = _gen_calendar(session).build()
            return [ReplyMessage(
                chat_id, text, markup=markup, next_handler=False)]
        case 'results_num':
            return [ReplyMessage(chat_id, _get_dialog(
                'RESULTS_NUM_START', [MAX_RESULTS]))]
        case 'photos_show':
            markup = ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
            for btn in PHOTOS_SHOW_BTNS.keys():
                markup.add(btn.title())
            return [ReplyMessage(chat_id, text, markup=markup)]
        case 'photos_num':
            return [ReplyMessage(chat_id, _get_dialog(
                'PHOTOS_NUM_START', [MAX_PHOTOS]))]
        case 'complete':
            return _get_results(session)
        case _:
            return [ReplyMessage(chat_id, text)]


# processors
def _process_main(session: UserSession, value: object) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances for photos_show."""
    chat_id = session.chat_id
    attr_name = session.current_step
    try:
        _update_session_byvalue(session, value)
        return []
    except ValueError as e:
        logger.error((
            '_process_main error '
            f"[{' '.join(map(str, *e.args))}]"))
        return [ReplyMessage(chat_id, _get_dialog(
            f'{attr_name}_WRONG'), next_handler=False)]


def _process_location_id(
        session: UserSession, message: str) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances for location_id."""
    locations = _get_locations(message, BTN_MAX)
    # check :64 symbols equals
    for location in locations:
        if location.caption[:64] == message:
            locations = [location]
            break
    chat_id = session.chat_id
    attr_name = 'location_id'
    match len(locations):
        case 0:
            # no results
            return [ReplyMessage(chat_id, _get_dialog(
                f'{attr_name}_WRONG'), next_handler=False)]
        case 1:
            # one result
            location = locations[0]
            return _process_main(session, location.destination_id)
        case _:
            # more that one result
            markup = ReplyKeyboardMarkup(
                one_time_keyboard=True, row_width=min(BTN_MAX, len(locations)))
            for location in locations:
                markup.add(location.caption[:64])
            return [ReplyMessage(
                chat_id, d.LOCATION_ID_CLARIFY, markup=markup, clarify=True)]


def _process_photos_show(
        session: UserSession, message: str) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances for photos_show."""
    chat_id = session.chat_id
    value = PHOTOS_SHOW_BTNS.get(message.lower(), None)
    match value:
        case None:
            return [ReplyMessage(
                chat_id, d.PHOTOS_SHOW_WRONG, next_handler=False)]
        case 0:
            try:
                session = _update_session_byvalue(session, bool(value))
                # update photos_num to 0
                return _process_main(session, 0)
            except ValueError as e:
                logger.error((
                    '_process_photos_show error '
                    f"[{' '.join(map(str, *e.args))}]"))
                return [ReplyMessage(
                    chat_id, d.PHOTOS_SHOW_WRONG, next_handler=False)]
        case _:
            try:
                return _process_main(session, bool(value))
            except ValueError as e:
                logger.error((
                    '_process_photos_show error '
                    f"[{' '.join(map(str, *e.args))}]"))
                return [ReplyMessage(
                    chat_id, d.PHOTOS_SHOW_WRONG, next_handler=False)]


def _process_user_message(
        session: UserSession, value: object) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances by processing data from user."""
    attr_name = session.current_step
    match attr_name:
        case 'location_id':
            reply_messages = _process_location_id(session, value)
        case 'photos_show':
            reply_messages = _process_photos_show(session, value)
        case _:
            reply_messages = _process_main(session, value)
    session = _get_session_bychatid(session.chat_id)
    _skip_attrs(session)
    return reply_messages


# main functions
def command_replies(chat_id: int, command: str) -> list[ReplyMessage]:
    """Return list of ReplyMessages by command."""
    session = _get_session_bychatid(chat_id, command)
    if session is None:
        return [ReplyMessage(chat_id, d.ERROR_CONTENT, next_handler=False)]
    command = command.replace('/', '')
    replies = [ReplyMessage(chat_id, _get_dialog(
        f'COMMAND_{command}'), next_handler=False)]
    replies += _starts(session)
    return replies


def message_replies(chat_id: int, message: str) -> list[ReplyMessage]:
    """Return list of ReplyMessages by message."""
    session = _get_session_bychatid(chat_id)
    if session is None:
        return [ReplyMessage(chat_id, d.ERROR_CONTENT, next_handler=False)]
    replies = _process_user_message(session, message)
    if len(replies) > 0:
        if replies[-1].clarify:
            return replies
    replies += _starts(session)
    return replies


def callback_replies(
        chat_id: int, callback: CallbackQuery) -> list[ReplyMessage]:
    """Return list of ReplyMessages by callback."""
    session = _get_session_bychatid(chat_id)
    if session is None:
        return [ReplyMessage(chat_id, d.ERROR_CONTENT, next_handler=False)]
    value, markup, step = _gen_calendar(session).process(callback.data)
    attr_name = session.current_step
    if not value and markup:
        # edit message
        return [ReplyMessage(
            chat_id, _get_dialog(f'{attr_name}_START'),
            markup=markup, next_handler=False,
            edit_message_id=callback.message.id, clarify=True)]
    elif value:
        replies = _process_user_message(session, value)
    else:
        logger.error(f'callback_replies error {callback}')
        replies = [ReplyMessage(chat_id, d.UNKNOWN_ERROR)]
    if len(replies) > 0:
        if replies[-1].clarify:
            return replies
    session = _get_session_bychatid(chat_id)
    replies += _starts(session)
    return replies


def get_user_history(chat_id: int) -> list[ReplyMessage]:
    """
    Return list of ReplyMessage instances with completed UserSession results.
    """
    replies = []
    for session in db.get_sessions(chat_id, MAX_HISTORY):
        min_placeholder = ''
        price_attrs = [session.price_min, session.price_max]
        distance_attrs = [session.distance_min, session.distance_max]
        if sum(price_attrs) + sum(distance_attrs) > 0:
            min_placeholder = _get_dialog(
                'USER_SESSION_FLOATS',
                price_attrs + [API_CURRENCY] + distance_attrs + ['км'])
        placeholder = [
            session.query_time.strftime('%d.%m.%Y %H:%M:%S'),
            session.command.replace('/', ''),
            db.get_location_byid(session.location_id).caption,
            session.check_in.strftime('%d.%m.%Y'),
            session.check_out.strftime('%d.%m.%Y'),
            min_placeholder,
            session.results_num,
            session.photos_num
        ]
        replies.append(ReplyMessage(chat_id, _get_dialog(
            'USER_SESSION', placeholder), next_handler=False))
        for result in db.get_search_results(session):
            hotel = db.get_hotel_byid(result.hotel_id)
            api_search_result = ApiSearchResult(
                hotel.id, hotel.name, hotel.address, hotel.star_rating,
                hotel.distance, result.price)
            api_search_result.add_session(session)
            replies.append(_display_api_search_result(
                session, api_search_result))
    return replies
