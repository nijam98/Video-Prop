#!/usr/bin/env python3
"""Terbitkan post teks ke Facebook Page melalui Graph API.

Perlu Page access token (kebenaran pages_manage_posts), disuntik oleh proxy sesi
ke graph.facebook.com, atau set FB_PAGE_TOKEN jika dijalankan di tempat lain.
Nota: API Facebook TIDAK membenarkan post ke profil peribadi atau group — Page sahaja.

Guna:
  python3 threads/fb_post.py --check
  python3 threads/fb_post.py --file post.txt [--dry-run]
"""
import argparse, json, os, sys, urllib.parse, urllib.request, urllib.error

API = "https://graph.facebook.com"


def call(method, path, params=None):
    params = dict(params or {})
    url = f"{API}/{path}"
    data = None
    if method == "GET":
        if params:
            url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    token = os.environ.get("FB_PAGE_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} {path}: {e.read().decode(errors='replace')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.check:
        print(json.dumps(call("GET", "me", {"fields": "id,name"}), indent=2))
        return
    if not a.file:
        ap.error("--file atau --check diperlukan")

    text = open(a.file, encoding="utf-8").read().strip()
    if not text:
        sys.exit("Post kosong.")
    if a.dry_run:
        print(f"[dry-run] {len(text)} aksara:\n{text}")
        return

    res = call("POST", "me/feed", {"message": text})
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
