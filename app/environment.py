# python_basic_diploma/app/environment.py
"""Load and check environment"""
from os import path, getcwd, environ
from dotenv import load_dotenv

from app.logger import get_logger


logger = get_logger(__name__)


def _load_environment() -> bool:
    """Load environment variables from .env file. Return True if all ok, else - False."""
    dotenv_path = path.join(getcwd(), '.env')
    if not path.exists(dotenv_path) or not path.isfile(dotenv_path):
        logger.critical('File .env not found.')
        return False
    else:
        logger.info('Environment loaded.')
        load_dotenv(dotenv_path)
        return True


def check_environment() -> bool:
    """Check enviroment variables. Return True if all ok, else - False."""
    if not _load_environment():
        logger.info('Check environment skipped. Environment not loaded.')
        return False
    else:
        dotenv_path = path.join(getcwd(), '.env.example')
        if not path.exists(dotenv_path):
            logger.info('Checking environment skipped. Environment example file not found.')
            return True
        else:
            # define environment keys that must be INT
            int_keys = (
                'MAX_PHOTOS',
                'MAX_RESULTS',
            )
            result = True
            # checking environment variables for example values
            with open(dotenv_path, 'r') as f:
                for line in f: 
                    key, value = line.split('=')
                    tmp_env_key = environ.get(key.strip())
                    value = value.strip().replace('\'', '').replace('"', '')
                    if tmp_env_key == value or tmp_env_key == None:
                        logger.critical(f'Fill {key.strip()} key in .env file with real values.')
                        result = False
            # checking INT environment variables
            for key in int_keys:
                try:
                    int(environ.get(key))
                except ValueError as e:
                    logger.critical(f'Key {key} must be integer.')
                    result = False
            if result:
                logger.info('Checking environment completed.')
            return result
