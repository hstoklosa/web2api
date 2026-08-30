from fastapi import APIRouter

from .routes import auth, endpoints

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(endpoints.router)
