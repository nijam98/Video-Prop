import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from autopost.captions import Templates, build_caption
from autopost.config import Settings
from autopost.products import Product, append_products, load_products, pick_next
from autopost.runner import Runner

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def templates():
    return Templates.load(ROOT / "data" / "templates.json")


@pytest.fixture
def product():
    return Product(id="p1", name="Kipas Mini", price="12.50", original_price="29.90",
                   affiliate_link="https://s.shopee.com.my/abc", image_url="https://img/x.jpg",
                   hashtags=["#a", "#b", "#c"])


def test_caption_contains_link_and_discount(templates, product):
    for seed in range(20):
        text = build_caption(product, templates, "facebook", rng=random.Random(seed))
        assert "https://s.shopee.com.my/abc" in text
        assert "{" not in text


def test_caption_without_link_has_cta(templates, product):
    text = build_caption(product, templates, "facebook", include_link=False, rng=random.Random(1))
    assert "s.shopee" not in text
    assert "komen" in text.lower()


def test_empty_placeholder_lines_removed(templates):
    p = Product(id="x", name="Barang", affiliate_link="https://l", price="10")
    for seed in range(20):
        text = build_caption(p, templates, "facebook", rng=random.Random(seed))
        assert "asal" not in text and "Jimat %" not in text and "{" not in text


def test_threads_limit_keeps_link(templates):
    p = Product(id="x", name="A" * 800, affiliate_link="https://s.shopee.com.my/zzz", price="10")
    text = build_caption(p, templates, "threads", max_hashtags=1, rng=random.Random(0))
    assert len(text) <= 500
    assert text.endswith("https://s.shopee.com.my/zzz")


def test_pick_next_prefers_unposted_then_oldest():
    now = datetime(2026, 1, 10)
    ps = [Product(id=i, name=i, affiliate_link="l") for i in "abc"]
    assert pick_next(ps, {"a": now.isoformat(), "b": now.isoformat()}, now, 7).id == "c"
    last = {"a": (now - timedelta(days=9)).isoformat(),
            "b": (now - timedelta(days=8)).isoformat(),
            "c": (now - timedelta(days=1)).isoformat()}
    assert pick_next(ps, last, now, 7).id == "a"
    # semua dalam cooldown -> masih pilih paling lama
    last = {k: (now - timedelta(days=d)).isoformat() for k, d in zip("abc", (3, 1, 2))}
    assert pick_next(ps, last, now, 7).id == "a"


def test_load_and_append_products(tmp_path):
    f = tmp_path / "p.csv"
    assert append_products(f, [Product(id="1", name="A", affiliate_link="l1", hashtags=["#x"])]) == 1
    assert append_products(f, [Product(id="1", name="A", affiliate_link="l1"),
                               Product(id="2", name="B", affiliate_link="l2")]) == 1
    loaded = load_products(f)
    assert [p.id for p in loaded] == ["1", "2"]
    assert loaded[0].hashtags == ["#x"]


class FakeFB:
    def __init__(self):
        self.calls = []

    def post_photo(self, url, caption):
        self.calls.append(("photo", url, caption))
        return "page_post1"

    def post_feed(self, message, link=None):
        self.calls.append(("feed", message, link))
        return "page_post2"

    def comment(self, oid, message):
        self.calls.append(("comment", oid, message))
        return "c1"


class FakeThreads:
    def __init__(self, fail=False):
        self.calls, self.fail = [], fail

    def post(self, text, image_url=None, reply_to_id=None, link=None):
        if self.fail:
            raise RuntimeError("boom")
        self.calls.append((text, image_url, reply_to_id, link))
        return f"t{len(self.calls)}"


def _settings(tmp_path, **kw):
    products = tmp_path / "products.csv"
    append_products(products, [Product(id="p1", name="Kipas", price="10",
                                       affiliate_link="https://s.shopee.com.my/real",
                                       image_url="https://img/1.jpg")])
    return Settings(products_file=products, templates_file=ROOT / "data" / "templates.json",
                    state_file=tmp_path / "state.json", **kw)


def test_run_once_posts_and_records(tmp_path):
    fb, th = FakeFB(), FakeThreads()
    r = Runner(_settings(tmp_path), facebook=fb, threads=th, rng=random.Random(0))
    out = r.run_once()
    assert out["results"]["facebook"]["ok"] and out["results"]["threads"]["ok"]
    assert fb.calls[0][0] == "photo" and "s.shopee" not in fb.calls[0][2]  # link dalam komen
    assert fb.calls[1] == ("comment", "page_post1", "🛒 Order sini: https://s.shopee.com.my/real")
    assert "https://s.shopee.com.my/real" in th.calls[0][0]
    state = json.loads((tmp_path / "state.json").read_text())
    assert "p1" in state["last_posted"]


def test_one_platform_failure_does_not_block_other(tmp_path):
    fb = FakeFB()
    r = Runner(_settings(tmp_path), facebook=fb, threads=FakeThreads(fail=True))
    out = r.run_once()
    assert out["results"]["facebook"]["ok"]
    assert not out["results"]["threads"]["ok"]


def test_dry_run_does_not_post_or_save(tmp_path):
    fb = FakeFB()
    r = Runner(_settings(tmp_path), facebook=fb, threads=FakeThreads())
    out = r.run_once(dry_run=True)
    assert fb.calls == []
    assert out["results"]["facebook"]["caption"]
    assert not (tmp_path / "state.json").exists()


def test_threads_link_in_reply(tmp_path):
    th = FakeThreads()
    r = Runner(_settings(tmp_path, fb_enabled=False, threads_link_in_reply=True), threads=th)
    r.run_once()
    assert "s.shopee" not in th.calls[0][0]
    assert th.calls[1][2] == "t1" and th.calls[1][3] == "https://s.shopee.com.my/real"
