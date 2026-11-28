"""Pos ke Facebook Page melalui Graph API.

Nota: Meta tidak benarkan pos automatik ke profil peribadi — hanya ke Page.
"""

from __future__ import annotations

import requests

from .http import call


class FacebookClient:
    def __init__(self, page_id: str, access_token: str, version: str = "v23.0",
                 session: requests.Session | None = None):
        self.page_id = page_id
        self.token = access_token
        self.base = f"https://graph.facebook.com/{version}"
        self.session = session or requests.Session()

    def _post(self, path: str, data: dict) -> dict:
        return call(self.session, "POST", f"{self.base}/{path}",
                    data={**data, "access_token": self.token})

    def check(self) -> str:
        data = call(self.session, "GET", f"{self.base}/{self.page_id}",
                    params={"fields": "name", "access_token": self.token})
        return data.get("name", self.page_id)

    def post_photo(self, image_url: str, caption: str) -> str:
        data = self._post(f"{self.page_id}/photos", {"url": image_url, "caption": caption})
        return data.get("post_id") or data["id"]

    def post_feed(self, message: str, link: str | None = None) -> str:
        payload = {"message": message}
        if link:
            payload["link"] = link
        return self._post(f"{self.page_id}/feed", payload)["id"]

    def comment(self, object_id: str, message: str) -> str:
        return self._post(f"{object_id}/comments", {"message": message})["id"]
