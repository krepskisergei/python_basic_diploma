from app.app_logger import get_logger
from app.config import DB_ENGINE
from classes.basic import Hotel, HotelPhoto, Location
from classes.database import DB
from classes.hotels_api import HotelsApi


# initiate logger
logger = get_logger(__name__)
# initiate database and api
db = DB(DB_ENGINE)
api = HotelsApi()


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
    if limit > 0 and limit > len(locations):
        return locations[:limit]
    return locations


def get_hotel_photos(hotel: Hotel, limit: int = 0) -> list[HotelPhoto]:
    """Return HotelPhoto instances list by database and Api responces."""
    # search in database
    photos = db.get_hotel_photos(hotel.id, limit)
    if len(photos) > 0:
        return photos
    # search by Api
    photos = api.get_hotel_photos(hotel.id)
    if len(photos) == 0:
        return []
    # save hotel photos to database
    if not db.add_hotel_photos():
        logger.debug('get_hotel_photos error.')
    # return photos
    if limit > 0 and limit > len(photos):
        return photos[:limit]
    return photos
