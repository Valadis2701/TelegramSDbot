from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils import pp

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    
    username = Column(String)
    name = Column(String)
    lang = Column(String)
    chat_id = Column(Integer, unique=True)

    prompts = relationship('Prompt', back_populates='user')

class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True)
    
    chat_id = Column(Integer)
    message_id = Column(Integer)
    original_prompt = Column(String)
    base_prompt = Column(String)
    negative_prompt = Column(String)
    final_prompt = Column(String)
    date = Column(String)
    seed = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='prompts')

    results = relationship('Result', back_populates='prompt')

class Result(Base):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)
    
    chat_id = Column(Integer)
    response_message_id = Column(Integer)
    date = Column(String)
    is_saved = Column(Boolean)
    is_removed = Column(Boolean)
    result_base64 = Column(String)

    prompt_id = Column(Integer, ForeignKey('prompts.id'))
    prompt = relationship('Prompt', back_populates='results')

db_session = None
print("db setup")
# Create an engine and session
engine = create_engine('sqlite:///database.db', echo=True, connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()

def get_all_users():
    users = db_session.query(User).all()
    pp(users)
    # db_session.commit()
    return users

def get_user_by_chat_id(chat_id):
    return db_session.query(User).filter_by(chat_id=chat_id).first()

def get_result_by_chat_id_and_message_id(chat_id, message_id):
    return db_session.query(Result).filter_by(chat_id=chat_id).filter_by(response_message_id=message_id).first()

def get_prompt_by_message_id(chat_id, message_id):
    return db_session.query(Prompt).filter_by(chat_id=chat_id, message_id=message_id).first()

def mark_result_as_deleted(chat_id, message_id):
    try:
        result = get_result_by_chat_id_and_message_id(chat_id, message_id)
        result.is_removed = True
        # db_session update entity
        db_session.commit()
    except Exception as err:
        print(f"Can't update entity. Err", err)
        db_session.rollback()
    

def mark_result_as_saved(chat_id, message_id):
    try:
        result = get_result_by_chat_id_and_message_id(chat_id, message_id)
        result.is_saved = True
        # db_session update entity
        db_session.commit()
    except Exception as err:
        print(f"Can't update entity. Err", err)
        db_session.rollback()
    

def save_entity(entity):
    try:
        db_session.add(entity)
        db_session.commit()
    except Exception as err:
        print(f"Can't save entity: {entity}. Err", err)
        db_session.rollback()
