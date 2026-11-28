"""Logik utama: pilih produk → jana kapsyen → pos ke setiap platform → simpan rekod."""

from __future__ import annotations

import logging
import random
import time
from dataclasses import replace
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from .captions import Templates, build_caption
from .config import Settings
from .facebook import FacebookClient
from .products import Product, load_products, pick_next
from .shopee import ShopeeAffiliate
from .state import State
from .threads import ThreadsClient

log = logging.getLogger("autopost")

SHORT_LINK_HOSTS = ("s.shopee.", "shope.ee", "shp.ee")


class Runner:
    def __init__(self, settings: Settings, facebook: FacebookClient | None = None,
                 threads: ThreadsClient | None = None, shopee: ShopeeAffiliate | None = None,
                 rng: random.Random | None = None):
        self.s = settings
        self.rng = rng or random.Random()
        self.tz = ZoneInfo(settings.timezone)

        if facebook is None and settings.fb_enabled and settings.fb_page_id and settings.fb_page_access_token:
            facebook = FacebookClient(settings.fb_page_id, settings.fb_page_access_token, settings.fb_graph_version)
        if threads is None and settings.threads_enabled and settings.threads_access_token:
            threads = ThreadsClient(settings.threads_user_id, settings.threads_access_token)
        if shopee is None and settings.shopee_enabled:
            shopee = ShopeeAffiliate(settings.shopee_app_id, settings.shopee_app_secret, settings.shopee_api_url)

        self.facebook = facebook if settings.fb_enabled else None
        self.threads = threads if settings.threads_enabled else None
        self.shopee = shopee

    # ------------------------------------------------------------------ helpers
    def now(self) -> datetime:
        return datetime.now(self.tz)

    def _link_for(self, product: Product, platform: str) -> str:
        """Jana short link dengan sub_id platform (jika Shopee API diset) supaya boleh jejak klik."""
        link = product.affiliate_link
        if not self.shopee or any(h in link for h in SHORT_LINK_HOSTS):
            return link
        try:
            return self.shopee.short_link(link, [platform])
        except Exception as e:  # noqa: BLE001 - guna link asal jika gagal
            log.warning("Gagal jana short link Shopee (%s), guna link asal", e)
            return link

    # ------------------------------------------------------------------ platforms
    def _post_facebook(self, product: Product, dry_run: bool) -> dict[str, Any]:
        link_in_comment = self.s.fb_link_in_comment
        p = replace(product, affiliate_link=product.affiliate_link if dry_run else self._link_for(product, "facebook"))
        caption = build_caption(p, self.templates, "facebook", include_link=not link_in_comment, rng=self.rng)
        comment = f"🛒 Order sini: {p.affiliate_link}" if link_in_comment else None
        if dry_run:
            return {"ok": True, "dry_run": True, "caption": caption, "comment": comment}

        if p.image_url:
            post_id = self.facebook.post_photo(p.image_url, caption)
        else:
            post_id = self.facebook.post_feed(caption, None if link_in_comment else p.affiliate_link)
        result: dict[str, Any] = {"ok": True, "id": post_id}
        if comment:
            try:
                result["comment_id"] = self.facebook.comment(post_id, comment)
            except Exception as e:  # noqa: BLE001
                result["comment_error"] = str(e)
                log.error("Facebook: pos berjaya tetapi komen link gagal: %s", e)
        return result

    def _post_threads(self, product: Product, dry_run: bool) -> dict[str, Any]:
        link_in_reply = self.s.threads_link_in_reply
        p = replace(product, affiliate_link=product.affiliate_link if dry_run else self._link_for(product, "threads"))
        text = build_caption(p, self.templates, "threads", include_link=not link_in_reply,
                             max_hashtags=self.s.threads_max_hashtags, rng=self.rng)
        reply = f"🛒 Link: {p.affiliate_link}" if link_in_reply else None
        if dry_run:
            return {"ok": True, "dry_run": True, "caption": text, "reply": reply}

        post_id = self.threads.post(text, image_url=p.image_url or None,
                                    link=None if (p.image_url or link_in_reply) else p.affiliate_link)
        result: dict[str, Any] = {"ok": True, "id": post_id}
        if reply:
            try:
                result["reply_id"] = self.threads.post(reply, reply_to_id=post_id, link=p.affiliate_link)
            except Exception as e:  # noqa: BLE001
                result["reply_error"] = str(e)
                log.error("Threads: pos berjaya tetapi reply link gagal: %s", e)
        return result

    # ------------------------------------------------------------------ public
    def run_once(self, dry_run: bool | None = None, product_id: str | None = None) -> dict[str, Any]:
        dry_run = self.s.dry_run if dry_run is None else dry_run
        self.templates = Templates.load(self.s.templates_file)
        products = load_products(self.s.products_file)
        state = State(self.s.state_file)
        now = self.now()

        if product_id:
            product = next((p for p in products if p.id == product_id), None)
            if not product:
                raise SystemExit(f"Produk dengan id '{product_id}' tidak dijumpai / tidak aktif")
        else:
            product = pick_next(products, state.last_posted, now, self.s.repost_cooldown_days, self.rng)
        if not product:
            log.warning("Tiada produk aktif dalam %s", self.s.products_file)
            return {}

        log.info("Produk dipilih: [%s] %s", product.id, product.name)
        if not dry_run and "CONTOH" in product.affiliate_link:
            raise SystemExit("Produk contoh masih dalam products.csv — gantikan dengan produk & link affiliate sebenar.")
        platforms = {"facebook": (self.facebook, self.s.fb_enabled, self._post_facebook),
                     "threads": (self.threads, self.s.threads_enabled, self._post_threads)}
        results: dict[str, Any] = {}
        for name, (client, enabled, fn) in platforms.items():
            # Dry run tetap papar kapsyen walaupun token belum diset.
            if client is None and not (dry_run and enabled):
                continue
            try:
                results[name] = fn(product, dry_run)
                log.info("%s: %s", name, "DRY RUN" if dry_run else f"berjaya (id={results[name].get('id')})")
            except Exception as e:  # noqa: BLE001 - satu platform gagal tidak halang yang lain
                results[name] = {"ok": False, "error": str(e)}
                log.error("%s: GAGAL — %s", name, e)

        if not results:
            log.warning("Tiada platform aktif. Semak token dalam .env")
        if not dry_run and results:
            state.record(product.id, now.isoformat(timespec="seconds"), results)
            state.save()
        return {"product": product, "results": results}

    def daemon(self, window_minutes: int = 30, tick_seconds: int = 30) -> None:
        """Jalan berterusan dan pos pada setiap waktu dalam POST_TIMES."""
        log.info("Daemon bermula. Waktu pos (%s): %s", self.s.timezone, ", ".join(self.s.post_times))
        while True:
            now = self.now()
            state = State(self.s.state_file)
            for hhmm in self.s.post_times:
                h, m = (int(x) for x in hhmm.split(":"))
                slot_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
                slot = slot_time.strftime("%Y-%m-%d %H:%M")
                if slot_time <= now < slot_time + timedelta(minutes=window_minutes) and not state.slot_done(slot):
                    log.info("Slot %s", slot)
                    try:
                        self.run_once()
                    except Exception:  # noqa: BLE001
                        log.exception("Ralat semasa pos slot %s", slot)
                    state = State(self.s.state_file)
                    state.mark_slot(slot)
                    state.save()
            time.sleep(tick_seconds)
