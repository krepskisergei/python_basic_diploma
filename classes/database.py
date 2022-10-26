from app.app_logger import get_logger
from classes.db_connector import DBConnector
from classes.basic import (
    Location, Hotel, HotelPhoto
)


# initiate logger
logger = get_logger(__name__)


class DB(DBConnector):
    """Extendend class for application database methods."""
    # Location
    def get_location_byid(self, id: int) -> Location:
        """Return Location instance by id."""
        columns = (
            'destinationId', 'geoId', 'caption', 'name', 'name_lower'
        )
        q = (
            f"SELECT {', '.join(columns)} FROM locations"
            " WHERE destinationId = ?"
        )
        try:
            response = self._select_one(q, [id], {})
        except self.DBError:
            response = None
        if response is None:
            logger.debug('get_location_byid return None.')
            return None
        return Location(**response)

    def get_locations_byname(
            self, name: str, limit: int = 0) -> list[Location]:
        """
        Return list of Lication instances by name.
        Can be limited.
        """
        # query by name_lower
        columns = (
            'destinationId', 'geoId', 'caption', 'name', 'name_lower'
        )
        q = (
            f"SELECT {', '.join(columns)} FROM locations"
            " WHERE name_lower = ? ORDER BY destinationId"
        )
        if limit > 0:
            q += f" LIMIT {limit}"
        name_lower = name.lower().replace(' ', '').replace('-', '')
        try:
            response = self._select_all(q, [name_lower], {})
        except self.DBError:
            response = []
        if len(response) > 0:
            return [Location(**x) for x in response]
        # query by caption
        q = (
            f"SELECT {', '.join(columns)} FROM locations"
            " WHERE caption LIKE ? ORDER BY destinationId"
        )
        if limit > 0:
            q += f" LIMIT {limit}"
        caption = name.lower().title()
        try:
            response = self._select_all(q, [caption], {})
        except self.DBError:
            response = []
        if len(response) > 0:
            return [Location(**x) for x in response]
        logger.debug('get_location_byname return None.')
        return []

    def add_location(self, location: Location) -> bool:
        """Return status of adding Location instance."""
        columns = (
            'destinationId', 'geoId', 'caption', 'name', 'name_lower'
        )
        q = (
            f"INSERT INTO locations({''})"
            f" VALUES ({', '.join('?' * len(columns))})"
        )
        try:
            self._update(q, location.data)
            return True
        except self.DBUniqueError:
            return True
        except self.DBError:
            return False

    # Hotel
    def get_hotel_byid(self, id: int) -> Hotel:
        """Return Hotel instance by id."""
        columns = (
            'id', 'name', 'address', 'url', 'starRating', 'distance'
        )
        q = (
            f"SELECT {', '.join(columns)} FROM hotels"
            " WHERE id = ?"
        )
        try:
            response = self._select_one(q, [id], {})
        except self.DBError:
            response = None
        if response is None:
            logger.debug('get_hotel_byid return None.')
        return Hotel(**response)

    def add_hotel(self, hotel: Hotel) -> bool:
        """Return status of adding Hotel instance."""
        columns = (
            'id', 'name', 'address', 'url', 'starRating', 'distance'
        )
        q = (
            f"INSERT INTO hotels({', '.join(columns)}) "
            f"VALUES ({', '.join('?' * len(columns))})"
        )
        try:
            self._update(q, hotel.data)
            return True
        except self.DBUniqueError:
            return True
        except self.DBError:
            return False

    # HotelPhotos
    def get_hotel_photos(
        self, hotel_id: int,
            limit: int = 0) -> list[HotelPhoto]:
        """
        Return list of HotelPhoto instances by Hotel id.
        """
        columns = ('imageId', 'hotelId', 'baseUrl')
        q = (
            f"SELECT {', '.join(columns)} FROM photos"
            " WHERE hotelId = ? ORDER BY imageId"
        )
        if limit > 0:
            q += f" LIMIT {limit}"
        try:
            response = self._select_all(q, [hotel_id], {})
        except (self.DBError):
            response = []
        if len(response) > 0:
            return [HotelPhoto(**x) for x in response]
        logger.debug('get_hotel_photos return None.')
        return []

    def add_hotel_photos(self, photos: list[HotelPhoto]) -> bool:
        """Return status of adding HotelPhoto instances list."""
        columns = ('imageId', 'hotelId', 'baseUrl')
        values = [x for y in photos for x in y.data]
        values_placer = ', '.join(
            [f"({', '.join('?' * len(columns))})" for _ in range(len(photos))])
        q = (
            f"INSERT INTO photos({', '.join(columns)})"
            f" VALUES {values_placer}"
        )
        try:
            self._update(q, values)
            return True
        except self.DBUniqueError:
            return True
        except self.DBError:
            return False
