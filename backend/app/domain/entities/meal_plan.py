from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict

from sqlalchemy import Date, DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database import Base
from ...core.types import GUID


class MealPlanRecordModel(Base):
    __tablename__ = "meal_plans"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    diet_id: Mapped[str] = mapped_column(String(100), nullable=False)
    culture_id: Mapped[str] = mapped_column(String(100), nullable=False)
    plan_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
