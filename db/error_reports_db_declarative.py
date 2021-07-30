import os
import sys
from typing import Text

from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql.sqltypes import TEXT, VARCHAR, TIMESTAMP, INTEGER

UserBase = declarative_base()


class Device(UserBase):
    __tablename__ = 'error_reports'

    id = Column(INTEGER, primary_key=True)
    userId = Column(INTEGER, nullable=False)
    appVersion = Column(TEXT, nullable=False)
    os = Column(TEXT, nullable=False)
    deviceName = Column(TEXT, nullable=False)
    deviceIP = Column(VARCHAR(15), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)


engine = create_engine('sqlite:///db/error_reports.db')

UserBase.metadata.create_all(engine)
