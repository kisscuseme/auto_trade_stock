import time
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv
import os
from config import set_running, get_running
load_dotenv()
updater = None

def send_log(log_message):
    try:
        updater.bot.send_message(chat_id=os.getenv('CHAT_ID'), text=log_message)
    except Exception as ex:
        print(ex)

def run_telegram():
    try:
        global updater

        updater = Updater(token=os.getenv('TELE_TOKEN'), use_context=True)
        dispatcher = updater.dispatcher

        def start(update, context):
            context.bot.send_message(chat_id=update.effective_chat.id, text="트레이드 시작")
            set_running(True)
            send_log("트레이드 상태: " + str(get_running()))

        start_handler = CommandHandler('gt', start)
        dispatcher.add_handler(start_handler)

        def stop(update, context):
            context.bot.send_message(chat_id=update.effective_chat.id, text="트레이드 중지")
            set_running(False)
            send_log("트레이드 상태: " + str(get_running()))

        stop_handler = CommandHandler('st', stop)
        dispatcher.add_handler(stop_handler)

        updater.start_polling(poll_interval=0.5)
    except Exception as ex:
        print(ex)