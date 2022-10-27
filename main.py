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

        import app.service as s
        from classes.basic import Hotel

        hotel = Hotel(
            id=1178275040,
            name='asdf',
            address='asdf',
            url='asdf',
            starRating=4,
            distance='sdf4'
        )
        photos = s.get_hotel_photos(hotel, 3)
