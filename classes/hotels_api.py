from dataclasses import dataclass

from app.app_logger import get_logger
from app.config import API_CURRENCY
from classes.basic import Address, Hotel, HotelPhoto, Location, SearchResult
from classes.rapidapi import Api
from classes.user_session import UserSession


# initiate logger
logger = get_logger(__name__)


@dataclass(frozen=False)
class ApiSearchResult:
    id: int
    name: str
    address: str
    star_rating: int
    distance: float
    price: float
    session: UserSession = None

    @property
    def hotel(self) -> Hotel:
        """Return Hotel instance."""
        return Hotel(
            id=self.id, name=self.name, address=self.address,
            star_rating=self.star_rating, distance=self.distance)

    @property
    def search_result(self) -> SearchResult:
        """Return SearchResult instance."""
        try:
            return SearchResult(
                session_id=self.session.id, hotel_id=self.id,
                url=self._url, price=self.price)
        except AttributeError as e:
            logger.error(
                f"ApiSearchResult error [{' '.join(map(str, *e.args))}]")
            return None

    @property
    def _url(self) -> str:
        """Return url"""
        try:
            return (
                f'https://www.hotels.com/ho{self.id}/'
                f'?q-check-in={str(self.session.check_in)}'
                f'&q-check-out={str(self.session.check_out)}'
                '&q-rooms=1&q-room-0-adults=1&q-room-0-children=0'
                f'&f-hotel-id={self.id}&cur={API_CURRENCY}'
            )
        except AttributeError as e:
            logger.error(
                f"ApiSearchResult error [{' '.join(map(str, *e.args))}]")
            return ''

    def add_session(self, session: UserSession) -> None:
        """Add UserSession instance to ApiSearchResult instance."""
        self.session = session


class HotelsApi(Api):
    """Extended methods for Hotels RapidApi."""
    # Parsers
    def _parse_location(self, data: dict) -> Location:
        """Parse dict data to Location instance."""
        try:
            location = Location(
                destination_id=int(data['destinationId']),
                geo_id=int(data['geoId']),
                caption=data['caption'],
                name=data['name']
            )
            location._format_content()
            return location
        except (KeyError, ValueError) as e:
            raise self.ApiParseError(*e.args, data)

    def _parse_address(self, data: dict) -> str:
        """
        Parse dict data to Address instance.
        Return full address in str.
        """
        try:
            address = Address(
                street_address=data['streetAddress'],
                extended_address=data['extendedAddress'],
                locality=data['locality'],
                region=data['region'],
                country_name=data['countryName']
            )
            return address.data
        except (KeyError, ValueError) as e:
            raise self.ApiParseError(*e.args, data)

    def _parse_landmarks(self, data: dict) -> float:
        """Parse dict data to distance from city center."""
        labels = ('?????????? ????????????', 'city center')
        units = ('????', 'km')
        try:
            for landmark in data:
                if landmark['label'].lower() in labels:
                    distance_string: str = landmark['distance']
                    break
            else:
                raise self.ApiParseError('_parse_landmarks error', data)
            distance_string = distance_string.replace(',', '.')
            for unit in units:
                distance_string = distance_string.replace(unit, '')
            return float(distance_string.strip())
        except (KeyError, ValueError) as e:
            raise self.ApiParseError(*e.args, data)

    def _parse_price(self, data: object) -> float:
        """Parse dict data to price."""
        try:
            return float(data)
        except (KeyError, ValueError) as e:
            raise self.ApiParseError(*e.args, data)

    def _parse_search_result(self, data: dict) -> ApiSearchResult:
        """Parse dict data to ApiSearchResult instance."""
        try:
            try:
                price_data = data['ratePlan']['price']['exactCurrent']
            except KeyError:
                price_data = data['price']
            return ApiSearchResult(
                id=int(data['id']),
                name=data['name'],
                address=self._parse_address(data['address']),
                star_rating=int(data['starRating']),
                distance=self._parse_landmarks(data['landmarks']),
                price=self._parse_price(price_data)
            )
        except (KeyError, ValueError) as e:
            raise self.ApiParseError(*e.args, data)

    def _parse_hotel_photos(self, data: dict) -> HotelPhoto:
        """Parse dict data to HotelPhoto instance."""
        try:
            return HotelPhoto(id=data['imageId'], url=data['baseUrl'])
        except (KeyError, ValueError) as e:
            raise self.ApiParseError(*e.args, data)

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
            logger.error(
                f"get_locations error: [{' '.join(map(str, *e.args))}]")
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
                logger.error(
                    f"get_locations error: [{' '.join(map(str, *e.args))}]")
            except self.ApiParseError:
                pass
        return locations

    def get_search_results(
            self, user_session: UserSession) -> list[ApiSearchResult]:
        """Return ApiSearchResult instances list by API request result."""
        url = f'{self._base_url}/properties/list'
        page_size = 25
        # prepare params
        params = {
            'destinationId': str(user_session.location_id),
            'pageSize': str(page_size),
            'checkIn': str(user_session.check_in),
            'checkOut': str(user_session.check_out),
            'adults1': '1',
            'locale': self._locale,
            'currency': self._currency
        }
        # add params by command
        match user_session.command:
            case '/lowprice':
                params['sortOrder'] = 'PRICE'
            case '/highprice':
                params['sortOrder'] = 'PRICE_HIGHEST_FIRST'
            case '/bestdeal':
                params['sortOrder'] = 'DISTANCE_FROM_LANDMARK'
                params['minPrice'] = int(user_session.price_min)
                params['maxPrice'] = int(user_session.price_max)
        # process requests
        page = 1
        result_counter = 0
        results = []
        while True:
            params['pageNumber'] = str(page)
            try:
                data = self._get(url, params)
            except self.ApiRequestError:
                break
            # get results
            try:
                results_num = int(
                    data['data']['body']['searchResults']['totalCount'])
                results_data = data['data']['body']['searchResults']['results']
            except KeyError as e:
                logger.error(
                    f"get_search_results error [{' '.join(map(str, *e.args))}]"
                )
                break
            # parse results
            for result_data in results_data:
                if len(results) >= user_session.results_num:
                    return results
                result_counter += 1
                try:
                    result = self._parse_search_result(result_data)
                    result.add_session(user_session)
                    if not user_session.command == '/bestdeal':
                        results.append(result)
                        continue
                    # check Hotel distance
                    if user_session.distance_min <= result.distance <= \
                        user_session.distance_max and \
                        user_session.price_min <= result.price <= \
                            user_session.price_max:
                        results.append(result)
                except self.ApiParseError:
                    pass
            page += 1
            # check last page
            if result_counter // page_size >= results_num // page_size:
                break
        return results

    def get_hotel_photos(
                self, hotel: Hotel, limit: int = 0) -> list[HotelPhoto]:
        """Return HotelPhoto instances list by API request result."""
        url = f'{self._base_url}/properties/get-hotel-photos'
        params = {'id': hotel.id}
        try:
            data = self._get(url, params)
        except self.ApiRequestError:
            return []
        hotel_photos = []
        try:
            for photo_data in data['hotelImages']:
                try:
                    hotel_photos.append(self._parse_hotel_photos(photo_data))
                except self.ApiParseError:
                    pass
                if limit > 0 and len(hotel_photos) >= limit:
                    break
        except KeyError as e:
            logger.error(
                f"get_hotel_photos error: [{' '.join(map(str, *e.args))}]")
            return []
        return hotel_photos
