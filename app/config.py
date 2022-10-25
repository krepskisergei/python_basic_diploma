from os import getenv


def load_variable(name: str, default_value: str = None) -> str:
    """
    Return environment variable value by name.
    If not exists, return default_value.
    If default_value is None raise EnvironmentError.
    """
    value = getenv(name)
    if value is not None and len(value) > 0:
        return value
    if default_value is not None:
        return default_value
    raise EnvironmentError(f'Environment variable [{name}] value error.')


APP_DEBUG = None
# Database
DB_ENGINE = load_variable('DATABASE_ENGINE')
# Telegram
TOKEN = load_variable('BOT_TOKEN')
# Api
API_HOST = load_variable('API_HOST')
API_KEY = load_variable('API_KEY')
API_LOCALE = load_variable('API_LOCALE', 'ru_RU')
API_CURRENCY = load_variable('API_CURRENCY', 'RUB')
# Bot
try:
    MAX_RESULTS = int(load_variable('MAX_RESULTS', '5'))
    MAX_PHOTOS = int(load_variable('MAX_PHOTOS', '5'))
except ValueError as e:
    raise EnvironmentError(str(e))
