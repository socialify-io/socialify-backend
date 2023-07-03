from fastapi import APIRouter

from src.routers.api.oauth2_v1 import router as oauth2_v1_router
from src.routers.api.messenger.dm_v1 import router as messenger_dm_v1_router
from src.routers.api.user_v1 import router as user_v1_router

router: APIRouter = APIRouter(prefix="/api")

router.include_router(oauth2_v1_router)
router.include_router(messenger_dm_v1_router)
router.include_router(user_v1_router)
