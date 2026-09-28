from types import SimpleNamespace

import httpx
import pytest
from fastapi import FastAPI

from app import deps
from app.core.database import get_db
from app.core.error_handlers import register_exception_handlers
from app.core.exceptions import AuthenticationError
from app.core.security import ACCESS_COOKIE_NAME
from app.deps import CurrentUserDep, SessionUserDep

pytestmark = pytest.mark.anyio

API_KEY_USER = SimpleNamespace(id=1)
SESSION_USER = SimpleNamespace(id=2)


@pytest.fixture(autouse=True)
def fake_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    async def from_api_key(session: object, key: str) -> SimpleNamespace:
        if key != "w2a_valid":
            raise AuthenticationError("Invalid API key")
        return API_KEY_USER

    async def from_token(
        session: object, token: str, token_type: object
    ) -> SimpleNamespace:
        if token != "valid":
            raise AuthenticationError("Could not validate credentials")
        return SESSION_USER

    monkeypatch.setattr(deps, "get_user_from_api_key", from_api_key)
    monkeypatch.setattr(deps, "get_user_from_token", from_token)


def make_client(
    headers: dict[str, str] | None = None, cookies: dict[str, str] | None = None
) -> httpx.AsyncClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.dependency_overrides[get_db] = lambda: None

    @app.get("/any")
    async def any_auth(user: CurrentUserDep) -> int:
        return user.id

    @app.get("/session")
    async def session_only(user: SessionUserDep) -> int:
        return user.id

    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        headers=headers,
        cookies=cookies,
    )


def bearer(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"}


async def test_accepts_an_api_key() -> None:
    async with make_client(headers=bearer("w2a_valid")) as client:
        response = await client.get("/any")

    assert response.status_code == 200
    assert response.json() == API_KEY_USER.id


async def test_accepts_a_session_cookie() -> None:
    async with make_client(cookies={ACCESS_COOKIE_NAME: "valid"}) as client:
        response = await client.get("/any")

    assert response.status_code == 200
    assert response.json() == SESSION_USER.id


async def test_prefers_the_api_key_over_the_cookie() -> None:
    async with make_client(
        headers=bearer("w2a_valid"), cookies={ACCESS_COOKIE_NAME: "valid"}
    ) as client:
        response = await client.get("/any")

    assert response.json() == API_KEY_USER.id


async def test_rejects_a_bad_api_key_despite_a_valid_cookie() -> None:
    async with make_client(
        headers=bearer("w2a_wrong"), cookies={ACCESS_COOKIE_NAME: "valid"}
    ) as client:
        response = await client.get("/any")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


async def test_rejects_requests_without_credentials() -> None:
    async with make_client() as client:
        response = await client.get("/any")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


async def test_session_only_routes_reject_api_keys() -> None:
    async with make_client(headers=bearer("w2a_valid")) as client:
        response = await client.get("/session")

    assert response.status_code == 401
    assert "API keys can't be used" in response.json()["detail"]


async def test_session_only_routes_accept_the_cookie() -> None:
    async with make_client(cookies={ACCESS_COOKIE_NAME: "valid"}) as client:
        response = await client.get("/session")

    assert response.json() == SESSION_USER.id
