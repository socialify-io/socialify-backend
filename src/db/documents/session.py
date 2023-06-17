from datetime import datetime

from mongoengine import Document, ObjectIdField, StringField, DateTimeField


class SessionDocument(Document):
    id = StringField(db_filed="_id", primary_key=True)
    ip_address: str = StringField(db_field="ipAddress")
    user_agent: str = StringField(db_field="userAgent")
    account_id: str = ObjectIdField(db_field="accountId")
    created_at: datetime = DateTimeField(db_field="createdAt")
    expire_at: datetime = DateTimeField(db_field="expireAt")
    last_validation_date: datetime = DateTimeField(db_field="lastValidationDate")
    last_active_date: datetime = DateTimeField(db_field="lastActiveDate")
