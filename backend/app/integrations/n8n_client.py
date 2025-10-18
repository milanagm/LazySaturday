from __future__ import annotations

from typing import Any, Dict

import httpx


class N8NClient:
    """Lightweight HTTP client placeholder for orchestrating workflows."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        basic_auth_user: str | None = None,
        basic_auth_password: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.basic_auth_user = basic_auth_user
        self.basic_auth_password = basic_auth_password

    def trigger_webhook(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers: Dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        webhook_path = path.lstrip("/")
        if webhook_path.startswith("webhook"):
            url = f"{self.base_url}/{webhook_path}"
        else:
            url = f"{self.base_url}/webhook/{webhook_path}"
        auth = None
        if self.basic_auth_user and self.basic_auth_password:
            auth = (self.basic_auth_user, self.basic_auth_password)
        resp = httpx.post(url, json=payload, headers=headers, auth=auth, timeout=30.0)
        resp.raise_for_status()
        if resp.content:
            return resp.json()
        return {}
