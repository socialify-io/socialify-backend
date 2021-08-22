from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import BOOLEAN, TEXT, VARCHAR, TIMESTAMP, INTEGER

UserBase = declarative_base()


class User(UserBase):
    __tablename__ = 'users'

    id = Column(INTEGER, primary_key=True)
    username = Column(TEXT, nullable=False)
    password = Column(TEXT, nullable=False)
    avatar = Column(TEXT, nullable=False)
    sids = Column(TEXT, nullable=False)

    # relationships
    devices = relationship('Device', backref='Device.userId', primaryjoin='User.id==Device.userId', lazy='dynamic')


class Device(UserBase):
    __tablename__ = 'devices'

    id = Column(INTEGER, primary_key=True)
    userId = Column(INTEGER, ForeignKey(User.id), autoincrement=True)
    appVersion = Column(TEXT, nullable=False)
    os = Column(TEXT, nullable=False)
    pubKey = Column(TEXT, nullable=False)
    fingerprint = Column(VARCHAR(40), nullable=False)
    deviceName = Column(TEXT, nullable=False)
    deviceIP = Column(VARCHAR(15), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    last_active = Column(TIMESTAMP, nullable=False)
    messageToken = Column(VARCHAR(46), nullable=True)
    status = Column(INTEGER, nullable=False)


engine = create_engine('sqlite:///db/users.db')

UserBase.metadata.create_all(engine)
