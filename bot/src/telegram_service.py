import requests
import base64
import datetime
import telebot
import repository

from deep_translator import GoogleTranslator
from user_service import *
from file_utils import *
from utils import *
from user_service import *
from bot_config import *

global current_datetime
global formatted_datetime
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%d-%m-%Y_%H:%M:%S")

def start_handler(message):
    init_user_context(message.from_user)

    chat_id = message.chat.id
    bot.send_message(chat_id, start_msg)

def edit_handler(message):
    pass

def help_handler(message):
    init_user_context(message.from_user)
    chat_id = message.chat.id
    bot.send_message(chat_id, help_msg, parse_mode='MarkdownV2')

def list_users_handler(message):
    init_user_context(message.from_user)
    chat_id = message.from_user.id
    if is_admin(chat_id) == False:
        bot.send_message(chat_id, no_perrmission_msg)
        return

    bot.send_message(chat_id, get_registered_user_message())

def text_handler(message):
    init_user_context(message.from_user)
    chat_id = message.chat.id
    
    original_prompt = message.text
    prepared_prompt = prepare_prompt(original_prompt, chat_id)
    save_new_prompt_for_user(message, prepared_prompt)

    try:
        response = generate_pone(prepared_prompt, chat_id)
    except Exception as err:
        print("Can't connect to the AI engine ", err)
        bot.send_message(chat_id, "Упс. Хтось вкрав відеокарту. Не можу малювати в даний час. Якщо це повторюється часто - пиши @Kipo17")
        return;

    handle_response(chat_id, response)

def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data

    if data == "cancel":
        try:
            bot.send_message(chat_id, text="Видалено! Спробуємо ще раз?")
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
            bot.delete_message(chat_id, message_id)
            return
        except Exception:
            print("Нам ПиЗдА!!")
            return None
    elif data == "retry":
        bot.send_message(chat_id, "TODO: Retrying")
        retry_drawing(chat_id, message_id)
    else:
        copy_image_path = copy_image(data, pictures_folder_path)

        if copy_image_path:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
            bot.send_message(chat_id, text="Картинка збережена до публiчного альбому")
        else:
            bot.send_message(chat_id, text="Помилка при збереженi! Якщо ти бачиш це часто пиши @kipo17")

def is_admin(id) -> bool:
    if id in ADMIN_LIST:
        return True
    else:
        return False
    

def generate_pone(prompt, chat_id):
    response_msg = bot.send_message(chat_id, text=in_progress_msg)

    response = requests.post(api_endpoint, json={
        "prompt": prompt,
        "negative_prompt": fetch_negative_prompt(),
        "steps": 30,
        "cfg_scale": 7.5,
        "save_images": "true",
        # "width": 512,
        # "height": 512,
        "enable_hr": "false",
        "denoising_strength": 0.7,
        "firstphase_width": 512,
        "firstphase_height": 512,
        "hr_scale": 2,
        "hr_upscaler": "R-ESRGAN 4x+",
        "hr_prompt": prompt,
        "hr_negative_prompt": fetch_negative_prompt(),
    })

    message_id = response_msg.message_id
    bot.delete_message(chat_id, message_id)

    return response

def handle_response(chat_id, response):
    if response.status_code == 200:
        images_base64 = response.json().get("images")

        if images_base64:
            image_base64 = images_base64[0]
            image_data = base64.b64decode(image_base64)

            if is_image_completely_black(image_data):
                bot.send_message(chat_id, text=nsfw_content)
            else:
                # Сохраняем изображение в папке "all"
                global current_datetime
                global formatted_datetime
                current_datetime = datetime.datetime.now()
                formatted_datetime = current_datetime.strftime("%d-%m-%Y_%H:%M:%S")
                iname = str(chat_id) + ":" + formatted_datetime + ".jpg"
                image_path = save_image(iname.replace(":", "-"), image_data, all_images_folder_path)
                if image_path:
                    # Отправляем изображение и кнопку пользователю
                    with open(image_path, "rb") as file:
                        bot.send_photo(chat_id, photo=file, reply_markup=create_inline_keyboard(image_path))
                else:
                    bot.send_message(chat_id, text="Щось пiшло не так..")
        else:
            bot.send_message(chat_id, text="Впав сервер! Пиши @kipo17 щоб подивився що не так")
    else:
        bot.send_message(chat_id, text="Навiть телеграм не хоче це вiдправляти. Якщо ти бачиш це часто пиши @kipo17")


def prepare_prompt(user_input, chat_id):
    translated = GoogleTranslator(source='auto', target='en').translate(user_input)
    print(str(chat_id) + "  :  " + user_input + "  ==>  " + translated)
    text = fetch_base_prompt() + translated
    return text


def create_inline_keyboard(image_path):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    approve_button = telebot.types.InlineKeyboardButton(text="🔥", callback_data=image_path)
    cancel_button = telebot.types.InlineKeyboardButton(text="❌", callback_data="cancel")
    retry_button = telebot.types.InlineKeyboardButton(text="Інший варіант", callback_data="retry")
    keyboard.add(approve_button, cancel_button)
    keyboard.add(retry_button)
    return keyboard

def retry_drawing(chat_id, message_id):
    user = repository.get_user_by_chat_id(chat_id)
    if user is None:
        print("Can't find user with id: ", chat_id)
        bot.send_message(chat_id, "Щось пішло не так. Повідом @Kipo17")
        return
    
    prompt = repository.get_prompt_by_message_id(chat_id, message_id)
    if prompt is None:
        print(f"Can't find prompt for user: {chat_id} for message_id: {message_id}")
        bot.send_message(chat_id, "Щось пішло не так. Повідом @Kipo17")
        return

    print("Retrying generation for: " + prompt.final_prompt)
    bot.send_message(chat_id, "Малюю інший варіант для запиту:", prompt.original_prompt)
    # save_new_prompt_for_user(message, prepared_prompt)

    try:
        response = generate_pone(prompt.final_prompt, chat_id)
    except Exception as err:
        print("Can't connect to the AI engine ", err)
        bot.send_message(chat_id, "Упс. Хтось вкрав відеокарту. Не можу малювати в даний час. Якщо це повторюється часто - пиши @Kipo17")
        return

    handle_response(chat_id, response)
