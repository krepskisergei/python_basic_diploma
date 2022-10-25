from datetime import date, timedelta
from telebot.types import ReplyKeyboardMarkup
from telebot.types import InlineKeyboardMarkup
from telegram_bot_calendar import WMonthTelegramCalendar
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


def gen_calendar_msg(id: int, min_date: date, msg: str) -> MsgKeyboard:
    """Generate message with Calendar keyboard."""
    calendar, step = WMonthTelegramCalendar(
        calendar_id=id,
        current_date=min_date,
        min_date=min_date,
        locale='ru'
    ).build()
    return MsgKeyboard(msg, calendar)


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
                messages.append(gen_calendar_msg(
                    0, date.today(), m.CHECK_IN_START_MESSAGE))
                return (messages, None)
            return (messages, h.current_step)
        case 'checkIn':
            # process checkIn current step
            messages = []
            messages.append(process_check_in(h, message))
            if h.current_step == 'checkOut':
                min_date = h.checkIn + timedelta(days=1)
                messages.append(gen_calendar_msg(
                    1, min_date, m.CHECK_OUT_START_MESSAGE
                ))
            if h.current_step == 'checkIn':
                messages.append(gen_calendar_msg(
                    0, date.today(), m.CHECK_IN_START_MESSAGE))
            return (messages, None)
        case 'checkOut':
            # process checkOut current step
            messages = []
            messages.append(process_check_out(h, message))
            if h.current_step == 'checkOut':
                min_date = h.checkIn + timedelta(days=1)
                messages.append(gen_calendar_msg(
                    1, min_date, m.CHECK_OUT_START_MESSAGE
                ))
                return (messages, None)
            if h.current_step == 'priceMin':
                messages.append(MsgKeyboard(m.MIN_PRICE_START_MESSAGE))
            if h.current_step == 'resultsNum':
                messages.append(MsgKeyboard('Количество результатов'))
            return messages, h.current_step


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
        return MsgKeyboard(f'{m.LID_FINISH_MESSAGE}{location.caption}')
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


def process_check_in(h: History, check_in: date) -> MsgKeyboard:
    """Process check in date"""
    update_attrs = h.set_attributes(
        {'checkIn': check_in})
    if len(update_attrs) == 0:
        return MsgKeyboard(m.CHECK_IN_WRONG_MESSAGE)
    db.update_history(h, update_attrs)
    return MsgKeyboard(
        f"{m.CHECK_IN_FINISH_MESSAGE}{check_in.strftime('%d.%m.%Y')}")


def process_check_out(h: History, check_out: date) -> MsgKeyboard:
    """Process check out date."""
    update_attrs = h.set_attributes(
        {'checkOut': check_out}
    )
    if len(update_attrs) == 0:
        return MsgKeyboard(m.CHECK_OUT_WRONG_MESSAGE)
    # skip steps for /lowprice, /highprice commands
    if h.command == '/lowprice' or h.command == '/highprice':
        new_attrs = h.set_attributes({
            'priceMin': 0,
            'priceMax': 1,
            'distanceMin': 0,
            'distanceMax': 1
        })
        for _k, _v in new_attrs.items():
            if update_attrs.get(_k, None) is not None:
                update_attrs[_k] = _v
    db.update_history(h, update_attrs)
    return MsgKeyboard(
        f"{m.CHECK_OUT_FINISH_MESSAGE}{check_out.strftime('%d.%m.%Y')}")


def process_price_min(h: History, price_min: str) -> MsgKeyboard:
    """Process priceMin"""
    price_min = price_min.replace(' ', '').replace(',', '.')
    try:
        update_attrs = h.set_attributes(
            {'priceMin': float(price_min)}
        )
    except ValueError:
        return MsgKeyboard('priceMin error')
    if len(update_attrs) == 0:
        return MsgKeyboard('priceMin error')
    db.update_history(update_attrs)
    return MsgKeyboard('priceMin success')


def process_price_max(h: History, price_max: str) -> MsgKeyboard:
    """Process priceMax"""
    price_max = price_max.replace(' ', '').replace(',', '.')
    try:
        update_attrs = h.set_attributes(
            {'priceMax': float(price_max)}
        )
    except ValueError:
        return MsgKeyboard('priceMin error')
    if len(update_attrs) == 0:
        return MsgKeyboard('priceMin error')
    db.update_history(update_attrs)
    return MsgKeyboard('priceMin success')
