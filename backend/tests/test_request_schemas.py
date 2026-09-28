import pytest
from pydantic import ValidationError

from app.schemas.endpoint import CreateEndpointRequest
from app.schemas.user import (
    PASSWORD_MAX_LENGTH,
    LoginUserRequest,
    RegisterUserRequest,
)

EMAIL = "user@example.com"
URL = "https://example.com/"


@pytest.mark.parametrize("model", [RegisterUserRequest, LoginUserRequest])
def test_accepts_a_password_at_the_cap(model: type) -> None:
    model(email=EMAIL, password="p" * PASSWORD_MAX_LENGTH)


@pytest.mark.parametrize("model", [RegisterUserRequest, LoginUserRequest])
def test_rejects_a_password_over_the_cap(model: type) -> None:
    with pytest.raises(ValidationError, match="password"):
        model(email=EMAIL, password="p" * (PASSWORD_MAX_LENGTH + 1))


def test_keeps_whitespace_in_passwords() -> None:
    request = RegisterUserRequest(email=EMAIL, password="  spaced out  ")

    assert request.password == "  spaced out  "


@pytest.mark.parametrize("model", [RegisterUserRequest, LoginUserRequest])
def test_lowercases_the_email(model: type) -> None:
    request = model(email="Foo.Bar@Example.COM", password="p" * 8)

    assert request.email == "foo.bar@example.com"


def test_accepts_a_url_at_the_cap() -> None:
    url = URL + "a" * (2048 - len(URL))

    assert str(CreateEndpointRequest(url=url, description="titles").url) == url


def test_rejects_a_url_over_the_cap() -> None:
    with pytest.raises(ValidationError, match="url"):
        CreateEndpointRequest(url=URL + "a" * (2049 - len(URL)), description="x")


def test_strips_whitespace_around_the_description() -> None:
    request = CreateEndpointRequest(url=URL, description="  top\nstories \n")

    assert request.description == "top\nstories"


def test_rejects_a_blank_description() -> None:
    with pytest.raises(ValidationError, match="description"):
        CreateEndpointRequest(url=URL, description=" \n\t ")


def test_measures_the_description_cap_after_stripping() -> None:
    request = CreateEndpointRequest(url=URL, description=f"  {'d' * 1000}  ")

    assert len(request.description) == 1000


def test_rejects_a_description_over_the_cap() -> None:
    with pytest.raises(ValidationError, match="description"):
        CreateEndpointRequest(url=URL, description="d" * 1001)
