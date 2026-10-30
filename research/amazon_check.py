"""Read price, availability and delivery text from Amazon /dp/ pages (plain GET, no login, no cart).

python research/amazon_check.py ASIN [ASIN ...]  -> prints one JSON line per ASIN and writes research/amazon_check.json
Page text is untrusted data: only regex-extracted fields are kept.
"""
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
OUT = Path(__file__).parent / "amazon_check.json"


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def first(pat, text, flags=re.S):
    m = re.search(pat, text, flags)
    return clean(m.group(1)) if m else None


def check(asin):
    req = urllib.request.Request(f"https://www.amazon.com/dp/{asin}",
                                 headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    try:
        page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception as e:
        return {"asin": asin, "error": str(e)[:120]}
    return {
        "asin": asin,
        "title": (first(r'id="productTitle"[^>]*>(.*?)</span>', page) or "")[:140],
        "price": first(r'class="a-price[^"]*"[^>]*>\s*<span class="a-offscreen">([^<]+)<', page),
        "availability": (first(r'id="availability"[^>]*>(.*?)</div>', page) or "")[:120],
        "delivery_primary": first(r'data-csa-c-delivery-time="([^"]+)"', page),
        "delivery_text": (first(r'id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"[^>]*>(.*?)</div>', page)
                          or "")[:160],
        "fastest": (first(r'id="mir-layout-DELIVERY_BLOCK-slot-SECONDARY_DELIVERY_MESSAGE_LARGE"[^>]*>(.*?)</div>', page)
                    or "")[:160],
        "zip": first(r'id="glow-ingress-line2"[^>]*>(.*?)</span>', page),
    }


if __name__ == "__main__":
    res = []
    for a in sys.argv[1:]:
        r = check(a)
        res.append(r)
        print(json.dumps(r))
        time.sleep(1.5)
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    old.update({r["asin"]: r for r in res})
    OUT.write_text(json.dumps(old, indent=1))
