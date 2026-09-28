from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

# Caps the input argon2 hashes on every register and login, and has to be the
# same for both so no password that registers can fail to log in.
PASSWORD_MAX_LENGTH = 128

# Emails are stored lowercased, which the users table enforces, so Foo@x.com and
# foo@x.com are one account and either spelling logs in to it.
NormalizedEmail = Annotated[EmailStr, AfterValidator(str.lower)]


class RegisterUserRequest(BaseModel):
    email: NormalizedEmail
    password: str = Field(min_length=8, max_length=PASSWORD_MAX_LENGTH)


class LoginUserRequest(BaseModel):
    email: NormalizedEmail
    password: str = Field(max_length=PASSWORD_MAX_LENGTH)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
