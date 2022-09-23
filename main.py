# from datetime import datetime


if __name__ == '__main__':
    from app.config import load_env

    if load_env(fn='.env', override=True):
        from app.logger import get_logger
        from bot.handlers import bot
        logger = get_logger(__name__)
        logger.info('Bot started. Ctrl+C to terminate.')
        bot.polling(non_stop=True, interval=0)
