from datetime import datetime

from mongoengine import (
    ObjectIdField,
    StringField,
    DateTimeField,
    Document,
    BooleanField,
)


class DirectMessageDocument(Document):
    sender_id: str = ObjectIdField(db_field="senderId")
    receiver_id: str = ObjectIdField(db_field="receiverId")
    sent_at: datetime = DateTimeField(db_field="sentAt")
    read_at: datetime = DateTimeField(db_field="readAt")
    deleted: bool = BooleanField()
    text: str = StringField()
    meta = {"collection": "direct-message"}
