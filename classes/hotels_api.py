from dataclasses import dataclass

from app.app_logger import get_logger
from classes.basic import Address, Hotel, HotelPhoto, Location, SearchResult
from classes.rapidapi import Api
from classes.user_session import UserSession

# initiate logger
logger = get_logger(__name__)


@dataclass(frozen=True)
class ApiSearchResult:
    hotel_id: int
    name: str
    address: str
    url: str
    starRating: int
    distance: str
    session_id: int
    price: float

    @property
    def hotel(self) -> Hotel:
        """Return Hotel instance."""
        return Hotel(
            hotel_id=self.id, name=self.name, address=self.address,
            url=self.url, starRating=self.starRating, distance=self.distance)

    @property
    def search_result(self) -> SearchResult:
        """Return SearchResult instance."""
        return SearchResult(
            sessionId=self.session_id, hotelId=self.hotel_id, price=self.price)


class HotelsApi(Api):
    """Extended methods for Hotels RapidApi."""
    # Parsers
    def _parse_location(self, data: dict) -> Location:
        """Parse dict data to Location instance."""
        try:
            location = Location(
                destinationId=int(data['destinationId']),
                geoId=int(data['geoId']),
                caption=data['caption'],
                name=data['name']
            )
            location._format_content()
            return location
        except (KeyError, ValueError) as e:
            raise self.ApiParseError(*e.args)

    def _parse_address(self, data: dict) -> Address:
        """Parse dict data to Address instance."""
        pass

    def _parse_hotel(self, data: dict) -> Hotel:
        """Parse dict data to Hotel instance."""
        pass

    def _parse_hotel_photos(self, data: dict) -> HotelPhoto:
        """Parse dict data to HotelPhoto instance."""
        pass

    def _parse_search_results(self, data: dict) -> SearchResult:
        """Parse dict data to SearchResult instance."""
        pass

    # Getters
    def get_locations(self, location_name: str) -> list[Location]:
        """Return Location instances list by API request results."""
        url = f'{self._base_url}/locations/v2/search'
        params = {
            'query': location_name,
            'locale': self._locale,
            'currency': self._currency
        }
        try:
            data = self._get(url, params)
        except self.ApiRequestError:
            return []
        try:
            for suggestion in data['suggestions']:
                if suggestion['group'].upper() == 'CITY_GROUP':
                    entities = suggestion['entities']
                    break
            else:
                logger.debug('get_locations return None.')
                return []
        except KeyError as e:
            logger.error('get_locations error', *e.args)
            return []
        if len(entities) == 0:
            logger.debug('get_locations return None.')
            return []
        locations = []
        for entity in entities:
            try:
                if entity['type'].upper() == 'CITY':
                    locations.append(self._parse_location(entity))
            except KeyError as e:
                logger.error('get_locations error', *e.args)
            except self.ApiParseError:
                pass
        return locations

    def get_search_results(
            self, user_session: UserSession) -> list[ApiSearchResult]:
        """Return ApiSearchResult instances list by API request result."""
        pass

    def get_hotel_photos(self, hotel_id: int) -> list[HotelPhoto]:
        """Return HotelPhoto instances list by API request result."""
        pass
