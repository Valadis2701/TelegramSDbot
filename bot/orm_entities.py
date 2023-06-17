from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    name = Column(String)
    chat_id = Column(Integer)
    prompts = relationship('Prompt', back_populates='user')

class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    chat_id = Column(Integer)
    message_id = Column(Integer)
    prompt = Column(String)
    date = Column(String)
    is_saved = Column(Boolean)
    is_removed = Column(Boolean)
    seed = Column(String)
    user = relationship('User', back_populates='prompts')
