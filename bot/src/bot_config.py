import telebot
import os

# Config
bot_token = "1247537040:AAFa0NAtFcTXEa4PGQerTbQo7QfQ2bQw3G0"
api_endpoint = "http://217.77.221.234:7860/sdapi/v1/txt2img"
saved_pictures_folder_path = "./pictures"
all_images_folder_path = "./all"
prompt_file_path = "./bot/properties/prompt.txt"
negative_prompt_file_path = "./bot/properties/negativeprompt.txt"

# Message text
start_msg = "Привіт, я генєрю панєй. \n Ти мені промпти з тегами, я тобі всраті арти! Зверни увагу, що теги потрiбно писати українською або англiйською. Iнакше результат буде жахливим"
help_msg = "[Example](https://purplesmart.ai/item/e78ab628-1242-40d7-be0a-e7b2113cd166#:~:text=Prompt-,safe,%20%28%28derpibooru_p_95%29%29,%20fluffy%20filly%20princess%20luna,%20%5Bcute,%20smiling,%20beautiful%20eyes%5D,%20artstation,%20detailed%20light,%20soft,%20glowing%20royal%20garden,-Negative%20prompt)"
in_progress_msg = "Малюю. Це може зайняти декiлька хвилин якщо багато людей використовує бота одночас"
no_perrmission_msg = "You don't have permission to do it"
nsfw_content = "Пробачте, але президент заборонив клопати до перемоги"

# Admin list
ADMIN_LIST = [
    455937183 # HalavicH
]

# Setup
print("Bot setup")
bot = telebot.TeleBot(bot_token)


print("########## CONFIG ############")
print("Saved pictures path: " + os.path.abspath(saved_pictures_folder_path))
print("All pictures path: " + os.path.abspath(all_images_folder_path))