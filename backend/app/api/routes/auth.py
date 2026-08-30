from typing import Annotated

from app.core.security import create_access_token
from app.deps import CurrentUserDep, SessionDep
from app.schemas.user import RegisterUserRequest, TokenResponse, UserResponse
from app.services.user_service import authenticate_user, create_user
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])


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
) -> TokenResponse:
    user = await authenticate_user(session, form.username, form.password)
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserResponse)
async def read_current_user(user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(user)
