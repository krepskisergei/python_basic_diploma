from requests import request
from requests.exceptions import RequestException
from json import loads

from app.app_logger import get_logger
from app.config import API_HOST, API_KEY, API_LOCALE, API_CURRENCY


# initiate logger
logger = get_logger(__name__)


class Api:
    """Basic class for rapidapi connections."""
    def __init__(self) -> None:
        """Initiate RapidApi connection from environment attributes."""
        self._base_url = f'https://{API_HOST}'
        self._headers = {
            'x-rapidapi-host': API_HOST,
            'x-rapidapi-key': API_KEY
        }
        self._locale = API_LOCALE
        self._currency = API_CURRENCY

    def _get(self, url: str, params: dict, method: str = 'GET') -> dict:
        """Return response result from url by method."""
        logger.debug(
            f"rapidapi _get call [{' '.join(map(str, params.values()))}]")
        try:
            response = request(
                method=method,
                url=url,
                params=params,
                headers=self._headers
            )
        except RequestException as e:
            raise self.ApiRequestError(*e.args)
        if not response.ok:
            raise self.ApiRequestError('status code', response.status_code)
        return loads(response.text)

    # Exceptions
    class _ApiError(Exception):
        """Basic exception with logging for API errors."""
        _log_level = 0
        _msg = ''

        def __init__(self, *args: object) -> None:
            if self._log_level > 0:
                msg = ''
                if args:
                    msg = ' '.join(map(str, args))
                logger.log_msg(self._log_level, f'{self._msg}: {msg}')
            super().__init__(*args)

    class ApiRequestError(_ApiError):
        """Exception for request errors."""
        _log_level = logger.ERROR
        _msg = 'Request error'

    class ApiParseError(_ApiError):
        """Exception for parse request data errors."""
        _log_level = logger.ERROR
        _msg = 'Parse error'
