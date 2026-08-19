from fastapi import APIRouter

from .routes import build

router = APIRouter()

router.include_router(build.router)
