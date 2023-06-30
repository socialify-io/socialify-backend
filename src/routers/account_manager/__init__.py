from fastapi import APIRouter

from src.routers.account_manager.account_v1 import router as account_v1_router
from src.routers.account_manager.oauth2_token_v1 import router as oauth2_token_v1_router
from src.routers.account_manager.session_v1 import router as session_v1_router

router: APIRouter = APIRouter(prefix="/account-manager")


router.include_router(account_v1_router)
router.include_router(oauth2_token_v1_router)
router.include_router(session_v1_router)
