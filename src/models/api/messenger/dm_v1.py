from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.db.documents.dm import DirectMessageDocument


class DirectMessage(BaseModel):
    id: str
    sender_id: str = Field(alias="senderId")
    receiver_id: str = Field(alias="receiverId")
    sent_at: datetime = Field(alias="sentAt")
    read_at: Optional[datetime] = Field(alias="readAt")
    deleted: bool
    text: Optional[str]

    @staticmethod
    def build(document: DirectMessageDocument) -> "DirectMessage":
        return DirectMessage(
            id=str(document.id),
            sender_id=str(document.sender_id),
            receiver_id=str(document.receiver_id),
            sent_at=document.sent_at,
            read_at=document.read_at,
            deleted=document.deleted,
            text=document.text,
        )

    class Config:
        allow_population_by_field_name = True
