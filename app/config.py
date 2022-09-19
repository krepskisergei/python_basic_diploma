from os import getenv, path, getcwd
from dotenv import load_dotenv


def load_env(fn: str = '.env', override: bool = False) -> bool:
    """Return environment loading status from file fn."""
    fn_path = path.join(getcwd, fn)
    if not path.exists(fn_path):
        raise EnvironmentError(f'Environment file [{fn_path}] not exists.')
    return load_dotenv(fn_path, override=override, verbose=True)


def load_var(name: str, default_value: str = None) -> str:
    """
    Return variable by name. If not exists, return default_value.
    Else raise EnvironmentError.
    """
    value = getenv(name)
    if value is not None and len(value) > 0:
        return value
    if default_value is not None:
        return default_value
    raise EnvironmentError(f'Environment variable [{name}] value error.')


APP_DEBUG = ''
# Database
DB_ENGINE = load_var('DATABASE_ENGINE')
# Telegram
TOKEN = load_var('BOT_TOKEN')
# Api
API_HOST = load_var('API_HOST')
API_KEY = load_var('API_KEY')
API_LOCALE = load_var('API_LOCALE', 'ru_RU')
API_CURRENCY = load_var('API_CURRENCY', 'RUB')
# Bot
try:
    MAX_RESULTS = int(load_var('MAX_RESULTS', '5'))
    MAX_PHOTOS = int(load_var('MAX_PHOTOS', '5'))
except ValueError as e:
    raise EnvironmentError(str(e))
