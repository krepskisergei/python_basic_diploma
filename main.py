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
        from datetime import date

        session = s.get_session_bychatid(1)
        attrs = {
            'location_id': 123,
            'check_in': date(2022, 11, 1),
            'check_out': date(2022, 11, 3),
            'price_min': 0.0,
            'price_max': 0.0,
            'distance_min': 0.0,
            'distance_max': 0.0,
            'results_num': 4,
            'photos_num': 0
        }
        print(session.set_attrs(attrs))
        print(session.current_step)
