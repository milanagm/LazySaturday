from __future__ import annotations

from typing import Any, Dict

import httpx


class N8NClient:
    """Lightweight HTTP client placeholder for orchestrating workflows."""

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def trigger_workflow(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/webhook/{name}", json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
