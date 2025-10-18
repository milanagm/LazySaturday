from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..entities.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower())
        return self._session.scalars(stmt).first()

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self._session.get(User, user_id)

    def save(self, user: User) -> User:
        self._session.add(user)
        return user
