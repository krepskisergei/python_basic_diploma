from app.logger import get_logger
from classes.base import Hotel, Location, Photo
from classes.history import History
from db.base import SqliteDatabase


# initiate logger
logger = get_logger(__name__)


class Database(SqliteDatabase):
    """Extension for base database class with app methods."""
    @logger.debug_func
    def get_location_by_id(self, id: int) -> Location:
        """Return Location by destinationId."""
        query = (
            'SELECT destinationId, geoId, caption, name '
            'FROM locations WHERE destinationId = ?'
        )
        try:
            location = self._select_one(query, [id], {})
        except self.DBError:
            return None
        if location is None:
            return None
        return Location(**location)

    @logger.debug_func
    def get_locations_by_name(self, name: str) -> list[Location]:
        """Return list of Locations by name."""
        # search by name
        query = (
            'SELECT destinationId, geoId, caption, name '
            'FROM locations WHERE name = ?'
        )
        try:
            locations = self._select_all(query, [name.title()], {})
        except self.DBError:
            locations = []
        if len(locations) > 0:
            return [Location(**x) for x in locations]
        # search by caption
        query = (
            'SELECT destinationId, geoId, caption, name '
            'FROM locations WHERE caption LIKE ?'
        )
        try:
            locations = self._select_all(query, [f'%{name}%'], {})
        except self.DBError:
            locations = []
        if len(locations) == 0:
            return []
        return [Location(**x) for x in locations]

    @logger.debug_func
    def add_location(self, location: Location) -> bool:
        """Add Location to database. Return status."""
        query = (
            'INSERT INTO locations('
            'destinationId, geoId, caption, name)'
            ' VALUES(?, ?, ?, ?)'
        )
        try:
            self._update(query, location.to_list())
            return True
        except self.DBError:
            return False

    @logger.debug_func
    def get_hotel_by_id(self, id: int) -> Hotel:
        """Return Hotel by id."""
        query = ('SELECT * FROM hotels WHERE id = ?')
        try:
            hotel = self._select_one(query, [id], {})
        except self.DBError:
            return None
        if hotel is None:
            return None
        return Hotel(**hotel)

    @logger.debug_func
    def add_hotel(self, hotel: Hotel) -> bool:
        """Add Hotel to database. Return status."""
        query = (
            'INSERT INTO hotels('
            'id, name, fullAddress, url, starRating, distance'
            ') VALUES (?, ?, ?, ?, ?, ?)'
        )
        try:
            self._update(query, hotel.to_list())
            return True
        except self.DBDataError:
            return False

    @logger.debug_func
    def add_photo(self, photo: Photo) -> bool:
        """Add hotel Photo to database. Return status."""
        query = (
            'INSERT INTO photos('
            'imageId, hotelId, baseUrl'
            ') VALUES (?, ?, ?)'
        )
        try:
            self._update(query, photo.to_list())
            return True
        except self.DBError:
            return False

    @logger.debug_func
    def get_hotel_photos(self, id: int) -> list[Photo]:
        """Return list of Photo by hotel id."""
        query = ('SELECT * FROM photos WHERE hotelId = ?')
        try:
            photos = self._select_all(query, [id], {})
        except self.DBError:
            photos = []
        if len(photos) == 0:
            return []
        return [Photo(**x) for x in photos]

    @logger.debug_func
    def get_current_history(self, chat_id: int) -> History:
        """Return active history by chat_id."""
        query = (
            'SELECT * FROM history '
            'WHERE chatId = ? AND complete IS FALSE'
        )
        try:
            history_data = self._select_one(query, [chat_id], {})
        except self.DBError:
            return None
        if history_data is None:
            return None
        history = History(chat_id)
        history.set_attributes(history_data)
        return history

    @logger.debug_func
    def get_all_history(self, chat_id: int) -> list[History]:
        """Return list of all user histories by chat_id."""
        query = (
            'SELECT * FROM history '
            'WHERE chatId = ? AND complete IS TRUE'
        )
        try:
            history_data = self._select_all(query, [chat_id], {})
        except self.DBError:
            return []
        if history_data is None:
            return []
        histories = []
        for data in history_data:
            history = History(chat_id)
            history.set_attributes(data)
            histories.append(history)
        return histories

    @logger.debug_func
    def add_history(self, history: History) -> History:
        """Add new history."""
        try:
            history.__getattribute__('chatId')
            history.__getattribute__('command')
        except AttributeError:
            return None
        query = (
            'INSERT INTO history(chatId, command) '
            'VALUES (?, ?)'
        )
        try:
            self._update(query, [history.chatId, history.command])
        except self.DBError:
            return None
        return self.get_current_history(history.chatId)

    @logger.debug_func
    def update_history(self, history: History, update_attrs: dict) -> History:
        """Update history data from update_attrs dict."""
        try:
            history.__getattribute__('id')
        except AttributeError:
            return None
        columns = []
        values = []
        for key, value in update_attrs.items():
            columns.append(f'{key} = ?')
            values.append(value)
        query = (
            'UPDATE history SET '
            f"{', '.join(columns)} "
            'WHERE id = ?'
        )
        values.append(history.id)
        try:
            self._update(query, values)
        except self.DBError:
            return None
        return self.get_current_history(history.chatId)
