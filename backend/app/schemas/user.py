from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Caps the input argon2 hashes on every register and login, and has to be the
# same for both so no password that registers can fail to log in.
PASSWORD_MAX_LENGTH = 128


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=PASSWORD_MAX_LENGTH)


class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=PASSWORD_MAX_LENGTH)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
