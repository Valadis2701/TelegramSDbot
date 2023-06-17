import os
import shutil

prompt_file_path = "./properties/prompt.txt"
negative_prompt_file_path = "./properties/negativeprompt.txt"

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


def fetch_base_prompt():
    if os.path.exists(prompt_file_path):
        with open(prompt_file_path, "r") as file:
            prompt_text = file.read()
        return prompt_text
    else:
        print("No base prompt found")
        return ""


def fetch_negative_prompt():
    if os.path.exists(negative_prompt_file_path):
        with open(negative_prompt_file_path, "r") as file:
            negative_prompt_text = file.read()
        return negative_prompt_text
    else:
        print("No negative prompt found")
        return ""

