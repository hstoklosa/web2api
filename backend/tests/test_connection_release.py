"""Slow work must not run inside a database transaction.

An open transaction keeps its connection checked out of the pool, so a request
that fetches a page, calls the AI model or waits to hash a password while one
is open starves every other request of connections.
"""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app import deps
from app.core.security import TokenType
from app.services import endpoint_service, user_service

pytestmark = pytest.mark.anyio


class FakeSession:
    """Tracks whether a transaction is open, the way AsyncSession autobegins
    one on the first statement and ends it on commit."""

    def __init__(self, result: object = None) -> None:
        self.result = result
        self.in_transaction = False

    def _begin(self) -> object:
        self.in_transaction = True
        return self.result

    async def scalar(self, statement: object) -> object:
        return self._begin()

    async def get(self, entity: object, ident: object) -> object:
        return self._begin()

    def add(self, instance: object) -> None:
        self.in_transaction = True

    async def commit(self) -> None:
        self.in_transaction = False

    async def refresh(self, instance: object) -> None:
        pass


async def test_cookie_auth_ends_its_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession()

    async def from_token(
        session: FakeSession, token: str, token_type: TokenType
    ) -> SimpleNamespace:
        session.in_transaction = True
        return SimpleNamespace(id=1)

    monkeypatch.setattr(deps, "get_user_from_token", from_token)

    await deps.get_current_user(None, "token", session)  # type: ignore[arg-type]

    assert not session.in_transaction


async def test_endpoint_data_fetches_outside_a_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    endpoint = SimpleNamespace(
        url="https://example.com",
        extraction_schema={"fields": [{"name": "title", "selector": "h1"}]},
    )
    session = FakeSession(result=endpoint)

    async def fetch(url: str) -> str:
        assert not session.in_transaction
        return "<h1>Hello</h1>"

    monkeypatch.setattr(endpoint_service, "fetch_clean_html", fetch)

    data = await endpoint_service.get_endpoint_data(session, uuid4(), 1)  # type: ignore[arg-type]

    assert data == {"title": "Hello"}


async def test_login_verifies_outside_a_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(result=SimpleNamespace(id=1, hashed_password="hashed"))

    async def verify(password: str, hashed_password: str) -> bool:
        assert not session.in_transaction
        return True

    monkeypatch.setattr(user_service, "verify_password", verify)

    await user_service.authenticate_user(session, "a@example.com", "pw")  # type: ignore[arg-type]


async def test_register_hashes_outside_a_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession()

    async def hash_(password: str) -> str:
        assert not session.in_transaction
        return "hashed"

    monkeypatch.setattr(user_service, "hash_password", hash_)

    await user_service.create_user(session, "a@example.com", "pw")  # type: ignore[arg-type]
