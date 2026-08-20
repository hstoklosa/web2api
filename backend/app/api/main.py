from fastapi import APIRouter

from .routes import endpoints

router = APIRouter(prefix="/v1")

router.include_router(endpoints.router)
