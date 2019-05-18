
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')

def main():
    updater = Updater("TOKEN", use_context=True)
    bot.send_message(chat_id=chat_id, text="I'm sorry Dave I'm afraid I can't do that.")


if __name__ == '__main__':
    main()



def simple():
    bot = telegram.Bot(token="v807697602:AAEd8XnZA9_6RtbueBBwvTGMbCkqhl8iTVU")
    bot.send_message(chat_id="97886168", text="Hi")