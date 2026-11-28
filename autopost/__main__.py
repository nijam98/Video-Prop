"""CLI: python -m autopost <arahan>"""

from __future__ import annotations

import argparse
import logging
import sys

from .config import load_settings
from .products import append_products
from .runner import Runner


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="autopost", description="Autopost affiliate Shopee ke Facebook & Threads")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Pos satu produk sekarang")
    p_run.add_argument("--dry-run", action="store_true", help="Papar kapsyen sahaja, tidak pos")
    p_run.add_argument("--product", help="Pos produk dengan id tertentu")

    sub.add_parser("daemon", help="Jalan berterusan ikut POST_TIMES")

    p_prev = sub.add_parser("preview", help="Lihat contoh kapsyen")
    p_prev.add_argument("-n", "--count", type=int, default=3)

    sub.add_parser("check", help="Semak token Facebook & Threads")
    sub.add_parser("refresh-threads-token", help="Panjangkan token Threads (60 hari)")

    p_imp = sub.add_parser("import-shopee", help="Import produk dari Shopee Affiliate API")
    p_imp.add_argument("--keyword", required=True)
    p_imp.add_argument("--limit", type=int, default=20)
    p_imp.add_argument("--sort", type=int, default=2,
                       help="1=relevan 2=jualan 3=harga tinggi 4=harga rendah 5=komisen")
    p_imp.add_argument("--hashtags", default="", help="Hashtag untuk produk diimport, cth '#gadget #murah'")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = load_settings()
    runner = Runner(settings)

    if args.cmd == "run":
        out = runner.run_once(dry_run=args.dry_run or None, product_id=args.product)
        _print_results(out)
        failed = [k for k, v in out.get("results", {}).items() if not v.get("ok")]
        return 1 if failed and len(failed) == len(out["results"]) else 0

    if args.cmd == "daemon":
        runner.daemon()
        return 0

    if args.cmd == "preview":
        for _ in range(args.count):
            _print_results(runner.run_once(dry_run=True))
        return 0

    if args.cmd == "check":
        ok = True
        for name, client in (("Facebook", runner.facebook), ("Threads", runner.threads)):
            if client is None:
                print(f"⚪ {name}: tidak diset / dimatikan")
                continue
            try:
                print(f"✅ {name}: {client.check()}")
            except Exception as e:  # noqa: BLE001
                ok = False
                print(f"❌ {name}: {e}")
        print(f"{'✅' if settings.shopee_enabled else '⚪'} Shopee Affiliate API: "
              f"{'diset' if settings.shopee_enabled else 'tidak diset (pilihan)'}")
        return 0 if ok else 1

    if args.cmd == "refresh-threads-token":
        from .threads import ThreadsClient
        data = ThreadsClient.refresh_token(settings.threads_access_token)
        days = int(data.get("expires_in", 0)) // 86400
        print(f"Token baru (sah {days} hari). Kemas kini THREADS_ACCESS_TOKEN dalam .env / GitHub Secrets:\n")
        print(data["access_token"])
        return 0

    if args.cmd == "import-shopee":
        if not runner.shopee:
            print("Set SHOPEE_APP_ID dan SHOPEE_APP_SECRET dalam .env dahulu.", file=sys.stderr)
            return 1
        products = runner.shopee.search_products(args.keyword, args.limit, args.sort)
        tags = [t if t.startswith("#") else f"#{t}" for t in args.hashtags.split() if t]
        for p in products:
            p.hashtags = tags
        added = append_products(settings.products_file, products)
        print(f"Dijumpai {len(products)} produk, {added} baru ditambah ke {settings.products_file}")
        return 0

    return 1


def _print_results(out: dict) -> None:
    if not out:
        return
    product = out["product"]
    print("=" * 60)
    print(f"Produk: [{product.id}] {product.name}")
    for platform, r in out["results"].items():
        print("-" * 60)
        print(f"{platform.upper()}: {'OK' if r.get('ok') else 'GAGAL: ' + r.get('error', '')}")
        if r.get("caption"):
            print(r["caption"])
        for extra in ("comment", "reply"):
            if r.get(extra):
                print(f"\n[{extra}] {r[extra]}")
    print()


if __name__ == "__main__":
    raise SystemExit(main())
