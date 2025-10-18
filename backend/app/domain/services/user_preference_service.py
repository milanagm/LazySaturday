from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import UUID, uuid4

from ...schemas.user import UserPreferencesRequest, UserPreferencesSaveResponse, UserPreferencesView


@dataclass
class StoredPreferences:
    email: str
    payload: UserPreferencesView
    workflow_id: UUID
    updated_at: datetime


class UserPreferenceService:
    """In-memory representation of user preference persistence and workflow triggers."""

    def __init__(self) -> None:
        self._storage: Dict[str, StoredPreferences] = {}

    def save_preferences(self, payload: UserPreferencesRequest) -> UserPreferencesSaveResponse:
        workflow_id = uuid4()
        data = payload.model_dump()
        for key in ("additional_cultures", "dietary_goals", "allergies", "disliked_ingredients"):
            data[key] = list(dict.fromkeys(data.get(key, [])))
        view = UserPreferencesView(**data)
        record = StoredPreferences(
            email=payload.email.lower(),
            payload=view,
            workflow_id=workflow_id,
            updated_at=datetime.now(timezone.utc),
        )
        self._storage[record.email] = record
        return UserPreferencesSaveResponse(
            status="accepted",
            workflow_id=workflow_id,
            message="Preferences saved. Plan generation in progress.",
        )

    def get_preferences(self, email: str) -> Optional[UserPreferencesView]:
        record = self._storage.get(email.lower())
        return record.payload if record else None
