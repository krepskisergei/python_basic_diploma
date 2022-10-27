from os import getcwd, path
from dotenv import load_dotenv


def load_env(fn: str = '.env', override: bool = False) -> bool:
    """Return environment load status from fn file."""
    fn_path = path.join(getcwd(), fn)
    if not path.exists(fn_path):
        raise EnvironmentError(f'Environment file [{fn_path}] not exists.')
    return load_dotenv(fn_path, verbose=True, override=override)


def clear_debug_log() -> None:
    fn = path.join(getcwd(), 'app_debug.log')
    if path.exists(fn):
        with open(fn, 'w'):
            pass


if __name__ == '__main__':
    if load_env(fn='.env', override=True):
        # TODO: remove debug log cleaner
        clear_debug_log()

        from app.app_logger import get_logger
        logger = get_logger(__name__)

        logger.debug('Debug.')
        logger.info('Application starts.')

        from classes.user_session import UserSession
        from classes.hotels_api import HotelsApi
        from datetime import date, datetime

        session_dict = {
            'command': '/bestdeal',
            'id': 100,
            'queryTime': datetime.now(),
            'locationId': 118894,
            'checkIn': date(2022, 12, 15),
            'checkOut': date(2022, 12, 18),
            'priceMin': 5000,
            'priceMax': 8000,
            'distanceMin': 0.5,
            'distanceMax': 1,
            'resultsNum': 5,
            'photosNum': 0
        }
        session = UserSession(1, **session_dict)
        api = HotelsApi()
        results = api.get_search_results(session)
        print(f'Found {len(results)} results:')
        for result in results:
            print('#' * 20)
            print(result.hotel)
            print('-' * 10)
            print(result.search_result)
