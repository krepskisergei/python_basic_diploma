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
        from datetime import date, datetime
        import app.service as s

        command = input('Enter command: ')

        session = UserSession(100, **{'command': command})

        location_name = input('Enter location: ')

        locations = s.get_locations(location_name)

        session_dict = {
            'id': 100,
            'query_time': datetime.now(),
            'location_id': locations[0].destination_id,
            'check_in': date(2022, 12, 15),
            'check_out': date(2022, 12, 18),
            'price_min': 5000,
            'price_max': 8000,
            'distance_min': 0.5,
            'distance_max': 1,
            'results_num': 3,
            'photos_num': 0
        }
        session.set_attrs(session_dict)

        results = s.api.get_search_results(session)
        print(f'Found {len(results)} results:')
        for result in results:
            print('#' * 20)
            print(result.hotel)
            print('-' * 10)
            print(result.search_result)
        if len(results) > 0:
            photos = s.get_hotel_photos(results[0], 3)
            print('*' * 20)
            for _p in photos:
                print(_p)
