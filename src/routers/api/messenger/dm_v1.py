import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Depends, Body
from mongoengine import Q

from src.db.documents.account import AccountDocument
from src.db.documents.dm import DirectMessageDocument
from src.db.documents.oauth2.token import OAuth2AccessTokenDocument
from src.exceptions import APIException
from src.models.api.messenger.dm_v1 import DirectMessage
from src.services.websocket_connection import service as connection_service
from src.services.account import AccountService
from src.services.oauth2 import OAuth2Service

router: APIRouter = APIRouter(prefix="/messenger/dm/v1", tags=["api.messenger.dm.v1"])


@router.get("")
def get_direct_messages(
    unread: bool = Query(default=False),
    interlocutor_id: str = Query(alias="interlocutorId", default=None),
    page_id: int = Query(alias="pageId", default=1),
    page_size: int = Query(alias="pageSize", ge=10, le=100, default=100),
    access_token: OAuth2AccessTokenDocument = Depends(
        OAuth2Service.get_access_token_by_header
    ),
) -> list[DirectMessage]:
    if "messenger.dm:read" not in access_token.scopes:
        raise APIException(401, "unauthorized", "No permissions")
    account: AccountDocument = AccountService.get_by_access_token(access_token)
    if interlocutor_id:
        query = Q(sender_id=account.id, receiver_id=interlocutor_id) | Q(
            sender_id=interlocutor_id, receiver_id=account.id
        )
    else:
        query = Q(receiver_id=account.id) | Q(sender_id=account.id)
    if unread:
        query = query & Q(read_at=None, receiver_id=account.id)
    direct_messages = DirectMessageDocument.objects(query)
    direct_messages.skip((page_id - 1) * page_size).limit(page_size)
    return [DirectMessage.build(direct_message) for direct_message in direct_messages]


@router.post("")
async def send_direct_message(
    receiver_id: str = Body(alias="receiverId"),
    text: str = Body(min_length=1, max_length=200),
    access_token: OAuth2AccessTokenDocument = Depends(
        OAuth2Service.get_access_token_by_header
    ),
) -> DirectMessage:
    if "messenger.dm:write" not in access_token.scopes:
        raise APIException(401, "unauthorized", "No permissions")
    account: AccountDocument = AccountService.get_by_access_token(access_token)
    receiver: AccountDocument = AccountDocument.objects(id=receiver_id).first()
    if not receiver:
        raise APIException(400, "invalid_receiver", "Invalid receiver id")
    document: DirectMessageDocument = DirectMessageDocument(
        sender_id=account.id,
        receiver_id=receiver_id,
        text=text.strip(),
        sent_at=datetime.utcnow(),
        deleted=False,
    ).save()
    direct_message: DirectMessage = DirectMessage.build(document)
    connections: list = list(
        set(
            connection_service.get_connections_by_account(receiver)
            + connection_service.get_connections_by_account(account)
        )
    )
    for connection in connections:
        await connection_service.emit(
            connection, "new_message", json.loads(direct_message.json(by_alias=True))
        )
    return direct_message


@router.post("/{direct_message_id}/read")
async def read_direct_message(
    direct_message_id: str,
    access_token: OAuth2AccessTokenDocument = Depends(
        OAuth2Service.get_access_token_by_header
    ),
):
    if "messenger.dm:read" not in access_token.scopes:
        raise APIException(401, "unauthorized", "No permissions")
    account: AccountDocument = AccountService.get_by_access_token(access_token)
    direct_message: Optional[DirectMessageDocument] = DirectMessageDocument.objects(
        id=direct_message_id, receiver_id=account.id, read_at=None
    ).first()
    if not direct_message:
        raise APIException(400, "invalid_dm", "Invalid dm id")
    direct_message.update(read_at=datetime.utcnow())
    receiver: Optional[AccountDocument] = AccountDocument.objects(
        id=direct_message.receiver_id
    ).first()
    connections: list = list(
        set(
            connection_service.get_connections_by_account(receiver)
            if receiver
            else [] + connection_service.get_connections_by_account(account)
        )
    )
    for connection in connections:
        await connection_service.emit(
            connection,
            "update_message",
            json.loads(
                DirectMessage.build(direct_message.reload()).json(by_alias=True)
            ),
        )


@router.delete("/{direct_message_id}")
async def delete_direct_message(
    direct_message_id: str,
    access_token: OAuth2AccessTokenDocument = Depends(
        OAuth2Service.get_access_token_by_header
    ),
):
    if "messenger.dm:delete" not in access_token.scopes:
        raise APIException(401, "unauthorized", "No permissions")
    account: AccountDocument = AccountService.get_by_access_token(access_token)
    direct_message: Optional[DirectMessageDocument] = DirectMessageDocument.objects(
        id=direct_message_id, sender_id=account.id, deleted=False
    ).first()
    if not direct_message:
        raise APIException(400, "invalid_dm", "Invalid dm id")
    direct_message.update(text=None, deleted=True)
    receiver: AccountDocument = AccountDocument.objects(
        id=direct_message.receiver_id
    ).first()
    connections: list = list(
        set(
            connection_service.get_connections_by_account(receiver)
            if receiver
            else [] + connection_service.get_connections_by_account(account)
        )
    )
    for connection in connections:
        await connection_service.emit(
            connection,
            "update_message",
            json.loads(
                DirectMessage.build(direct_message.reload()).json(by_alias=True)
            ),
        )
