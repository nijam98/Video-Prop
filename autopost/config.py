"""Baca tetapan daripada fail .env dan environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path) -> None:
    """Parser .env ringkas (KEY=VALUE). Environment sedia ada tidak ditindih."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None or val.strip() == "":
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on", "ya"}


def _int(name: str, default: int) -> int:
    val = os.environ.get(name, "").strip()
    return int(val) if val else default


def _str(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _path(name: str, default: str) -> Path:
    p = Path(_str(name, default))
    return p if p.is_absolute() else ROOT / p


@dataclass
class Settings:
    # Facebook Page
    fb_enabled: bool = True
    fb_page_id: str = ""
    fb_page_access_token: str = ""
    fb_graph_version: str = "v23.0"
    fb_link_in_comment: bool = True

    # Threads
    threads_enabled: bool = True
    threads_user_id: str = "me"
    threads_access_token: str = ""
    threads_link_in_reply: bool = False
    threads_max_hashtags: int = 1

    # Shopee Affiliate Open API (pilihan)
    shopee_app_id: str = ""
    shopee_app_secret: str = ""
    shopee_api_url: str = "https://open-api.affiliate.shopee.com.my/graphql"

    # Jadual & data
    timezone: str = "Asia/Kuala_Lumpur"
    post_times: list[str] = field(default_factory=lambda: ["09:00", "13:00", "20:00"])
    repost_cooldown_days: int = 7
    products_file: Path = ROOT / "data" / "products.csv"
    templates_file: Path = ROOT / "data" / "templates.json"
    state_file: Path = ROOT / "data" / "state.json"
    dry_run: bool = False

    @property
    def shopee_enabled(self) -> bool:
        return bool(self.shopee_app_id and self.shopee_app_secret)


def load_settings(env_file: Path | None = None) -> Settings:
    load_dotenv(env_file or ROOT / ".env")
    times = [t.strip() for t in _str("POST_TIMES", "09:00,13:00,20:00").split(",") if t.strip()]
    return Settings(
        fb_enabled=_bool("FB_ENABLED", True),
        fb_page_id=_str("FB_PAGE_ID"),
        fb_page_access_token=_str("FB_PAGE_ACCESS_TOKEN"),
        fb_graph_version=_str("FB_GRAPH_VERSION", "v23.0"),
        fb_link_in_comment=_bool("FB_LINK_IN_COMMENT", True),
        threads_enabled=_bool("THREADS_ENABLED", True),
        threads_user_id=_str("THREADS_USER_ID", "me") or "me",
        threads_access_token=_str("THREADS_ACCESS_TOKEN"),
        threads_link_in_reply=_bool("THREADS_LINK_IN_REPLY", False),
        threads_max_hashtags=_int("THREADS_MAX_HASHTAGS", 1),
        shopee_app_id=_str("SHOPEE_APP_ID"),
        shopee_app_secret=_str("SHOPEE_APP_SECRET"),
        shopee_api_url=_str("SHOPEE_API_URL", "https://open-api.affiliate.shopee.com.my/graphql"),
        timezone=_str("TIMEZONE", "Asia/Kuala_Lumpur"),
        post_times=times,
        repost_cooldown_days=_int("REPOST_COOLDOWN_DAYS", 7),
        products_file=_path("PRODUCTS_FILE", "data/products.csv"),
        templates_file=_path("TEMPLATES_FILE", "data/templates.json"),
        state_file=_path("STATE_FILE", "data/state.json"),
        dry_run=_bool("DRY_RUN", False),
    )
