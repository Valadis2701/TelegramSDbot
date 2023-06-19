import requests
import base64
import datetime
import telebot
import repository

from repository import Result
from deep_translator import GoogleTranslator
from user_service import *
from file_utils import *
from utils import *
from user_service import *
from bot_config import *

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
    prompt = save_new_prompt_for_user(message, prepared_prompt)

    try:
        response = generate_pone(prepared_prompt, chat_id)
    except Exception as err:
        print("Can't connect to the AI engine ", err)
        bot.send_message(chat_id, "Упс. Хтось вкрав відеокарту. Не можу малювати в даний час. Якщо це повторюється часто - пиши @Kipo17")
        return

    handle_response(chat_id, response, prompt)

def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data

    if data == "cancel":
        try:
            bot.send_message(chat_id, text="Видалено! Спробуй інші теги. Опиши більш точно")
            bot.delete_message(chat_id, message_id)
            repository.mark_result_as_deleted(chat_id, message_id)
            return
        except Exception:
            print("Нам ПиЗдА!!")
            return None
    elif data == "retry":
        retry_drawing(chat_id, message_id)
    else:
        copy_image_path = copy_image(data, saved_pictures_folder_path)

        if copy_image_path:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=make_retry_image_keyboard())
            bot.send_message(chat_id, text="Картинка збережена до публiчного альбому")
            repository.mark_result_as_saved(chat_id, message_id)
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

def handle_response(chat_id, response, prompt_entity):
    if response.status_code != 200:
        bot.send_message(chat_id, text="Навiть телеграм не хоче це вiдправляти. Якщо ти бачиш це часто пиши @kipo17")
        print("AI request failed")
        return

    image_list_base64 = response.json().get("images")
    if image_list_base64 is None:
        bot.send_message(chat_id, text="Впав сервер! Пиши @kipo17 щоб подивився що не так")
        print("No responce image from AI server")
        return

    image_base64 = image_list_base64[0]
    raw_image = base64.b64decode(image_base64)

    if is_image_completely_black(raw_image):
        print("NSFW content generated")
        bot.send_photo(chat_id, nsfw_image, nsfw_content)
        return
    
    current_datetime = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    iname = str(chat_id) + "_" + current_datetime + ".jpg"
    image_path = save_image(iname, raw_image, all_images_folder_path)

    if image_path is None:
        bot.send_message(chat_id, text="Не вийшло зберегти")
        print("Couldn't save image")
        return

    # Отправляем изображение и кнопку пользователю
    responce_msg_id = None
    with open(image_path, "rb") as file:
        message = bot.send_photo(chat_id, photo=file, reply_markup=make_responce_image_keyboard(image_path))
        responce_msg_id = message.message_id

    result = Result(
        chat_id=chat_id,
        response_message_id=responce_msg_id,
        date=current_datetime,
        is_saved=False,
        is_removed=False,
        result_base64=image_base64,
        prompt_id=prompt_entity.id
    )

    repository.save_entity(result)
    print("Saved result")


def prepare_prompt(user_input, chat_id):
    translated = GoogleTranslator(source='auto', target='en').translate(user_input)
    print(str(chat_id) + "  :  " + user_input + "  ==>  " + translated)
    text = fetch_base_prompt() + translated
    return text

##### KEYBOARDS ####
def make_responce_image_keyboard(image_path):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    approve_button = telebot.types.InlineKeyboardButton(text="🔥", callback_data=image_path)
    cancel_button = telebot.types.InlineKeyboardButton(text="❌", callback_data="cancel")
    retry_button = telebot.types.InlineKeyboardButton(text="Інший варіант", callback_data="retry")
    keyboard.add(approve_button, cancel_button)
    keyboard.add(retry_button)
    return keyboard

def make_retry_image_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    retry_button = telebot.types.InlineKeyboardButton(text="Інший варіант", callback_data="retry")
    keyboard.add(retry_button)
    return keyboard

def retry_drawing(chat_id, message_id):
    previous_result = repository.get_result_by_chat_id_and_message_id(chat_id, message_id)
    if previous_result is None:
        print(f"Can't find prevoius result with id: {chat_id} and message id: {message_id}")
        bot.send_message(chat_id, "Щось пішло не так. Повідом @HalavicH")
        return
    
    prompt_entity = previous_result.prompt
    if prompt_entity is None:
        print(f"Can't get prompt for user: {chat_id} for message_id: {message_id}")
        bot.send_message(chat_id, "Щось пішло не так. Повідом @HalavicH")
        return

    print("Retrying generation for: " + prompt_entity.final_prompt)
    bot.send_message(chat_id, f"Малюю інший варіант для запиту: `{prompt_entity.original_prompt}`", parse_mode='MarkdownV2')
    # save_new_prompt_for_user(message, prepared_prompt)

    try:
        response = generate_pone(prompt_entity.final_prompt, chat_id)
    except Exception as err:
        print("Can't connect to the AI engine ", err)
        bot.send_message(chat_id, "Упс. Хтось вкрав відеокарту. Не можу малювати в даний час. Якщо це повторюється часто - пиши @Kipo17")
        return

    handle_response(chat_id, response, prompt_entity)
