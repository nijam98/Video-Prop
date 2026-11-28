"""Senarai produk (CSV) dan pemilihan produk seterusnya untuk dipos."""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

COLUMNS = [
    "id", "name", "price", "original_price", "affiliate_link",
    "image_url", "hashtags", "caption", "active",
]


@dataclass
class Product:
    id: str
    name: str
    affiliate_link: str
    price: str = ""
    original_price: str = ""
    image_url: str = ""
    hashtags: list[str] = field(default_factory=list)
    caption: str = ""
    active: bool = True

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Product":
        def g(key: str) -> str:
            return (row.get(key) or "").strip()

        tags = [t if t.startswith("#") else f"#{t}" for t in g("hashtags").replace(",", " ").split() if t]
        active = g("active").lower() not in {"0", "false", "no", "tidak", "n"}
        return cls(
            id=g("id") or g("affiliate_link"),
            name=g("name"),
            affiliate_link=g("affiliate_link"),
            price=g("price"),
            original_price=g("original_price"),
            image_url=g("image_url"),
            hashtags=tags,
            caption=g("caption").replace("\\n", "\n"),
            active=active,
        )

    def to_row(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "original_price": self.original_price,
            "affiliate_link": self.affiliate_link,
            "image_url": self.image_url,
            "hashtags": " ".join(self.hashtags),
            "caption": self.caption.replace("\n", "\\n"),
            "active": "1" if self.active else "0",
        }


def load_products(path: Path) -> list[Product]:
    if not path.exists():
        raise FileNotFoundError(f"Fail produk tidak dijumpai: {path}")
    with path.open(newline="", encoding="utf-8-sig") as f:
        products = [Product.from_row(r) for r in csv.DictReader(f)]
    return [p for p in products if p.active and p.name and p.affiliate_link]


def append_products(path: Path, products: list[Product]) -> int:
    """Tambah produk baru ke CSV (abaikan id yang sudah wujud). Pulangkan bilangan ditambah."""
    existing: set[str] = set()
    if path.exists():
        with path.open(newline="", encoding="utf-8-sig") as f:
            existing = {(r.get("id") or "").strip() for r in csv.DictReader(f)}
    new = [p for p in products if p.id not in existing]
    if not new:
        return 0
    write_header = not path.exists() or path.stat().st_size == 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        for p in new:
            writer.writerow(p.to_row())
    return len(new)


def pick_next(
    products: list[Product],
    last_posted: dict[str, str],
    now: datetime,
    cooldown_days: int,
    rng: random.Random | None = None,
) -> Product | None:
    """Pilih produk: yang belum pernah dipos dahulu, kemudian yang paling lama tidak dipos.

    Produk yang dipos dalam tempoh `cooldown_days` dilangkau. Jika semua produk masih
    dalam cooldown, produk paling lama dipos tetap dipilih supaya jadual tidak terhenti.
    """
    if not products:
        return None
    rng = rng or random.Random()

    never = [p for p in products if p.id not in last_posted]
    if never:
        return rng.choice(never)

    def ts(p: Product) -> datetime:
        return datetime.fromisoformat(last_posted[p.id])

    cutoff = now - timedelta(days=cooldown_days)
    ready = [p for p in products if ts(p) <= cutoff]
    pool = ready or products
    return min(pool, key=ts)
