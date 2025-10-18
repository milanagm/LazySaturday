from __future__ import annotations

import logging
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
        self._logger = logging.getLogger(__name__)

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
        timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
        self._logger.debug("Triggering n8n webhook", extra={
            "webhook_url": url,
            "payload_request_id": payload.get("request_id"),
        })
        try:
            resp = httpx.post(url, json=payload, headers=headers, auth=auth, timeout=timeout)
            resp.raise_for_status()
        except httpx.ReadTimeout:
            self._logger.warning(
                "Timeout while waiting for n8n response", extra={"webhook_url": url, "request_id": payload.get("request_id")}
            )
            return {}
        except httpx.HTTPStatusError as exc:
            response_content = exc.response.text if exc.response is not None else ""
            self._logger.error(
                "n8n webhook returned error",
                extra={
                    "webhook_url": url,
                    "request_id": payload.get("request_id"),
                    "status_code": exc.response.status_code if exc.response else None,
                    "response_body": response_content[:2000],
                },
            )
            raise
        if resp.content:
            return resp.json()
        return {}
