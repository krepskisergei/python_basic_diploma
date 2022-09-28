from requests import request
from requests.exceptions import RequestException
import json

from app.logger import get_logger
from app.config import API_HOST, API_KEY, API_LOCALE, API_CURRENCY
from classes.base import Location


# initiate logger
logger = get_logger(__name__)


class RapidApi:
    """Class for rapid api methods."""
    class ApiError(Exception):
        """Basic exception for api errors."""
        msg = ''

        def __init__(self, *args: object) -> None:
            attr_msg = ''
            if args:
                attr_msg = ', '.join(args)
                attr_msg = f'. {attr_msg}.'
            logger.error(f'{self.msg}{attr_msg}')
            super().__init__(*args)

    class ApiRequestError(ApiError):
        msg = 'Request error.'

    class ApiBadData(ApiError):
        msg = 'Bad data in request.'

    def __init__(self):
        """Initiate class instance."""
        self._base_url = f'https://{API_HOST}'
        self._headers = {
            'x-rapidapi-host': API_HOST,
            'x-rapidapi-key': API_KEY
        }
        self._locale = API_LOCALE
        self._currency = API_CURRENCY

    def _get_response(
            self, url: str, query: dict, method: str = 'GET') -> dict:
        """Return response for query by url."""
        try:
            response = request(
                method=method,
                url=url,
                headers=self._headers,
                params=query
            )
        except RequestException as e:
            raise self.ApiRequestError(*e.args)
        if not response.ok:
            raise self.ApiRequestError(response.status_code)
        return json.loads(response.text)

    def _parse_location(self, data: dict) -> Location:
        """Parse data from dict to Location."""
        try:
            destination_id = int(data['destinationId'])
            geo_id = int(data['geoId'])
            caption = data['caption']
            name = data['name']
            location = Location(destination_id, geo_id, caption, name)
            location.format_caption()
            return location
        except (KeyError, ValueError) as e:
            raise self.ApiBadData(*e.args)

    @logger.debug_func
    def get_locations(self, name: str) -> list[Location]:
        """Get locations by name."""
        url = f'{self._base_url}/locations/v2/search'
        query = {
            'query': name,
            'locale': self._locale,
            'currency': self._currency
        }
        try:
            data = self._get_response(url, query)
        except self.ApiError:
            return None
        try:
            for suggestion in data['suggestions']:
                if suggestion['group'].upper() == 'CITY_GROUP':
                    entities = suggestion['entities']
                    break
            else:
                return []
            if len(entities) == 0:
                return []
            locations = []
            for entity in entities:
                if entity['type'].upper() == 'CITY':
                    try:
                        locations.append(self._parse_location(entity))
                    except self.ApiBadData:
                        pass
            return locations
        except KeyError as e:
            raise self.ApiBadData(*e.args)
