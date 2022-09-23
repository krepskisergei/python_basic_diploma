from app.logger import get_logger
from classes.history import History
from db.database import Database
from app.config import DB_ENGINE


# initiate
logger = get_logger(__name__)
db = Database(DB_ENGINE)


def get_history(
        chat_id: int, create: bool = False, command: str = '', ) -> History:
    """Return existing or create History."""
    h = db.get_current_history(chat_id)
    if h is None and create:
        # create new history
        h = History(chat_id)
        if command:
            h.set_attributes({'command': command})
            db_h = db.add_history(h)
            return db_h
        logger.error('Error creating History: no command.')
    else:
        return h


def process_command(chat_id: int, command: str):
    h = get_history(chat_id, command)
    if h.current_step == 'locationId':
        print(h.command)
    else:
        print(h.id)
