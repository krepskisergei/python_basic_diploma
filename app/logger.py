import logging
from functools import wraps
from typing import Callable

from app.config import APP_DEBUG


class _AppLogger(logging.Logger):
    """
    Instances of the Logger class represent a stream and file logging channel.
    """
    _LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    _LOG_FN = 'error.log'
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, name: str, fn_level: int, io_level: int = 0) -> None:
        """Initialize the logger with a name levels for stream and file."""
        level = min(io_level, fn_level) if io_level > 0 else fn_level
        super().__init__(name, level)
        # create additional handlers
        fn_handler = logging.FileHandler(self._LOG_FN, encoding='utf-8')
        fn_handler.setFormatter(self._LOG_FORMAT)
        fn_handler.setLevel(fn_level)
        self.addHandler(fn_handler)
        self.io_level = io_level
        if io_level:
            io_handler = logging.StreamHandler()
            io_handler.setFormatter(self._LOG_FORMAT)
            io_handler.setLevel(io_level)
            self.addHandler(io_handler)

    def log_message(self, msg: str, level: int) -> None:
        """Log message by loglevel."""
        match level:
            case self.DEBUG:
                self.debug(msg)
            case self.INFO:
                self.info(msg)
            case self.WARNING:
                self.warning(msg)
            case self.ERROR:
                self.error(msg)
            case self.CRITICAL:
                self.critical(msg)
            case _:
                self.error(f'[UNKNOWN LOG LEVEL] {msg}')

    def debug_func(self, func: Callable):
        """Decorator for logging func entry and return."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Func wrapper."""
            if self.io_level == 0:
                return func(*args, **kwargs)
            attr_list = []
            if args:
                attr_list = [str(x) for x in args]
            if kwargs:
                for _attr, _val in kwargs.items():
                    attr_list.append(f'{_attr}={_val}')
            msg = f"Function {func.__name__}({', '.join(attr_list)}) start."
            self.debug(msg)
            result = func(*args, **kwargs)
            msg = f'Function {func.__name__} return {result}.'
            self.debug(msg)
            return result
        return wrapper


def get_logger(name, fn_level: int = logging.ERROR) -> _AppLogger:
    """Return a ModuleLogger with the specified name and levels."""
    io_level = logging.DEBUG if APP_DEBUG else 0
    return _AppLogger(name, fn_level, io_level)
