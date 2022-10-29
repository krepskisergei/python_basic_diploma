from datetime import datetime, date
from telebot.types import ReplyKeyboardMarkup  # , InlineKeyboardMarkup

from app.app_logger import get_logger
from app.config import DB_ENGINE, API_CURRENCY
import bot.dialog as d
from classes.basic import Hotel, HotelPhoto, Location
from classes.database import DB
from classes.hotels_api import HotelsApi
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


# Validator
def validator(message: str, valid_class: type) -> object:
    """
    Return message in valid_class type.
    Else raise ValueError.
    """
    if isinstance(message, valid_class):
        return message
    # int
    if valid_class == int:
        message = message.replace('.', '').replace(',', '').replace(' ', '')
        return int(message)
    if valid_class == float:
        message = message.replace(',', '.').replace(' ', '')
        return float(message)
    if valid_class == date:
        return datetime.strptime(message, '%Y-%m-%d').date()
    if valid_class == datetime:
        return datetime.strptime(message, '%Y-%m-%d %H:%M:%S')
    raise ValueError('validator error', message, valid_class)


# Api and database unify methods
def get_locations(location_name: str, limit: int = 0) -> list[Location]:
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
            logger.debug('get_locations error.')
    # return locations
    if 0 < limit > len(locations):
        return locations[:limit]
    return locations


def get_hotel_photos(hotel: Hotel, limit: int = 0) -> list[HotelPhoto]:
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
        logger.debug('get_hotel_photos error.')
    # return photos
    if 0 < limit < len(photos):
        return photos[:limit]
    return photos


# Session methods
def get_session_bychatid(chat_id: int, message: str = None) -> UserSession:
    """
    Return UserSession by chat_id from database.
    Create new UserSession instance if command is None and is correct.
    """
    session = db.get_active_session(chat_id)
    if session is not None:
        return session
    # no active session in database
    if message is None:
        logger.warning(f'get_session_bychatid error: [{chat_id} {message}]')
        return None
    session_attrs = {'command': message}
    session = UserSession(chat_id, **session_attrs)
    return db.add_session(session)


def update_session(session: UserSession, message: str) -> UserSession:
    """
    Return updated by msg UserSession instance.
    Raise ValueError on update failed.
    """
    current_step = session.current_step
    valid_class = session.attrs[current_step]
    attrs = {current_step: validator(message, valid_class)}
    updated_attrs = session.set_attrs(attrs)
    if len(updated_attrs) == 0:
        logger.warning(f"update_session error: {session.chat_id} {message}")
        raise ValueError()
    return db.update_session(session, updated_attrs)


# dialogs
def get_dialog(attr_name: str, placeholder: list | tuple = None) -> str:
    """Return dialog bt attr_name formated by placeholder."""
    try:
        dialog: str = d.__getattribute__(attr_name.upper())
        if placeholder is None:
            return dialog
        return dialog.format(*placeholder)
    except AttributeError as e:
        logger.debug(f"get_dialog error [{' '.join(map(str, *e.args))}]")
        return d.UNKNOWN_ERROR


# generators
def skip_attrs(session: UserSession) -> None:
    """Fill some attributes by 0 by command."""
    skip_commands = ('/lowprice', '/highprice')
    skip_steps = {
        'price_min': 0.0,
        'price_max': 0.0,
        'distance_min': 0.0,
        'distance_max': 0.0,
    }
    if session.command in skip_commands:
        updated_attrs = session.set_attrs(skip_steps)
        if len(skip_steps) == len(updated_attrs):
            db.update_session(session, updated_attrs)


def generate_calendar(session: UserSession) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances with calendar."""
    pass


def generate_results(session: UserSession) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances by search result"""
    pass


def generate_start(session: UserSession) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances for start reply."""
    attr_name = session.current_step
    match attr_name:
        case 'check_in':
            return []
        case 'check_out':
            return []
        case 'complete':
            return generate_results(session)
        case _:
            return [
                ReplyMessage(session.chat_id, get_dialog(f'{attr_name}_START'))
            ]


# additional processors
def process_location_id(
        session: UserSession, message: str) -> ReplyMessage:
    """Return ReplyMessage instances by proceccing location_id."""
    attr_name = 'location_id'
    locations = get_locations(message, BTN_MAX)
    # check :64 symbols equals
    for location in locations:
        if location.caption[:64] == message:
            locations = [location]
            break
    # check results
    match len(locations):
        case 0:
            # no results
            return ReplyMessage(
                session.chat_id,
                text=get_dialog(f'{attr_name}_WRONG'),
                next_handler=False
            )
        case 1:
            # one result
            try:
                value = locations[0].destination_id
                session = update_session(session, str(value))
                return ReplyMessage(
                    session.chat_id,
                    text=get_dialog(
                        f'{attr_name}_COMPLETE', [locations[0].caption]),
                    next_handler=False
                    )
            except ValueError:
                return ReplyMessage(
                    session.chat_id, text=d.UNKNOWN_ERROR, next_handler=False)
        case _:
            # many results
            markup = ReplyKeyboardMarkup(one_time_keyboard=True)
            for location in locations[:BTN_MAX]:
                markup.add(location.caption[:64])
            return ReplyMessage(
                session.chat_id,
                d.LOCATION_ID_CLARIFY,
                markup=markup,
                clarify=True
            )


def process_date_or_float(session: UserSession, message: str) -> ReplyMessage:
    """Return ReplyMessage instances by proceccing dates."""
    attr_name: str = session.current_step
    try:
        session = update_session(session, message)
        placeholder = [session.__getattribute__(attr_name)]
        for name, value in UNITS.items():
            if attr_name.find(name) >= 0:
                placeholder.append(value)
        return ReplyMessage(
            session.chat_id,
            text=get_dialog(f'{attr_name}_COMPLETE', placeholder),
            next_handler=False)
    except ValueError:
        return ReplyMessage(
            session.chat_id,
            text=get_dialog(f'{attr_name}_WRONG'),
            next_handler=False
        )


# main processors
def process_command(chat_id: int, command: str) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances by command from chat_id."""
    session = get_session_bychatid(chat_id, command)
    # wrong command in message
    if session is None:
        return [ReplyMessage(chat_id, d.ERROR_CONTENT)]
    replies = [ReplyMessage(
        chat_id, get_dialog(f"COMMAND_{command.replace('/', '')}"))]
    if replies[-1].clarify:
        return replies
    replies += generate_start(session)
    return replies


def process_message(chat_id: int, message: str) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances by message from chat_id."""
    session = get_session_bychatid(chat_id, message)
    # no active session
    if session is None:
        return [ReplyMessage(chat_id, d.ERROR_CONTENT, next_handler=False)]
    replies = []
    match session.current_step:
        case 'location_id':
            replies.append(process_location_id(session, message))
        case _:
            # check_in, check_out
            # price_min, price_max
            # distance_min, distance_max
            replies.append(process_date_or_float(session, message))
            # skip attrs
            skip_attrs(session)
    # update session
    session = get_session_bychatid(chat_id)
    if replies[-1].clarify:
        return replies
    replies += generate_start(session)
    return replies
