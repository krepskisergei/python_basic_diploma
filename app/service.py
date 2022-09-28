from datetime import datetime, timedelta
from telebot.types import ReplyKeyboardMarkup
from telebot.types import InlineKeyboardMarkup
from telegram_bot_calendar import WMonthTelegramCalendar
from telegram_bot_calendar import LSTEP
from dataclasses import dataclass

from app.logger import get_logger
from classes.history import History
from db.database import Database
from api.rapidapi import RapidApi
from app.config import DB_ENGINE
import bot.messages as m


@dataclass(frozen=True)
class MsgKeyboard:
    msg: str
    markup: ReplyKeyboardMarkup | InlineKeyboardMarkup = None


# initiate
logger = get_logger(__name__)
db = Database(DB_ENGINE)
api = RapidApi()


def get_history(chat_id: int, command: str = None) -> History:
    """Return existing or create History."""
    h = db.get_current_history(chat_id)
    if h is None and command:
        # create new history
        h = History(chat_id)
        h.set_attributes({'command': command})
        return db.add_history(h)
    else:
        return h


def process_command(
        chat_id: int, message: str = None) -> tuple[list[MsgKeyboard], str]:
    """Process user message. Return MsgKeyboard list and next handler."""
    commands = (
        '/lowprice',
        '/highprice',
        '/bestdeal'
    )
    command = message if message in commands else False
    h = get_history(chat_id, command)
    if h is None:
        return ([MsgKeyboard(m.BAD_CONTENT_MESSAGE)], None)
    match h.current_step:
        case 'locationId':
            if command:
                messages = []
                match command:
                    case '/lowprice':
                        messages.append(MsgKeyboard(m.LOWPRICE_MESSAGE))
                    case '/highprice':
                        messages.append(MsgKeyboard(m.HIGHPRICE_MESSSAGE))
                    case '/bestdeal':
                        messages.append(MsgKeyboard(m.BESTDEAL_MESSAGE))
                messages.append(MsgKeyboard(m.LID_START_MESSAGE))
                return (messages, h.current_step)
            # get town
            messages = []
            messages.append(process_location_id(h, message))
            if h.current_step == 'checkIn':
                min_date = datetime.now().date()
                calendar, step = WMonthTelegramCalendar(
                    calendar_id=0,
                    current_date=min_date,
                    min_date=min_date,
                    locale='ru'
                ).build()
                messages.append(
                    MsgKeyboard(
                        f'{m.CHECK_IN_START_MESSAGE} {LSTEP[step]}',
                        markup=calendar))
                return (messages, None)
            return (messages, h.current_step)
        case 'checkIn':
            messages = []
            messages.append(process_check_in(h, message))
            if h.current_step == 'checkOut':
                min_date = (h.checkIn + timedelta(days=1)).date()
                calendar, step = WMonthTelegramCalendar(
                    calendar_id=1,
                    current_date=min_date,
                    min_date=min_date,
                    locale='ru'
                ).build()
                messages.append(
                    MsgKeyboard(
                        f'{m.CHECK_IN_START_MESSAGE} {LSTEP[step]}',
                        markup=calendar))
                return (messages, None)
            return (messages, h.current_step)
        case 'checkOut':
            pass


def process_location_id(h: History, location_name: str) -> MsgKeyboard:
    # get town from db
    locations_list = db.get_locations_by_name(location_name)
    if len(locations_list) == 0:
        # get town from api
        try:
            locations_list = api.get_locations(location_name)
            # add locations to db
            for location in locations_list:
                if not db.add_location(location):
                    logger.error('Error adding location to db.')
        except api.ApiError:
            locations_list = []
    if len(locations_list) == 0:
        # no town
        return MsgKeyboard(m.LID_WRONG_MESSAGE)
    if len(locations_list) == 1:
        # one result
        location = locations_list[0]
        update_attrs = h.set_attributes(
            {'locationId': location.destinationId})
        db.update_history(h, update_attrs)
        return MsgKeyboard(f'{m.LID_FINISH_MESSAGE}{location.name}')
    else:
        # more than one result
        for location in locations_list:
            if location.caption[:64] == location_name:
                # one result
                update_attrs = h.set_attributes(
                    {'locationId': location.destinationId})
                db.update_history(h, update_attrs)
                return MsgKeyboard(f'{m.LID_FINISH_MESSAGE}{location.name}')
        markup = ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = min(3, len(locations_list))
        for _i in range(markup.row_width):
            caption = locations_list[_i].caption[:64]
            markup.add(caption)
        return MsgKeyboard(m.LID_ASK_MESSAGE, markup)


def process_check_in(h: History, check_in) -> MsgKeyboard:
    """Process check in date"""
    dt = datetime(year=check_in.year, month=check_in.month, day=check_in.day)
    update_attrs = h.set_attributes(
        {'checkIn': dt})
    db.update_history(h, update_attrs)
    return MsgKeyboard(f"{m.CHECK_IN_FINISH_MESSAGE}{dt.strftime('%d.%m.%Y')}")
