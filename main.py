import os
from dotenv import load_dotenv


if __name__ == '__main__':
    # load secrect from .env file to env
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(dotenv_path):
        raise EnvironmentError
    else:
        load_dotenv(dotenv_path)
        
        # run Bot
        from handlers import bot
        bot.polling(non_stop=True, interval=0)
