from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from dataclasses import dataclass

from app.app_logger import get_logger


# initiate logger
logger = get_logger(__name__)


@dataclass(frozen=True)
class ReplyMessage:
    """Dataclass for reply messages."""
    chat_id: int
    edit_message_id: int = None
    text: str = None
    markup: ReplyKeyboardMarkup | InlineKeyboardMarkup = None
    media: list = None
    next_handler: bool = True


class TBot(TeleBot):
    def send_reply_message(self, replies: list[ReplyMessage]):
        for reply in replies:
            if reply.media is not None:
                # send media group
                self.send_media_group(
                    chat_id=reply.chat_id,
                    media=reply.media
                )
            if reply.edit_message_id is not None:
                # edit message
                self.edit_message_text(
                    text=reply.text,
                    chat_id=reply.chat_id,
                    message_id=reply.edit_message_id,
                    reply_markup=reply.markup
                )
            else:
                self.send_message(
                    chat_id=reply.chat_id,
                    text=reply.chat_id,
                    reply_markup=reply.markup
                )
