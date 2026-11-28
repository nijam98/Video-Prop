"""Shopee Affiliate Open API (pilihan).

Perlu App ID & Secret daripada Shopee Affiliate (affiliate.shopee.com.my → Open API).
Digunakan untuk:
  * import produk mengikut kata kunci (productOfferV2)
  * jana short link affiliate dengan sub_id per platform (generateShortLink)
"""

from __future__ import annotations

import hashlib
import json
import time

import requests

from .http import ApiError
from .products import Product


class ShopeeAffiliate:
    def __init__(self, app_id: str, secret: str,
                 url: str = "https://open-api.affiliate.shopee.com.my/graphql",
                 session: requests.Session | None = None):
        self.app_id = app_id
        self.secret = secret
        self.url = url
        self.session = session or requests.Session()

    def _query(self, query: str, variables: dict | None = None) -> dict:
        body: dict = {"query": query}
        if variables:
            body["variables"] = variables
        payload = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
        ts = str(int(time.time()))
        sig = hashlib.sha256(f"{self.app_id}{ts}{payload}{self.secret}".encode()).hexdigest()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SHA256 Credential={self.app_id}, Timestamp={ts}, Signature={sig}",
        }
        resp = self.session.post(self.url, data=payload.encode(), headers=headers, timeout=60)
        data = resp.json()
        if data.get("errors"):
            raise ApiError(f"Shopee API: {data['errors'][0].get('message', data['errors'])}")
        return data.get("data", {})

    def short_link(self, origin_url: str, sub_ids: list[str] | None = None) -> str:
        q = ("mutation($url:String!,$subs:[String]){"
             "generateShortLink(input:{originUrl:$url,subIds:$subs}){shortLink}}")
        data = self._query(q, {"url": origin_url, "subs": sub_ids or []})
        return data["generateShortLink"]["shortLink"]

    def search_products(self, keyword: str, limit: int = 20, sort_type: int = 2) -> list[Product]:
        """sort_type: 1=relevan, 2=jualan terbanyak, 3=harga tinggi, 4=harga rendah, 5=komisen tertinggi."""
        q = ("query($kw:String,$limit:Int,$sort:Int){"
             "productOfferV2(keyword:$kw,limit:$limit,sortType:$sort){"
             "nodes{itemId productName priceMin priceMax imageUrl offerLink productLink "
             "commissionRate sales ratingStar shopName}}}")
        data = self._query(q, {"kw": keyword, "limit": limit, "sort": sort_type})
        out = []
        for n in data.get("productOfferV2", {}).get("nodes", []):
            out.append(Product(
                id=str(n.get("itemId")),
                name=n.get("productName", ""),
                price=str(n.get("priceMin") or ""),
                original_price="",
                affiliate_link=n.get("offerLink") or n.get("productLink", ""),
                image_url=n.get("imageUrl", ""),
                hashtags=[],
            ))
        return out
