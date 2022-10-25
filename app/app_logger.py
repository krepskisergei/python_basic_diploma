import logging
from app.config import APP_DEBUG


class _AppLogger(logging.Logger):
    """
    Instances of the Logger class represent a stream and file logging channel.
    """
    _LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    # log filenames
    _ERROR_LOG_FN = 'error.log'
    _APP_LOG_FN = 'app.log'
    _DEBUG_LOG_FN = 'app_debug.log'
    # Class variables for Exceptions
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, name: str) -> None:
        logger_level = self.INFO
        super().__init__(name, logger_level)
        if APP_DEBUG is not None:
            self.setLevel(self.DEBUG)
            stream = logging.StreamHandler()
            stream.setFormatter(logging.Formatter(self._LOG_FORMAT))
            stream.setLevel(self.DEBUG)
            self.addHandler(stream)
            self.addHandler(
                self._file_handler(self.DEBUG, self._DEBUG_LOG_FN, True))
        self.addHandler(self._file_handler(self.INFO, self._APP_LOG_FN))
        self.addHandler(self._file_handler(self.ERROR, self._ERROR_LOG_FN))

    def _file_handler(
        self, level: int, fn: str, override: bool = False
            ) -> logging.Handler:
        """Return file handler with level."""
        mode = 'a'
        if override:
            mode = 'w'
        h = logging.FileHandler(fn, mode=mode, encoding='utf-8')
        h.setFormatter(logging.Formatter(self._LOG_FORMAT))
        h.setLevel(level)
        h.set_name(fn.replace('.log', '').replace('logs', ''))
        return h

    def log_msg(self, level: int, msg: str) -> None:
        """Log msg by level."""
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


def get_logger(name: str) -> _AppLogger:
    """Return a ModuleLogger with the specified name."""
    return _AppLogger(name)
