from datetime import datetime

if __name__ == '__main__':
    from app.config import load_env

    if load_env(fn='.env', override=True):
        from app.logger import get_logger
        from classes.history import History

        logger = get_logger(__name__)
        h = History(123)
        h.set_attributes({
            'id': 11,
            'command': 'test',
            'checkIn': datetime.now()
        })
        print(h.current_step)
