import os
import sys
from typing import Text

from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql.sqltypes import TEXT, VARCHAR, TIMESTAMP, INTEGER

ErrorBase = declarative_base()


class ErrorReport(ErrorBase):
    __tablename__ = 'error_reports'

    id = Column(INTEGER, primary_key=True)
    message = Column(VARCHAR(150), nullable=False)
    userId = Column(INTEGER, nullable=False)
    appVersion = Column(TEXT, nullable=False)
    os = Column(TEXT, nullable=False)
    deviceName = Column(TEXT, nullable=False)
    deviceIP = Column(VARCHAR(15), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)


engine = create_engine('sqlite:///db/error_reports.db')

ErrorBase.metadata.create_all(engine)
