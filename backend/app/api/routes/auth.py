from datetime import timedelta
from typing import Annotated, Any

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import TokenType, create_access_token, create_refresh_token
from app.deps import CurrentUserDep, SessionDep
from app.schemas.user import RegisterUserRequest, TokenResponse, UserResponse
from app.services.user_service import (
    authenticate_user,
    create_user,
    get_user_from_token,
)
from fastapi import APIRouter, Cookie, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "refresh_token"


def _refresh_cookie_attrs() -> dict[str, Any]:
    # Deletion only matches the cookie when these attributes are identical.
    return {
        "key": REFRESH_COOKIE_NAME,
        "path": "/v1/auth",
        "secure": settings.COOKIE_SECURE,
        "httponly": True,
        "samesite": "strict",
    }


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        value=token,
        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
        **_refresh_cookie_attrs(),
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(request: RegisterUserRequest, session: SessionDep) -> UserResponse:
    user = await create_user(
        session=session,
        email=request.email,
        password=request.password,
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
    response: Response,
) -> TokenResponse:
    user = await authenticate_user(session, form.username, form.password)
    _set_refresh_cookie(response, create_refresh_token(str(user.id)))
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    session: SessionDep,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)] = None,
) -> TokenResponse:
    if refresh_token is None:
        raise AuthenticationError("Missing refresh token")
    user = await get_user_from_token(session, refresh_token, TokenType.REFRESH)
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(**_refresh_cookie_attrs())


@router.get("/me", response_model=UserResponse)
async def read_current_user(user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(user)
