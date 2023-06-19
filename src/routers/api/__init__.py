from fastapi import APIRouter

from src.routers.api.oauth2_v1 import router as oauth2_v1_router

router: APIRouter = APIRouter(prefix="/api")

router.include_router(oauth2_v1_router)
