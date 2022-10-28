from dataclasses import dataclass
from datetime import datetime, date
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from app.app_logger import get_logger
from app.config import DB_ENGINE
import bot.dialog as d
from classes.basic import Hotel, HotelPhoto, Location
from classes.database import DB
from classes.hotels_api import HotelsApi
from classes.user_session import UserSession


# initiate logger
logger = get_logger(__name__)
# initiate database and api
db = DB(DB_ENGINE)
api = HotelsApi()


# Classes
@dataclass(frozen=True)
class ReplyMessage:
    """Dataclass for reply messages."""
    chat_id: int
    edit: bool = False
    text: str = None
    markup: ReplyKeyboardMarkup | InlineKeyboardMarkup = None
    media: list = None


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


# processors
def process_location_id(
        session: UserSession, message: str) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances by proceccing location id."""
    attr_name = 'location_id'
    locations = get_locations(message, 3)
    if len(locations) == 0:
        try:
            text = d.__getattribute__(attr_name)
        except AttributeError:
            pass
        return [ReplyMessage(chat_id=session.chat_id, text=text)]


def process_message(chat_id: int, message: str) -> list[ReplyMessage]:
    """Return list of ReplyMessage instances by message from chat_id."""
    session = get_session_bychatid(chat_id, message)
    # no active session and wrong command in message
    if session is None:
        return [ReplyMessage(chat_id=chat_id, text='Нах')]
