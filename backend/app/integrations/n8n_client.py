from __future__ import annotations

from typing import Any, Dict

import httpx


class N8NClient:
    """Lightweight HTTP client placeholder for orchestrating workflows."""

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def trigger_webhook(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers: Dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        webhook_path = path.lstrip("/")
        resp = httpx.post(f"{self.base_url}/webhook/{webhook_path}", json=payload, headers=headers, timeout=30.0)
        resp.raise_for_status()
        if resp.content:
            return resp.json()
        return {}
