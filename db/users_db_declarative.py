import os
import sys
from typing import Text

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql.sqltypes import TEXT
 
UserBase = declarative_base()
 
class User(UserBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(TEXT, nullable=False)
    password = Column(TEXT, nullable=False)

engine = create_engine('sqlite:///db/users.db')

UserBase.metadata.create_all(engine)