from __future__ import annotations

from typing import Any, Dict

import httpx
from pydantic import ValidationError

from ...integrations.n8n_client import N8NClient
from .contracts import MealPlanGenerationContext, MealPlanGenerationError, MealPlanGenerationResult, MealPlanGenerator


class N8NMealPlanGenerator(MealPlanGenerator):
    """Delegates meal plan generation to an n8n workflow."""

    def __init__(self, client: N8NClient, workflow_path: str) -> None:
        self._client = client
        self._workflow_path = workflow_path

    def generate(self, context: MealPlanGenerationContext) -> MealPlanGenerationResult:
        payload = self._build_payload(context)
        try:
            response = self._client.trigger_webhook(self._workflow_path, payload)
        except httpx.HTTPError as exc:  # pragma: no cover - network failure
            raise MealPlanGenerationError(
                code="n8n_http_error",
                message="Unable to reach the meal plan generator",
                retryable=True,
                details={"error": str(exc)},
            ) from exc

        if not response:
            raise MealPlanGenerationError(
                code="n8n_empty_response",
                message="Generator returned no data",
                retryable=False,
            )

        try:
            return MealPlanGenerationResult.model_validate(response)
        except ValidationError as exc:
            raise MealPlanGenerationError(
                code="n8n_invalid_response",
                message="Generator returned invalid data",
                retryable=False,
                details={"errors": exc.errors()},
            ) from exc

    def _build_payload(self, context: MealPlanGenerationContext) -> Dict[str, Any]:
        return {
            "request_id": str(context.request_id),
            "user_email": context.user_email,
            "week_start": context.week_start.isoformat(),
            "context": context.model_dump(mode="json"),
        }
