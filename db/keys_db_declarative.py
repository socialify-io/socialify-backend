import os
import sys
from typing import Text

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql.sqltypes import TEXT
 
KeyBase = declarative_base()
 
class Key(KeyBase):
    __tablename__ = 'keys'

    id = Column(Integer, primary_key=True)
    pub_key = Column(TEXT, nullable=False)
    priv_key = Column(TEXT, nullable=False)

engine = create_engine('sqlite:///db/keys.db')

KeyBase.metadata.create_all(engine)