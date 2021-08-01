from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.sql.sqltypes import TEXT, VARCHAR, TIMESTAMP, INTEGER

UserBase = declarative_base()


class User(UserBase):
    __tablename__ = 'users'

    id = Column(INTEGER, primary_key=True)
    username = Column(TEXT, nullable=False)
    password = Column(TEXT, nullable=False)


class Device(UserBase):
    __tablename__ = 'devices'

    id = Column(INTEGER, primary_key=True)
    userId = Column(INTEGER, nullable=False)
    appVersion = Column(TEXT, nullable=False)
    os = Column(TEXT, nullable=False)
    pubKey = Column(TEXT, nullable=False)
    fingerprint = Column(VARCHAR(40), nullable=False)
    deviceName = Column(TEXT, nullable=False)
    deviceIP = Column(VARCHAR(15), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    last_active = Column(TIMESTAMP, nullable=False)


engine = create_engine('sqlite:///db/users.db')

UserBase.metadata.create_all(engine)
