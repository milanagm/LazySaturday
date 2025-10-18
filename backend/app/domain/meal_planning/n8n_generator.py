from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List
from uuid import uuid4

import httpx
from pydantic import ValidationError

from ...integrations.n8n_client import N8NClient
from .contracts import MealPlanGenerationContext, MealPlanGenerationError, MealPlanGenerationResult, MealPlanGenerator


logger = logging.getLogger(__name__)


class N8NMealPlanGenerator(MealPlanGenerator):
    """Delegates meal plan generation to an n8n workflow."""

    def __init__(self, client: N8NClient, workflow_path: str) -> None:
        self._client = client
        self._workflow_path = workflow_path

    def generate(self, context: MealPlanGenerationContext) -> MealPlanGenerationResult:
        payload = self._build_payload(context)
        try:
            response = self._client.trigger_webhook(self._workflow_path, payload)
        except httpx.RequestError as exc:  # pragma: no cover - network failure
            logger.error(
                "Unable to reach n8n meal plan generator",
                extra={"request_id": str(context.request_id), "error": str(exc)},
            )
            raise MealPlanGenerationError(
                code="n8n_http_error",
                message="Unable to reach the meal plan generator",
                retryable=True,
                details={"error": str(exc)},
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text if exc.response is not None else ""
            logger.error(
                "n8n returned HTTP error",
                extra={
                    "request_id": str(context.request_id),
                    "status_code": exc.response.status_code if exc.response else None,
                    "response_body": detail[:2000],
                },
            )
            raise MealPlanGenerationError(
                code="n8n_http_error",
                message="Meal plan generator returned an error",
                retryable=400 <= (exc.response.status_code if exc.response else 500) < 500,
                details={"status_code": exc.response.status_code if exc.response else None, "body": detail},
            ) from exc

        if not response:
            raise MealPlanGenerationError(
                code="n8n_empty_response",
                message="Generator returned no data",
                retryable=False,
            )

        try:
            normalized = self._normalize_response(response, context)
            return MealPlanGenerationResult.model_validate(normalized)
        except ValidationError as exc:
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message="Generator returned invalid data",
                retryable=False,
                details={"errors": exc.errors()},
            ) from exc

    def enqueue(self, context: MealPlanGenerationContext) -> None:
        payload = self._build_payload(context)
        try:
            self._client.trigger_webhook(self._workflow_path, payload)
        except httpx.RequestError as exc:  # pragma: no cover - network failure
            raise MealPlanGenerationError(
                code="n8n_http_error",
                message="Unable to reach the meal plan generator",
                retryable=True,
                details={"error": str(exc)},
            ) from exc

    def _build_payload(self, context: MealPlanGenerationContext) -> Dict[str, Any]:
        return {
            "request_id": str(context.request_id),
            "user_email": context.user_email,
            "week_start": context.week_start.isoformat(),
            "context": context.model_dump(mode="json"),
        }

    def _normalize_response(
        self,
        response: Dict[str, Any] | List[Dict[str, Any]],
        context: MealPlanGenerationContext,
    ) -> Dict[str, Any]:
        if isinstance(response, dict):
            raw_meals = response.get("meals")
            if raw_meals is None and self._looks_like_meal_payload(response):
                raw_meals = [response]
                plan_id = None
                status = "ready"
                shopping_list_raw = None
                summary_raw = None
                warnings_raw: Iterable[Any] | None = None
                diagnostics_raw = None
            else:
                plan_id = response.get("plan_id")
                status_raw = response.get("status")
                if isinstance(status_raw, str):
                    status = status_raw.strip() or "ready"
                elif status_raw is None:
                    status = "ready"
                else:
                    status = str(status_raw)
                shopping_list_raw = response.get("shopping_list")
                summary_raw = response.get("summary")
                warnings_raw = response.get("warnings")
                diagnostics_raw = response.get("diagnostics")
        elif isinstance(response, list):
            raw_meals = response
            plan_id = None
            status = "ready"
            shopping_list_raw = None
            summary_raw = None
            warnings_raw = None
            diagnostics_raw = None
        else:
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message="Generator returned data in an unexpected format",
                retryable=False,
            )

        if not raw_meals:
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message="Generator response did not include any meals",
                retryable=False,
            )

        if not isinstance(raw_meals, list):
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message="Generator response 'meals' field must be a list",
                retryable=False,
            )

        meals = [self._normalize_meal(meal) for meal in raw_meals]

        if shopping_list_raw is None:
            shopping_list = self._build_shopping_list(meals)
        else:
            shopping_list = self._normalize_shopping_list(shopping_list_raw)
        summary = self._normalize_summary(summary_raw) if summary_raw else self._build_summary(meals, context)
        warnings = self._normalize_warnings(warnings_raw)
        diagnostics = diagnostics_raw if isinstance(diagnostics_raw, dict) else None

        return {
            "plan_id": plan_id or str(uuid4()),
            "meals": meals,
            "shopping_list": shopping_list,
            "summary": summary,
            "warnings": warnings,
            "diagnostics": diagnostics,
            "status": status,
        }

    def _normalize_meal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message="Meal entry is not an object",
                retryable=False,
            )

        required_fields = ("day_of_week", "meal_type", "recipe_title")
        missing = [field for field in required_fields if not payload.get(field)]
        if missing:
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message=f"Meal entry is missing required fields: {', '.join(missing)}",
                retryable=False,
            )

        instructions_raw = payload.get("instructions") or payload.get("instruction_steps") or []
        ingredients_raw = payload.get("ingredients") or []
        normalized: Dict[str, Any] = {
            "day_of_week": str(payload["day_of_week"]),
            "meal_type": str(payload["meal_type"]),
            "recipe_id": payload.get("recipe_id"),
            "recipe_title": str(payload["recipe_title"]),
            "ingredients": [self._normalize_ingredient(item) for item in ingredients_raw],
            "instructions": [self._normalize_instruction(step) for step in instructions_raw],
            "tags": self._normalize_tags(payload.get("tags")),
        }

        if payload.get("prep_time_minutes") is not None:
            normalized["prep_time_minutes"] = self._parse_positive_int(payload.get("prep_time_minutes"))
        if payload.get("cook_time_minutes") is not None:
            normalized["cook_time_minutes"] = self._parse_positive_int(payload.get("cook_time_minutes"))
        if payload.get("nutrition"):
            normalized["nutrition"] = payload["nutrition"]
        if payload.get("source"):
            normalized["source"] = payload.get("source")

        return normalized

    @staticmethod
    def _normalize_tags(raw: Any) -> List[str]:
        if not raw:
            return []
        if isinstance(raw, str):
            return [raw]
        if isinstance(raw, (list, tuple, set)):
            return [str(item) for item in raw if item is not None]
        return []

    def _normalize_ingredient(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message="Ingredient entry is not an object",
                retryable=False,
            )
        name = raw.get("name")
        unit = raw.get("unit")
        if not name or not unit:
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message="Ingredient entry requires 'name' and 'unit'",
                retryable=False,
            )
        quantity = self._parse_quantity(raw.get("quantity"))
        normalized = {
            "name": str(name),
            "quantity": quantity,
            "unit": str(unit),
        }
        if raw.get("notes"):
            normalized["notes"] = str(raw["notes"])
        return normalized

    @staticmethod
    def _normalize_instruction(raw: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message="Instruction entry is not an object",
                retryable=False,
            )
        step_number = raw.get("step_number")
        description = raw.get("description")
        if step_number is None or description is None:
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message="Instruction entry requires 'step_number' and 'description'",
                retryable=False,
            )
        normalized = {
            "step_number": self._parse_positive_int(step_number, minimum=1),
            "description": str(description),
        }
        if raw.get("duration_minutes") is not None:
            normalized["duration_minutes"] = self._parse_positive_int(raw.get("duration_minutes"), minimum=0)
        return normalized

    @staticmethod
    def _normalize_warnings(raw: Iterable[Any] | None) -> List[Dict[str, Any]]:
        if not raw:
            return []
        warnings: List[Dict[str, Any]] = []
        for entry in raw:
            if isinstance(entry, dict) and entry.get("code") and entry.get("message"):
                warnings.append(
                    {
                        "code": str(entry["code"]),
                        "message": str(entry["message"]),
                        "blocking": bool(entry.get("blocking", False)),
                    }
                )
        return warnings

    @staticmethod
    def _normalize_shopping_list(raw: Any) -> List[Dict[str, Any]]:
        if not isinstance(raw, list):
            return []
        normalized: List[Dict[str, Any]] = []
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            name = entry.get("name")
            unit = entry.get("unit")
            quantity = entry.get("quantity")
            if not name or unit is None or quantity is None:
                continue
            normalized.append(
                {
                    "category": entry.get("category"),
                    "name": str(name),
                    "quantity": N8NMealPlanGenerator._parse_quantity_static(quantity),
                    "unit": str(unit),
                    "notes": entry.get("notes"),
                    "is_pantry": bool(entry.get("is_pantry", False)),
                }
            )
        return normalized

    def _build_shopping_list(self, meals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        aggregated: Dict[tuple[str, str], Dict[str, Any]] = {}
        for meal in meals:
            for ingredient in meal.get("ingredients", []):
                key = (ingredient["name"].strip().lower(), ingredient["unit"])
                if key not in aggregated:
                    aggregated[key] = {
                        "category": None,
                        "name": ingredient["name"],
                        "quantity": 0.0,
                        "unit": ingredient["unit"],
                        "notes": ingredient.get("notes"),
                        "is_pantry": False,
                    }
                aggregated[key]["quantity"] += ingredient["quantity"]
        ordered = sorted(aggregated.values(), key=lambda item: item["name"])
        return ordered

    def _build_summary(
        self, meals: List[Dict[str, Any]], context: MealPlanGenerationContext
    ) -> Dict[str, Any]:
        total_prep = sum(meal.get("prep_time_minutes") or 0 for meal in meals)
        total_cook = sum(meal.get("cook_time_minutes") or 0 for meal in meals)
        overview = (
            f"Generated {len(meals)} meals for the week starting {context.week_start.isoformat()} "
            f"with approximately {total_prep + total_cook} minutes of prep and cook time."
        )
        return {
            "overview": overview,
            "calorie_total": None,
            "macro_totals": None,
            "allergy_warnings": [],
            "variety_score": None,
        }

    @staticmethod
    def _normalize_summary(raw: Any) -> Dict[str, Any]:
        if isinstance(raw, dict) and raw.get("overview"):
            normalized = dict(raw)
            if "allergy_warnings" not in normalized or normalized["allergy_warnings"] is None:
                normalized["allergy_warnings"] = []
            return normalized
        return {"overview": "Generated meal plan", "allergy_warnings": []}

    @staticmethod
    def _looks_like_meal_payload(payload: Dict[str, Any]) -> bool:
        return all(field in payload for field in ("day_of_week", "meal_type", "recipe_title"))

    @staticmethod
    def _parse_quantity(value: Any) -> float:
        return N8NMealPlanGenerator._parse_quantity_static(value)

    @staticmethod
    def _parse_quantity_static(value: Any) -> float:
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        return 0.0

    @staticmethod
    def _parse_positive_int(value: Any, minimum: int = 0) -> int:
        if isinstance(value, bool):
            return minimum
        if isinstance(value, (int, float)):
            parsed = int(value)
        elif isinstance(value, str):
            try:
                parsed = int(float(value))
            except ValueError:
                return minimum
        else:
            return minimum
        return parsed if parsed >= minimum else minimum
