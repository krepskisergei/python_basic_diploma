# python_basic_diploma/app/handlers.py
"""
Logging
"""
import logging
from os import path, getcwd


_LOG_FORMAT = f'%(asctime)s - [%(levelname)s] - %(name)s : %(message)s'


def _get_file_handler() -> logging.FileHandler:
    """Create file handler"""
    file_handler = logging.FileHandler(path.join(getcwd(), 'error.log'))
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    return file_handler


def _get_stream_handler() -> logging.FileHandler:
    """Create stream handler"""
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    return stream_handler


def get_logger(name) -> logging.Logger:
    """Return logger for module. Use 'get_logger(__name__)' in code."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_get_file_handler())
    logger.addHandler(_get_stream_handler())
    return logger
