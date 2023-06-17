import traceback
import telegram_service
from bot_config import bot

def try_handle(callback, message):
    try:
        print("Trying to process callback for message from:", message.from_user.id)
        callback(message)
    except Exception as err:
        print("############ ERROR ###########")
        print("Unexpected error happened!")
        print(err)
        traceback.print_exc()
        print("##############################")
        try:
            bot.send_message(message.from_user.id, "Невідома помилка. Зконтактуй @Kipo17")
        except Exception as error:
            print("Та йоб жеж вашу мать. Навіть впасти нормально не можна. ", error)


@bot.edited_message_handler(func=lambda message: True)
def message_edit_handler(message):
    try_handle(telegram_service.edit_handler, message)

@bot.message_handler(commands=['start'])
def handle_start(message):
    try_handle(telegram_service.start_handler, message)

@bot.message_handler(commands=['help'])
def handle_help(message):
    try_handle(telegram_service.help_handler, message)

@bot.message_handler(commands=['list_user'])
def handle_list_users(message):
    try_handle(telegram_service.list_users_handler, message)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try_handle(telegram_service.text_handler, message)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try_handle(telegram_service.callback_handler, call)

