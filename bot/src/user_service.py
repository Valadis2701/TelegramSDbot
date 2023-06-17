import datetime
import repository
from file_utils import fetch_base_prompt, fetch_negative_prompt
from utils import pp
# from telebot import User
from repository import User, db_session, get_all_users, Prompt


def init_user_context(from_user):
    new_user = User(username=from_user.username,
                    name=from_user.full_name,
                    chat_id=from_user.id,
                    lang=from_user.language_code)
    
    user = repository.get_user_by_chat_id(from_user.id)

    if user is not None:
        print(f"User {user.name}:{user.chat_id} already initialized.")
        
        # # update with new fields if needed
        # print(" Updating with new data")
        # session.update(user)
        return

    print("Storing new user:")
    pp(new_user)

    try:
        db_session.add(new_user)
        db_session.commit()
    except Exception as err:
        print("Can't add new user: ", err)
        db_session.rollback()


def get_registered_user_message():
    users = get_all_users()
    message = []
    for u in users:
        user_msg = f"User: {u.id}\n" 
        user_msg += f"    chat id: {u.chat_id}\n    name: {u.name}\n    username: {u.username}\n    lang: {u.lang}\n    prompts: {u.prompts}"
        message.append(user_msg)

    return message

def save_new_prompt_for_user(message, prepared_prompt):
    current_user = db_session.query(User).filter_by(chat_id=message.from_user.id).first()

    prompt = Prompt(chat_id=current_user.chat_id,
                    message_id=message.message_id,
                    original_prompt=message.text,
                    base_prompt=fetch_base_prompt(),
                    negative_prompt=fetch_negative_prompt(),
                    final_prompt=prepared_prompt,
                    date=datetime.datetime.now(),
                    seed=None,
                    user_id=current_user.id)
    
    try:
        db_session.add(prompt)
        db_session.commit()
    except Exception as err:
        print("Can't add new prompt: ", err)
        db_session.rollback()

    return db_session.query(Prompt).filter_by(chat_id=message.from_user.id).filter_by(message_id=message.message_id).first()
