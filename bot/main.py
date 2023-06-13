import requests
import base64
import telebot
import os

bot_token = "5281939613:AAGHxPMQCzWQHs2A9DULc0jQMqkFCT5vv_U"
api_endpoint = "http://127.0.0.1:7861/sdapi/v1/txt2img"
image_folder_path = "./pictures"
index_file_path = "./pictures/index.txt"
prompt_file_path = "./prompt.txt"
negative_prompt_file_path = "./negativeprompt.txt"

bot = telebot.TeleBot(bot_token)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = read_prompt() + message.text

    response = requests.post(api_endpoint, json={
        "prompt": text,
        "negative_prompt": read_negative_prompt(),
        "steps": 40,
        "cfg_scale": 7.5,
        "save_images": "true",
        "width": 512,
        "height": 512,
        "sampler_name": "Euler a"
    })

    if response.status_code == 200:
        images_base64 = response.json().get("images")

        if images_base64:
            image_base64 = images_base64[0]
            image_data = base64.b64decode(image_base64)
            image_path = save_image(image_data)

            if image_path:
                update_index_file(chat_id, image_path)

                with open(image_path, "rb") as file:
                    bot.send_photo(chat_id, photo=file)
            else:
                bot.send_message(chat_id, text="Failed to save the image")
        else:
            bot.send_message(chat_id, text="No image received")
    else:
        bot.send_message(chat_id, text="Error sending the request")

def save_image(image_data):
    if not os.path.exists(image_folder_path):
        os.makedirs(image_folder_path)

    image_index = get_next_image_index()
    image_filename = f"{image_index}.jpg"
    image_path = os.path.join(image_folder_path, image_filename)

    try:
        with open(image_path, "wb") as file:
            file.write(image_data)
        return image_path
    except IOError:
        return None

def get_next_image_index():
    if os.path.exists(index_file_path):
        with open(index_file_path, "r") as file:
            lines = file.readlines()

        if lines:
            last_line = lines[-1].strip()
            last_index = int(last_line.split(":")[0])
            return last_index + 1

    return 0

def update_index_file(chat_id, image_path):
    line = f"{chat_id}:{image_path}\n"

    with open(index_file_path, "a") as file:
        file.write(line)

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

bot.polling()
