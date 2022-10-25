from os import getcwd, path
from dotenv import load_dotenv


def load_env(fn: str = '.env', override: bool = False) -> bool:
    """Return environment load status from fn file."""
    fn_path = path.join(getcwd(), fn)
    if not path.exists(fn_path):
        raise EnvironmentError(f'Environment file [{fn_path}] not exists.')
    return load_dotenv(fn_path, verbose=True, override=override)


if __name__ == '__main__':
    if load_env(fn='.env', override=True):
        from app.app_logger import get_logger
        logger = get_logger(__name__)
        logger.debug('Debug message.')
        logger.info('Application start.')
        logger.error('Error message.')
