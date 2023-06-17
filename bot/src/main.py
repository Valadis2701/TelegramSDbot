from utils import *
from file_utils import *
from user_service import *
from telegram_controller import *
from telegram_service import *

print("Setup")

bot.polling()

print("Destruction")
db_session.close()
