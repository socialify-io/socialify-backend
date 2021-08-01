import os
import sys
from typing import Text

from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql.sqltypes import TEXT, VARCHAR, TIMESTAMP, INTEGER

ErrorReportsBase = declarative_base()

class ErrorReport(ErrorReportsBase):
    __tablename__ = 'error_reports'

    id = Column(INTEGER, primary_key=True)
    errorType = Column(TEXT, nullable=True)
    errorContext = Column(TEXT, nullable=True)
    messageTitle = Column(TEXT, nullable=True)
    message = Column(TEXT, nullable=True)
    userId = Column(INTEGER, nullable=True)
    appVersion = Column(TEXT, nullable=False)
    os = Column(TEXT, nullable=False)
    deviceIP = Column(VARCHAR(15), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)


error_reports_engine = create_engine('sqlite:///db/error_reports.db')

ErrorReportsBase.metadata.create_all(error_reports_engine)
