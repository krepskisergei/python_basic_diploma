from dataclasses import dataclass
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from app.app_logger import get_logger
from app.config import DB_ENGINE
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
def get_session(chat_id: int, command: str = None) -> UserSession:
    """
    Return UserSession by chat_id from database.
    Create new UserSession instance if command is None and is correct.
    """
    session = db.get_active_session(chat_id)
    if session is not None:
        return session
    # no active session in database
    if command is None:
        return None
    session_attrs = {'command': command}
    session = UserSession(chat_id, **session_attrs)
    return db.add_session(session)
