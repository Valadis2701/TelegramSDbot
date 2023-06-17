from utils import *
from file_utils import *
from user_service import *
from telegram_controller import *
from telegram_service import *

print("Setup")
# init_bot(bot_token, path_to_db)

bot.polling()

print("Destruction")
db_session.close()
