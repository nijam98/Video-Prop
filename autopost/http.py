"""Pembantu HTTP dengan mesej ralat yang jelas dari Graph API."""

from __future__ import annotations

from typing import Any

import requests

TIMEOUT = 60


class ApiError(RuntimeError):
    pass


def call(session: requests.Session, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
    kwargs.setdefault("timeout", TIMEOUT)
    resp = session.request(method, url, **kwargs)
    try:
        data = resp.json()
    except ValueError:
        data = {"raw": resp.text[:500]}
    if resp.status_code >= 400 or (isinstance(data, dict) and "error" in data):
        err = data.get("error", data) if isinstance(data, dict) else data
        if isinstance(err, dict):
            msg = err.get("error_user_msg") or err.get("message") or str(err)
            code = err.get("code", resp.status_code)
        else:
            msg, code = str(err), resp.status_code
        raise ApiError(f"[{code}] {msg}")
    return data
