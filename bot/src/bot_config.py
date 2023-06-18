import sys
import telebot
import os

# Config
bot_token = sys.argv[1]
api_endpoint = sys.argv[2] + "/sdapi/v1/txt2img"
saved_pictures_folder_path = "./pictures"
all_images_folder_path = "./all"
prompt_file_path = "./bot/properties/prompt.txt"
negative_prompt_file_path = "./bot/properties/negativeprompt.txt"

# Message text
start_msg = "Привіт, я генєрю панєй. \n Ти мені промпти з тегами, я тобі всраті арти! Зверни увагу, що теги потрiбно писати українською або англiйською. Iнакше результат буде жахливим"
help_msg = "[Example](https://purplesmart.ai/item/e78ab628-1242-40d7-be0a-e7b2113cd166#:~:text=Prompt-,safe,%20%28%28derpibooru_p_95%29%29,%20fluffy%20filly%20princess%20luna,%20%5Bcute,%20smiling,%20beautiful%20eyes%5D,%20artstation,%20detailed%20light,%20soft,%20glowing%20royal%20garden,-Negative%20prompt)"
in_progress_msg = "Малюю. Це може зайняти декiлька хвилин якщо багато людей використовує бота одночас"
no_perrmission_msg = "You don't have permission to do it"
nsfw_content = "Виявлено хтиву картинку! \nПробачте, але президент заборонив клопати до перемоги \nЯкщо це помилка, спробуйте ще раз або додайте тег safe/безпечний"

# Media files
nsfw_image = "https://i.kym-cdn.com/photos/images/original/000/221/809/35kamk.jpg"

# Admin list
ADMIN_LIST = [
    455937183 # HalavicH
]

# Setup
print("Bot setup")
bot = telebot.TeleBot(bot_token)


print("########## CONFIG ############")
print("\tSaved pictures path:         " + os.path.abspath(saved_pictures_folder_path))
print("\tAll pictures path:           " + os.path.abspath(all_images_folder_path))
print("\tBase prompt file path:       " + os.path.abspath(prompt_file_path))
print("\tNegative prompt file path:   " + os.path.abspath(negative_prompt_file_path))
print("\tBot token:                   " + bot_token)
print("\tAPI endpoint:                " + api_endpoint)
print("##############################\n")
