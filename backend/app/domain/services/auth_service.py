from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ...core.config import get_settings
from ...core.security import create_access_token, hash_password, verify_password
from ..entities.user import User
from ..repositories.user_repository import UserRepository
from ...schemas.user import LoginRequest, LoginResponse, RegisterRequest, UserProfileResponse

settings = get_settings()


@dataclass
class AuthResult:
    user: User
    response: LoginResponse


class AuthService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._users = UserRepository(session)

    def register(self, payload: RegisterRequest) -> AuthResult:
        email = payload.email.lower()
        if self._users.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        user = User(email=email, hashed_password=hash_password(payload.password))
        self._users.save(user)

        return self._build_auth_result(user)

    def login(self, payload: LoginRequest) -> AuthResult:
        email = payload.email.lower()
        user = self._users.get_by_email(email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        return self._build_auth_result(user)

    def _build_auth_result(self, user: User) -> AuthResult:
        token = create_access_token(user.email)
        response = LoginResponse(
            access_token=token,
            expires_in=settings.access_token_expires_minutes * 60,
        )
        return AuthResult(user=user, response=response)

    def build_profile(self, user: User) -> UserProfileResponse:
        return UserProfileResponse(id=user.id, email=user.email, is_verified=user.is_verified)
