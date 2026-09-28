from fastapi import APIRouter

from .routes import api_keys, auth, endpoints

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(endpoints.router)
router.include_router(api_keys.router)
