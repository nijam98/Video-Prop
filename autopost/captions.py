"""Jana kapsyen berbeza-beza daripada template supaya pos tidak nampak berulang."""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path

from .products import Product

PLACEHOLDER = re.compile(r"\{(\w+)\}")
THREADS_LIMIT = 500
FB_LIMIT = 60000


@dataclass
class Templates:
    templates: list[str]
    hooks: list[str] = field(default_factory=lambda: [""])
    cta_link_elsewhere: dict[str, list[str]] = field(default_factory=dict)
    default_hashtags: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "Templates":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            templates=data["templates"],
            hooks=data.get("hooks") or [""],
            cta_link_elsewhere=data.get("cta_link_elsewhere", {}),
            default_hashtags=data.get("default_hashtags", []),
        )


def _num(value: str) -> float | None:
    try:
        return float(re.sub(r"[^\d.]", "", value))
    except ValueError:
        return None


def _money(value: str) -> str:
    if not value:
        return ""
    n = _num(value)
    if n is None:
        return value
    return f"RM{n:,.2f}".replace(".00", "")


def _fill(template: str, values: dict[str, str]) -> str:
    """Isi placeholder. Baris yang mengandungi placeholder kosong dibuang terus."""
    out = []
    for line in template.split("\n"):
        keys = PLACEHOLDER.findall(line)
        if any(not values.get(k, "") for k in keys):
            continue
        out.append(PLACEHOLDER.sub(lambda m: values.get(m.group(1), ""), line))
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def build_caption(
    product: Product,
    templates: Templates,
    platform: str,
    include_link: bool = True,
    max_hashtags: int | None = None,
    rng: random.Random | None = None,
) -> str:
    rng = rng or random.Random()

    tags = product.hashtags or templates.default_hashtags
    if max_hashtags is not None:
        tags = tags[:max_hashtags]

    price, original = _num(product.price), _num(product.original_price)
    discount = ""
    if price and original and original > price:
        discount = f"{round((1 - price / original) * 100)}%"

    values = {
        "hook": rng.choice(templates.hooks),
        "name": product.name,
        "price": _money(product.price),
        "original_price": _money(product.original_price) if discount else "",
        "discount": discount,
        "link": product.affiliate_link if include_link else "",
        "hashtags": " ".join(tags),
    }

    template = product.caption or rng.choice(templates.templates)
    text = _fill(template, values)

    if not include_link:
        ctas = templates.cta_link_elsewhere.get(platform) or ["Link di bawah 👇"]
        text = f"{text}\n\n{rng.choice(ctas)}"

    limit = THREADS_LIMIT if platform == "threads" else FB_LIMIT
    return _truncate(text, limit, keep=product.affiliate_link if include_link else "")


def _truncate(text: str, limit: int, keep: str = "") -> str:
    if len(text) <= limit:
        return text
    if keep and keep in text:
        # Pastikan link affiliate tidak terpotong.
        body = text.replace(keep, "").strip()
        room = limit - len(keep) - 3
        return f"{body[: max(room - 1, 0)].rstrip()}…\n\n{keep}"[:limit]
    return text[: limit - 1].rstrip() + "…"
