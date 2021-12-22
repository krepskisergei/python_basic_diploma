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


def _get_stream_handler(stream_level:int=logging.INFO) -> logging.FileHandler:
    """Create stream handler."""
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(stream_level)
    stream_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    return stream_handler


def get_logger(name, stream_level:int=logging.INFO) -> logging.Logger:
    """
    Return logger for module. 
    stream_level - logging level for stream.
    Use 'get_logger(__name__)' in code.
    """
    logger = logging.getLogger(name)
    logger.setLevel(stream_level)
    logger.addHandler(_get_file_handler())
    logger.addHandler(_get_stream_handler(stream_level))
    return logger
