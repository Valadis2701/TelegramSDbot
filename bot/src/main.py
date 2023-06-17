from utils import *
from file_utils import *
from user_service import *
from telegram_service import *

print("Setup")
# init_bot(sys.argv[1])

bot.polling()

print("Destruction")
db_session.close()
