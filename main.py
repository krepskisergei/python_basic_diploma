# python_basic_diploma/main.py
from sys import exit

from app.environment import check_environment


# check environment
if __name__ == '__main__':
    if not check_environment():
        exit()
    else:
        # import bot after environment loaded
        from app.handlers import bot
        # starting TeleBot
        print('Bot started. Press Ctrl+C to terminate.')
        bot.polling(non_stop=True, interval=0)
