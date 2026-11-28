"""Simpan rekod produk yang telah dipos (data/state.json)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_HISTORY = 500


class State:
    def __init__(self, path: Path):
        self.path = path
        self.data: dict[str, Any] = {"last_posted": {}, "slots_done": [], "history": []}
        if path.exists():
            self.data.update(json.loads(path.read_text(encoding="utf-8") or "{}"))

    @property
    def last_posted(self) -> dict[str, str]:
        return self.data["last_posted"]

    def slot_done(self, slot: str) -> bool:
        return slot in self.data["slots_done"]

    def mark_slot(self, slot: str) -> None:
        self.data["slots_done"] = (self.data["slots_done"] + [slot])[-50:]

    def record(self, product_id: str, when_iso: str, results: dict[str, Any]) -> None:
        if any(r.get("ok") for r in results.values()):
            self.last_posted[product_id] = when_iso
        self.data["history"] = (
            self.data["history"] + [{"time": when_iso, "product": product_id, "results": results}]
        )[-MAX_HISTORY:]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)
