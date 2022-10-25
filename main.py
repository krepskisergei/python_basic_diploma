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
        from datetime import datetime, date, timedelta

        session = UserSession(123)
        attrs = {
            'id': 1,
            'queryTime': datetime.now(),
            'command': '/bestdeal',
            'locationId': 404,
            'checkIn': date.today(),
            'checkOut': date.today() + timedelta(days=1),
            'priceMin': 0,
            'priceMax': 0,
            'distanceMin': 1.3,
            'distanceMax': 2.5,
            'resultsNum': 4,
            'photosNum': 0
        }
        session.set_attrs(attrs)
        print(session.data)
