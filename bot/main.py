import requests
import base64
import telebot
import os
import shutil
import datetime

print("Started")

bot_token = "5281939613:AAGHxPMQCzWQHs2A9DULc0jQMqkFCT5vv_U"
api_endpoint = "http://127.0.0.1:7861/sdapi/v1/txt2img"
pictures_folder_path = "./pictures"
all_images_folder_path = "./all"
index_file_path = "./pictures/index.txt"
prompt_file_path = "./prompt.txt"
negative_prompt_file_path = "./negativeprompt.txt"

bot = telebot.TeleBot(bot_token)


def is_image_completely_black(image_data):
    pattern = b"\x00" * 300  # Паттерн полностью черного пикселя
    consecutive_count = 0

    for i in range(len(image_data)):
        if image_data[i:i+300] == pattern:
            consecutive_count += 1
        else:
            consecutive_count = 0

        if consecutive_count >= 300:
            return True

    return False

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привіт, я генєрю панєй. /n Ти мені промпти з тегами, я тобі всраті арти!")

@bot.message_handler(commands=['help'])
def handle_help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "[Example](https://purplesmart.ai/item/e78ab628-1242-40d7-be0a-e7b2113cd166#:~:text=Prompt-,safe,%20%28%28derpibooru_p_95%29%29,%20fluffy%20filly%20princess%20luna,%20%5Bcute,%20smiling,%20beautiful%20eyes%5D,%20artstation,%20detailed%20light,%20soft,%20glowing%20royal%20garden,-Negative%20prompt)", parse_mode='MarkdownV2')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = read_prompt() + message.text

    response_msg = bot.send_message(chat_id, text="In progress...")
    message_id = response_msg.message_id

    response = requests.post(api_endpoint, json={
        "prompt": text,
        "negative_prompt": read_negative_prompt(),
        "steps": 40,
        "cfg_scale": 7.5,
        "save_images": "true",
        # "width": 512,
        # "height": 512,
        "enable_hr": "true",
        "denoising_strength": 0.7,
        "firstphase_width": 512,
        "firstphase_height": 512,
        "hr_scale": 2,
        "hr_upscaler": "R-ESRGAN 4x+",
        "hr_prompt": text,
        "hr_negative_prompt": read_negative_prompt(),
    })

    bot.delete_message(chat_id, message_id)

    if response.status_code == 200:
        images_base64 = response.json().get("images")

        if images_base64:
            image_base64 = images_base64[0]
            image_data = base64.b64decode(image_base64)

            if is_image_completely_black(image_data):
                bot.send_message(chat_id, text="NSFW!!")
            else:
            
            # Сохраняем изображение в папке "all"
                current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%d-%m-%Y_%H:%M:%S")
            iname = str(chat_id) + ":" + formatted_datetime + ".jpg"
            image_path = save_image(iname.replace(":","-"), image_data, all_images_folder_path)
            if image_path:
                # Отправляем изображение и кнопку пользователю
                with open(image_path, "rb") as file:
                    bot.send_photo(chat_id, photo=file, reply_markup=create_inline_keyboard(image_path))
            else:
                bot.send_message(chat_id, text="Failed to save the image")
        else:
            bot.send_message(chat_id, text="No image received")
    else:
        bot.send_message(chat_id, text="Error sending the request")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    image_path = call.data

    if image_path == "cancel":
        try:
            bot.send_message(chat_id, text="Removed...")
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
            bot.delete_message(chat_id, message_id)
            return 
        except Exception:
            print("Нам ПиЗдА!!")
            return None
    
    # Перемещаем изображение из папки "all" в папку "pictures"
    copy_image_path = copy_image(image_path, pictures_folder_path)

    if copy_image_path:

        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        bot.send_message(chat_id, text="Картинка сохранена успешно")
    else:
        bot.send_message(chat_id, text="Failed to move the image")

def save_image(image_name, image_data, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

 
    image_path = os.path.join(folder_path, image_name)

    try:
        with open(image_path, "wb") as file:
            file.write(image_data)
        return image_path
    except IOError:
        return None

def copy_image(image_path, destination_folder):
    try:
        image_filename = os.path.basename(image_path)
        destination_path = os.path.join(destination_folder, image_filename)
        shutil.copyfile(image_path, destination_path)
        return destination_path
    except OSError:
        return None

def get_next_image_index(folder_path):
    if os.path.exists(index_file_path):
        with open(index_file_path, "r") as file:
            lines = file.readlines()

        if lines:
            last_line = lines[-1].strip()
            last_index = int(last_line.split(":")[0])
            return last_index + 1

    return 0

def read_prompt():
    if os.path.exists(prompt_file_path):
        with open(prompt_file_path, "r") as file:
            prompt_text = file.read()
        return prompt_text
    else:
        return ""

def read_negative_prompt():
    if os.path.exists(negative_prompt_file_path):
        with open(negative_prompt_file_path, "r") as file:
            negative_prompt_text = file.read()
        return negative_prompt_text
    else:
        return ""

def create_inline_keyboard(image_path):
    keyboard = telebot.types.InlineKeyboardMarkup()
    approve_button = telebot.types.InlineKeyboardButton(text="🔥", callback_data=image_path)
    cancel_button = telebot.types.InlineKeyboardButton(text="❌", callback_data="cancel")
    keyboard.add(approve_button)
    keyboard.add(cancel_button)
    return keyboard

bot.polling()