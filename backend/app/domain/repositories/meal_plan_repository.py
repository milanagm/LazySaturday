from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import Select, desc, select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from ...schemas.meal import MealPlanResponse
from ..entities.meal_plan import MealPlanRecordModel


def upsert_plan(session: Session, plan: MealPlanResponse) -> None:
    plan_data = plan.model_dump(mode="json")

    record = session.get(MealPlanRecordModel, plan.id)
    if record:
        record.user_email = plan.user_email
        record.week_start = plan.week_start
        record.status = plan.status
        record.diet_id = plan.diet_id
        record.culture_id = plan.culture_id
        record.plan_data = plan_data
        flag_modified(record, "plan_data")
    else:
        record = MealPlanRecordModel(
            id=plan.id,
            user_email=plan.user_email,
            week_start=plan.week_start,
            status=plan.status,
            diet_id=plan.diet_id,
            culture_id=plan.culture_id,
            plan_data=plan_data,
        )
        session.add(record)


def get_plan(session: Session, plan_id: UUID) -> Optional[MealPlanResponse]:
    record = session.get(MealPlanRecordModel, plan_id)
    if not record:
        return None
    data = record.plan_data
    data.setdefault("diet_id", record.diet_id or "")
    data.setdefault("culture_id", record.culture_id or "")
    return MealPlanResponse.model_validate(data)


def get_latest_for_user(session: Session, email: str) -> Optional[MealPlanResponse]:
    stmt: Select[MealPlanRecordModel] = (
        select(MealPlanRecordModel)
        .where(MealPlanRecordModel.user_email == email.lower())
        .order_by(desc(MealPlanRecordModel.created_at))
        .limit(1)
    )
    record = session.execute(stmt).scalar_one_or_none()
    if not record:
        return None
    data = record.plan_data
    data.setdefault("diet_id", record.diet_id or "")
    data.setdefault("culture_id", record.culture_id or "")
    return MealPlanResponse.model_validate(data)


def get_most_recent(session: Session) -> Optional[MealPlanResponse]:
    stmt: Select[MealPlanRecordModel] = select(MealPlanRecordModel).order_by(desc(MealPlanRecordModel.created_at)).limit(1)
    record = session.execute(stmt).scalar_one_or_none()
    if not record:
        return None
    data = record.plan_data
    data.setdefault("diet_id", record.diet_id or "")
    data.setdefault("culture_id", record.culture_id or "")
    return MealPlanResponse.model_validate(data)


def update_status(session: Session, plan_id: UUID, status: str) -> None:
    record = session.get(MealPlanRecordModel, plan_id)
    if not record:
        return
    record.status = status
    record.plan_data["status"] = status
    flag_modified(record, "plan_data")
