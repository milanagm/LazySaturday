import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ...core.database import Base
from ...schemas.user import LoginRequest, RegisterRequest
from .auth_service import AuthService


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


def test_register_creates_user_and_returns_token(session: Session) -> None:
    service = AuthService(session)
    payload = RegisterRequest(email="person@example.com", password="StrongPass123")

    result = service.register(payload)

    assert result.user.email == "person@example.com"
    assert result.response.access_token
    assert result.response.token_type == "bearer"
    assert result.response.expires_in > 0


def test_login_requires_existing_user(session: Session) -> None:
    service = AuthService(session)
    service.register(RegisterRequest(email="person@example.com", password="StrongPass123"))
    session.commit()

    result = service.login(LoginRequest(email="person@example.com", password="StrongPass123"))

    assert result.user.email == "person@example.com"


def test_login_with_invalid_credentials(session: Session) -> None:
    service = AuthService(session)
    with pytest.raises(HTTPException) as exc:
        service.login(LoginRequest(email="unknown@example.com", password="Secret123"))
    assert exc.value.status_code == 401


def test_register_duplicate_email(session: Session) -> None:
    service = AuthService(session)
    service.register(RegisterRequest(email="person@example.com", password="StrongPass123"))
    session.commit()

    with pytest.raises(HTTPException) as exc:
        service.register(RegisterRequest(email="person@example.com", password="AnotherPass123"))
    assert exc.value.status_code == 400
