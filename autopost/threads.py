"""Pos ke Threads melalui Threads API (graph.threads.net)."""

from __future__ import annotations

import time

import requests

from .http import ApiError, call

BASE = "https://graph.threads.net/v1.0"


class ThreadsClient:
    def __init__(self, user_id: str, access_token: str,
                 session: requests.Session | None = None,
                 poll_interval: float = 3.0, poll_timeout: float = 120.0):
        self.user_id = user_id or "me"
        self.token = access_token
        self.session = session or requests.Session()
        self.poll_interval = poll_interval
        self.poll_timeout = poll_timeout

    def check(self) -> str:
        data = call(self.session, "GET", f"{BASE}/me",
                    params={"fields": "id,username", "access_token": self.token})
        return "@" + data.get("username", data.get("id", "?"))

    def _create_container(self, text: str, image_url: str | None = None,
                          reply_to_id: str | None = None, link: str | None = None) -> str:
        data: dict[str, str] = {"text": text, "access_token": self.token}
        if image_url:
            data.update(media_type="IMAGE", image_url=image_url)
        else:
            data["media_type"] = "TEXT"
            if link:
                data["link_attachment"] = link
        if reply_to_id:
            data["reply_to_id"] = reply_to_id
        return call(self.session, "POST", f"{BASE}/{self.user_id}/threads", data=data)["id"]

    def _wait_ready(self, container_id: str) -> None:
        deadline = time.monotonic() + self.poll_timeout
        while True:
            info = call(self.session, "GET", f"{BASE}/{container_id}",
                        params={"fields": "status,error_message", "access_token": self.token})
            status = info.get("status", "FINISHED")
            if status == "FINISHED":
                return
            if status in {"ERROR", "EXPIRED"}:
                raise ApiError(f"Container Threads gagal: {info.get('error_message', status)}")
            if time.monotonic() > deadline:
                raise ApiError("Container Threads mengambil masa terlalu lama untuk siap")
            time.sleep(self.poll_interval)

    def _publish(self, container_id: str) -> str:
        return call(self.session, "POST", f"{BASE}/{self.user_id}/threads_publish",
                    data={"creation_id": container_id, "access_token": self.token})["id"]

    def post(self, text: str, image_url: str | None = None,
             reply_to_id: str | None = None, link: str | None = None) -> str:
        cid = self._create_container(text, image_url, reply_to_id, link)
        self._wait_ready(cid)
        return self._publish(cid)

    @staticmethod
    def refresh_token(access_token: str, session: requests.Session | None = None) -> dict:
        """Panjangkan long-lived token (60 hari). Token mesti berumur > 24 jam."""
        return call(session or requests.Session(), "GET", "https://graph.threads.net/refresh_access_token",
                    params={"grant_type": "th_refresh_token", "access_token": access_token})
