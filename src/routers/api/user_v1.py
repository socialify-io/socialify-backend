from typing import Optional

from fastapi import APIRouter, Depends, Response, Query

from src.db.documents.account import AccountDocument
from src.db.documents.oauth2.token import OAuth2AccessTokenDocument
from src.exceptions import APIException
from src.models.api.user_v1 import User
from src.services.account import AccountService
from src.services.oauth2 import OAuth2Service

router: APIRouter = APIRouter(prefix="/user/v1", tags=["api.user.v1"])


@router.get("/me")
def get_my_user_data(
    access_token: OAuth2AccessTokenDocument = Depends(
        OAuth2Service.get_access_token_by_header
    ),
) -> User:
    if "user:read" not in access_token.scopes:
        raise APIException(401, "unauthorized", "No permissions")
    account: AccountDocument = AccountService.get_by_access_token(access_token)
    return User.build(account)

@router.get("/me/avatar")
def get_my_avatar(
    access_token: OAuth2AccessTokenDocument = Depends(
        OAuth2Service.get_access_token_by_header
    ),
):
    if "user:read" not in access_token.scopes:
        raise APIException(401, "unauthorized", "No permissions")
    account: AccountDocument = AccountService.get_by_access_token(access_token)
    if not bool(account.avatar):
        raise APIException(400, "user_without_avatar", "The user has not avatar")
    return Response(account.avatar.read(), media_type=account.avatar.content_type)


@router.get("/{user_id}")
def get_user_by_id(
    user_id: str,
    access_token: OAuth2AccessTokenDocument = Depends(
        OAuth2Service.get_access_token_by_header
    ),
) -> User:
    user: Optional[AccountDocument] = AccountDocument.objects(id=user_id).first()
    if not user:
        raise APIException(400, "invalid_user", "Invalid user id")
    return User.build(user)


@router.get("/{user_id}/avatar")
def get_user_avatar_by_id(
    user_id: str,
    access_token: OAuth2AccessTokenDocument = Depends(
        OAuth2Service.get_access_token_by_header
    ),
):
    user: Optional[AccountDocument] = AccountDocument.objects(id=user_id).first()
    if not bool(user.avatar):
        raise APIException(400, "user_without_avatar", "The user has not avatar")
    return Response(user.avatar.read(), media_type=user.avatar.content_type)


@router.get("")
def search_user(query: str = Query(min_length=5), access_token: OAuth2AccessTokenDocument = Depends(
        OAuth2Service.get_access_token_by_header
    )):
    users = AccountDocument.objects(username__contains=query)
    return [User.build(user) for user in (users[:100] if len(users) > 100 else users)]
