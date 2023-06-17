import requests
import base64
import datetime
import telebot
from deep_translator import GoogleTranslator
from user_service import save_new_prompt_for_user
from bot_config import bot
from user_service import get_registered_user_message
from file_utils import copy_image, fetch_base_prompt

from file_utils import fetch_negative_prompt, save_image
from utils import is_image_completely_black
from user_service import init_user_context

from utils import print_message

bot_token = "bot_token"
api_endpoint = "base_url/sdapi/v1/txt2img"
pictures_folder_path = "./pictures"
all_images_folder_path = "./all"


ADMIN_LIST = [
    455937183 # HalavicH
]

start_msg = "Привіт, я генєрю панєй. \n Ти мені промпти з тегами, я тобі всраті арти! Зверни увагу, що теги потрiбно писати українською або англiйською. Iнакше результат буде жахливим"
help_msg = "[Example](https://purplesmart.ai/item/e78ab628-1242-40d7-be0a-e7b2113cd166#:~:text=Prompt-,safe,%20%28%28derpibooru_p_95%29%29,%20fluffy%20filly%20princess%20luna,%20%5Bcute,%20smiling,%20beautiful%20eyes%5D,%20artstation,%20detailed%20light,%20soft,%20glowing%20royal%20garden,-Negative%20prompt)"
in_progress_msg = "Малюю. Це може зайняти декiлька хвилин якщо багато людей використовує бота одночас"
no_perrmission_msg = "You don't have permission to do it"
nsfw_content = "Пробачте, але президент заборонив клопати до перемоги"


global current_datetime
global formatted_datetime
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%d-%m-%Y_%H:%M:%S")


@bot.edited_message_handler(func=lambda message: True)
def your_func(message):
    print("Update: " + message.text)

@bot.message_handler(commands=['start'])
def handle_start(message):
    print_message(message)
    init_user_context(message.from_user)

    chat_id = message.chat.id
    bot.send_message(chat_id, start_msg)


@bot.message_handler(commands=['help'])
def handle_help(message):
    init_user_context(message.from_user)
    chat_id = message.chat.id
    bot.send_message(chat_id, help_msg, parse_mode='MarkdownV2')

@bot.message_handler(commands=['list_user'])
def handle_list_users(message):
    init_user_context(message.from_user)
    chat_id = message.from_user.id
    if is_admin(chat_id) == False:
        bot.send_message(chat_id, no_perrmission_msg)
        return

    # user_json = 

    bot.send_message(chat_id, get_registered_user_message())

# Message handler 
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    init_user_context(message.from_user)
    print_message(message)
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


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    callback_data = call.data

    if callback_data == "cancel":
        try:
            bot.send_message(chat_id, text="Видалено! Спробуємо ще раз?")
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
            bot.delete_message(chat_id, message_id)
            return
        except Exception:
            print("Нам ПиЗдА!!")
            return None

    # Перемещаем изображение из папки "all" в папку "pictures"
    copy_image_path = copy_image(callback_data, pictures_folder_path)

    if copy_image_path:
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        bot.send_message(chat_id, text="Картинка збережена до публiчного альбому")
    else:
        bot.send_message(chat_id, text="Помилка при збереженнi! Якщо ти бачиш це часто пиши @kipo17")


def create_inline_keyboard(image_path):
    keyboard = telebot.types.InlineKeyboardMarkup()
    approve_button = telebot.types.InlineKeyboardButton(text="🔥", callback_data=image_path)
    cancel_button = telebot.types.InlineKeyboardButton(text="❌", callback_data="cancel")
    keyboard.add(approve_button)
    keyboard.add(cancel_button)
    return keyboard
