import telegram
from app.elements.statisticsmanager import get_env_values
import app

class TelegramBot:

    def __init__(self, telegram_token, chat_id):
        self.bot = telegram.Bot(token=telegram_token)
        self.chat_id = chat_id
        self.start_message()

    def send_msg(self, msg):
        self.bot.send_message(chat_id=self.chat_id, text=msg)

    def start_message(self):
        msg = get_env_values()
        msg += " started"
        self.send_msg(msg)
    
    def stop_message(self):
        msg = get_env_values()
        msg += " stopped"

        start_btc = app.mw.data.user.start_btc
        total = app.mw.data.current.total_btc

        btc_change_total = float(start_btc) - float(total)

        msg += " " + str(total) + " change: " + str(btc_change_total)
        self.send_msg(msg)
        