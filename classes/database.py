from app.app_logger import get_logger
from classes.db_connector import DBConnector
from classes.basic import Location, Hotel, HotelPhoto, SearchResult
from classes.user_session import UserSession


# initiate logger
logger = get_logger(__name__)


class DB(DBConnector):
    """Extendend class for application database methods."""
    # Location
    def get_location_byid(self, id: int) -> Location:
        """Return Location instance by id."""
        columns = (
            'destination_id', 'geo_id', 'caption', 'name', 'name_lower'
        )
        q = (
            f"SELECT {', '.join(columns)} FROM locations"
            " WHERE destination_id = ?"
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
            'destination_id', 'geo_id', 'caption', 'name', 'name_lower'
        )
        q = (
            f"SELECT {', '.join(columns)} FROM locations"
            " WHERE name_lower = ? ORDER BY destination_id"
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
            " WHERE caption LIKE ? ORDER BY destination_id"
        )
        if limit > 0:
            q += f" LIMIT {limit}"
        caption = f'%{name}%'
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
            'destination_id', 'geo_id', 'caption', 'name', 'name_lower'
        )
        q = (
            f"INSERT INTO locations({','.join(columns)})"
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
            'id', 'name', 'address', 'star_rating', 'distance'
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
            'id', 'name', 'address', 'star_rating', 'distance'
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
        self, hotel: Hotel,
            limit: int = 0) -> list[HotelPhoto]:
        """
        Return list of HotelPhoto instances by Hotel id.
        """
        columns = ('id', 'url')
        q = (
            f"SELECT {', '.join(columns)} FROM photos"
            " WHERE hotel_id = ? ORDER BY id"
        )
        if limit > 0:
            q += f" LIMIT {limit}"
        try:
            response = self._select_all(q, [hotel.id], {})
        except (self.DBError):
            response = []
        if len(response) > 0:
            return [HotelPhoto(**x) for x in response]
        logger.debug('get_hotel_photos return None.')
        return []

    def add_hotel_photos(self, hotel: Hotel, photos: list[HotelPhoto]) -> bool:
        """Return status of adding HotelPhoto instances list."""
        columns = ('id', 'url', 'hotel_id')
        values = []
        for photo in photos:
            for value in photo.data:
                values.append(value)
            values.append(hotel.id)
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

    # SearchResult
    def get_search_results(self, session: UserSession) -> list[SearchResult]:
        """Return list of SearchResult instances by UserSession.id."""
        columns = ('session_id', 'hotel_id', 'url', 'price')
        q = (
            f"SELECT {', '.join(columns)} FROM results"
            " WHERE session_id = ?"
        )
        try:
            response = self._select_all(q, [session.id], {})
        except self.DBError:
            response = None
        if len(response) > 0:
            return [SearchResult(**x) for x in response]
        logger.debug('get_search_results')
        return []

    def add_search_result(self, search_result: SearchResult) -> bool:
        """Return status of adding SearchResult instances list."""
        columns = ('session_id', 'hotel_id', 'url', 'price')
        values = [x for x in search_result.data]
        q = (
            f"INSERT INTO results({', '.join(columns)})"
            f" VALUES ({', '.join('?' * len(values))})"
        )
        try:
            self._update(q, values)
            return True
        except self.DBUniqueError:
            return True
        except self.DBError:
            return False

    # UserSession
    def get_active_session(self, chat_id: int) -> UserSession:
        """Return active UserSession instance by chat_id."""
        columns = (
            'command', 'id', 'query_time', 'location_id',
            'check_in', 'check_out', 'price_min', 'price_max',
            'distance_min', 'distance_max', 'results_num', 'photos_num'
        )
        q = (
            f"SELECT {', '.join(columns)} FROM sessions"
            " WHERE chat_id = ? AND complete IS FALSE"
        )
        try:
            response = self._select_one(q, [chat_id], {})
        except self.DBError:
            response = None
        if response is None:
            logger.debug('get_active_session return None.')
            return None
        return UserSession(chat_id, **response)

    def get_sessions(self, chat_id: int, limit: int = 0) -> list[UserSession]:
        """Return list of complete UserSession instances list by chat_id."""
        columns = (
            'command', 'id', 'query_time', 'location_id',
            'check_in', 'check_out', 'price_min', 'price_max',
            'distance_min', 'distance_max', 'results_num', 'photos_num'
        )
        q = (
            f"SELECT {', '.join(columns)} FROM sessions"
            " WHERE chat_id = ? AND complete IS TRUE"
            " ORDER BY queryTime DECS"
        )
        if limit > 0:
            q += f" LIMIT {limit}"
        try:
            response = self._select_all(q, [chat_id], {})
        except self.DBError:
            response = []
        if len(response) > 0:
            return [UserSession(chat_id, **x) for x in response]
        logger.debug('get_sessions return None.')
        return []

    def add_session(self, session: UserSession) -> UserSession:
        """Return added UserSession instance."""
        columns = ('chat_id', 'command')
        try:
            values = [session.__getattribute__(x) for x in columns]
        except AttributeError as e:
            logger.error('add_session error', session, *e.args)
            return None
        q = (
            f"INSERT INTO sessions({', '.join(columns)})"
            f" VALUES ({', '.join('?' * len(values))})"
        )
        try:
            self._update(q, values)
        except (self.DBDataError, self.DBUniqueError):
            return None
        return self.get_active_session(session.chat_id)

    def update_session(
            self, session: UserSession, attrs: dict) -> UserSession:
        """
        Update UserSession attribute values by attrs.
        Return updated UserSession instance.
        """
        try:
            id = session.id
            chat_id = session.chat_id
        except AttributeError as e:
            logger.error('update_session error', session, *e.args)
            return None
        columns = []
        values = []
        for attr, value in attrs.items():
            columns.append(f'{attr} = ?')
            values.append(value)
        values.append(id)
        q = (
            f"UPDATE sessions SET {', '.join(columns)}"
            f" WHERE id = ?"
        )
        try:
            self._update(q, values)
        except self.DBError:
            return None
        return self.get_active_session(chat_id)
