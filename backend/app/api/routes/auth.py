from datetime import timedelta
from typing import Annotated, Any

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import (
    ACCESS_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    TokenType,
    create_access_token,
    create_refresh_token,
)
from app.deps import CurrentUserDep, SessionDep
from app.schemas.user import LoginUserRequest, RegisterUserRequest, UserResponse
from app.services.user_service import (
    authenticate_user,
    create_user,
    get_user_from_token,
)
from fastapi import APIRouter, Cookie, Response, status

router = APIRouter(prefix="/auth", tags=["auth"])

# Both tokens live in httpOnly cookies so page scripts can never read them. The
# access token goes to every API route, while the refresh token is only sent to
# the auth routes that exchange or clear it.
ACCESS_COOKIE_PATH = "/v1"
REFRESH_COOKIE_PATH = "/v1/auth"


def _cookie_attrs(key: str, path: str) -> dict[str, Any]:
    # Deletion only matches the cookie when these attributes are identical.
    return {
        "key": key,
        "path": path,
        "secure": settings.COOKIE_SECURE,
        "httponly": True,
        "samesite": "strict",
    }


def _set_access_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(
        value=create_access_token(str(user_id)),
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_cookie_attrs(ACCESS_COOKIE_NAME, ACCESS_COOKIE_PATH),
    )


def _set_session_cookies(response: Response, user_id: int) -> None:
    _set_access_cookie(response, user_id)
    response.set_cookie(
        value=create_refresh_token(str(user_id)),
        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
        **_cookie_attrs(REFRESH_COOKIE_NAME, REFRESH_COOKIE_PATH),
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterUserRequest,
    session: SessionDep,
    response: Response,
) -> UserResponse:
    user = await create_user(
        session=session,
        email=request.email,
        password=request.password,
    )
    _set_session_cookies(response, user.id)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=UserResponse)
async def login(
    request: LoginUserRequest,
    session: SessionDep,
    response: Response,
) -> UserResponse:
    user = await authenticate_user(session, request.email, request.password)
    _set_session_cookies(response, user.id)
    return UserResponse.model_validate(user)


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh(
    session: SessionDep,
    response: Response,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)] = None,
) -> None:
    if refresh_token is None:
        raise AuthenticationError("Missing refresh token")
    user = await get_user_from_token(session, refresh_token, TokenType.REFRESH)
    _set_access_cookie(response, user.id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(**_cookie_attrs(ACCESS_COOKIE_NAME, ACCESS_COOKIE_PATH))
    response.delete_cookie(**_cookie_attrs(REFRESH_COOKIE_NAME, REFRESH_COOKIE_PATH))


@router.get("/me", response_model=UserResponse)
async def read_current_user(user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(user)
