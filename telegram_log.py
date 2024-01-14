import logging
from telegram import ParseMode


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, bot_name, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot
        self.bot_name = bot_name

    def emit(self, record):
        log_entry = f'<b>{self.bot_name}:</b>\n{self.format(record)}'
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry, parse_mode=ParseMode.HTML)