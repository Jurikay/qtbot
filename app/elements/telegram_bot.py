import telegram
from app.elements.statisticsmanager import get_env_values
import app
from app.helpers import round_decimals



class TelegramBot:

    def __init__(self, telegram_token, chat_id):
        self.mw = app.mw
        self.bot = telegram.Bot(token=telegram_token)
        self.chat_id = chat_id
        self.start_message()
        

    def send_msg(self, msg):
        self.bot.send_message(chat_id=self.chat_id, text=msg)

    def start_message(self):
        msg = get_env_values()
        msg += " version: " + self.mw.version
        msg += " started"
        self.send_msg(msg)

    def stop_message(self):
        msg = get_env_values()
        msg += " stopped"

        start_btc = app.mw.data.user.start_btc
        total = app.mw.data.current.total_btc

        try:
            btc_change_total = round_decimals(float(start_btc) - float(total), 8)
        except TypeError:
            btc_change_total = 0

        msg += "\nacc value: " + str(total) \
             + "\nchange: " + str(btc_change_total) \
             + "\n" + "time running: " + self.mw.session_running.text() \
             + "\ntotal runtime: " + self.mw.total_running.text() \
             + "\nsession trades: " + self.mw.session_trades.text()


        self.send_msg(msg)
        