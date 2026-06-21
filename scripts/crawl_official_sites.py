"""
Crawl official Preston and Franklin County websites for civic knowledge sources.
Respects same-domain scope and stores structured page index with references.
"""

from __future__ import annotations

import json
import re
import time
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import Request, urlopen

from paths import DATA_GENERATED, OFFICIAL_JSON

OUT = OFFICIAL_JSON

SITES = {
    "preston": {
        "name": "City of Preston",
        "base_url": "https://www.prestonidaho.net/",
        "root_domain": "prestonidaho.net",
    },
    "franklin_county": {
        "name": "Franklin County, Idaho",
        "base_url": "https://www.franklincountyidaho.org/",
        "root_domain": "franklincountyidaho.org",
    },
}

MAX_PAGES_PER_SITE = 120
REQUEST_DELAY = 0.35
TIMEOUT = 20

SKIP_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico",
    ".pdf", ".zip", ".doc", ".docx", ".xls", ".xlsx", ".css", ".js",
    ".mp4", ".mp3", ".woff", ".woff2", ".ttf",
}

PRIORITY_KEYWORDS = [
    "ordinance", "code", "zoning", "planning", "permit", "license",
    "law", "regulation", "municipal", "city hall", "council",
    "agenda", "minutes", "form", "application", "fee", "utility",
    "building", "nuisance", "animal", "parking", "sheriff", "court",
    "election", "tax", "gis", "map", "contact", "department",
]


class LinkTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.title = ""
        self._in_title = False
        self._in_script = False
        self._in_style = False
        self._skip_tags = {"script", "style", "noscript"}
        self._block_tags = {
            "p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6",
            "tr", "td", "th", "br", "section", "article",
        }
        self._text_parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        if tag in self._skip_tags:
            if tag == "script":
                self._in_script = True
            if tag == "style":
                self._in_style = True
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)
        if tag in self._block_tags:
            self._text_parts.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        if tag == "script":
            self._in_script = False
        if tag == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._in_script or self._in_style:
            return
        if self._in_title:
            self.title += data
        else:
            self._text_parts.append(data)

    @property
    def text(self) -> str:
        raw = "".join(self._text_parts)
        raw = re.sub(r"\s+", " ", raw)
        return raw.strip()


def fetch(url: str) -> tuple[str | None, str | None]:
    try:
        req = Request(
            url,
            headers={
                "User-Agent": "CivicLawDashboard/1.0 (+local public-interest research)",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        with urlopen(req, timeout=TIMEOUT) as resp:
            ctype = resp.headers.get("Content-Type", "")
            if "text/html" not in ctype and "application/xhtml" not in ctype:
                return None, f"non-html:{ctype}"
            html = resp.read().decode("utf-8", errors="replace")
            return html, None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def normalize_url(base: str, href: str) -> str | None:
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    abs_url = urljoin(base, href)
    abs_url, _ = urldefrag(abs_url)
    parsed = urlparse(abs_url)
    if parsed.scheme not in ("http", "https"):
        return None
    path = parsed.path.lower()
    for ext in SKIP_EXTENSIONS:
        if path.endswith(ext):
            return None
    return abs_url


def same_site(url: str, root_domain: str) -> bool:
    host = urlparse(url).netloc.lower().replace("www.", "")
    return host == root_domain or host.endswith("." + root_domain)


def clean_title(title: str, url: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    if title:
        return title
    path = urlparse(url).path.strip("/") or "home"
    return path.replace("_", " ").replace("/", " - ").title()


def excerpt(text: str, n: int = 320) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rstrip() + "…"


def relevance_score(title: str, text: str, url: str) -> int:
    blob = f"{title} {text} {url}".lower()
    return sum(2 if kw in title.lower() else 1 for kw in PRIORITY_KEYWORDS if kw in blob)


def crawl_site(site_key: str, config: dict) -> dict:
    base = config["base_url"]
    domain = config["root_domain"]
    seen: set[str] = set()
    queue: deque[str] = deque([base])
    pages: list[dict] = []
    errors: list[dict] = []

    while queue and len(pages) < MAX_PAGES_PER_SITE:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)

        html, err = fetch(url)
        time.sleep(REQUEST_DELAY)
        if err or not html:
            errors.append({"url": url, "error": err or "empty"})
            continue

        parser = LinkTextParser()
        try:
            parser.feed(html)
        except Exception as exc:  # noqa: BLE001
            errors.append({"url": url, "error": str(exc)})
            continue

        title = clean_title(parser.title, url)
        text = parser.text
        if len(text) < 40 and url != base:
            continue

        page = {
            "url": url,
            "title": title,
            "excerpt": excerpt(text),
            "text": text[:12000],
            "word_count": len(text.split()),
            "relevance": relevance_score(title, text, url),
            "source": config["name"],
            "source_key": site_key,
        }
        pages.append(page)

        for href in parser.links:
            nxt = normalize_url(url, href)
            if not nxt or nxt in seen:
                continue
            if same_site(nxt, domain):
                queue.append(nxt)
            elif any(host in nxt for host in ("amlegal.com", "revize.com")):
                # Important external code/agenda hosts referenced by county site
                if nxt not in seen:
                    seen.add(nxt)
                    pages.append({
                        "url": nxt,
                        "title": f"Referenced: {urlparse(nxt).path.split('/')[-1] or nxt}",
                        "excerpt": f"External official resource linked from {config['name']}.",
                        "text": f"Official external resource referenced by {config['name']}: {nxt}",
                        "word_count": 0,
                        "relevance": 10 if "amlegal" in nxt else 6,
                        "source": config["name"],
                        "source_key": site_key,
                        "external": True,
                    })

    pages.sort(key=lambda p: (-p["relevance"], p["title"]))
    return {
        "site": config["name"],
        "base_url": base,
        "pages_crawled": len(pages),
        "errors": errors[:20],
        "pages": pages,
        "key_links": [p for p in pages if p.get("relevance", 0) >= 4][:25],
    }


def main() -> None:
    payload = {
        "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sites": {},
        "all_pages": [],
        "references": {
            "preston": "https://www.prestonidaho.net/",
            "franklin_county": "https://www.franklincountyidaho.org/",
            "county_ordinances": "https://codelibrary.amlegal.com/codes/franklincountyid/latest/overview",
        },
    }

    for key, cfg in SITES.items():
        print(f"Crawling {cfg['name']}...", flush=True)
        result = crawl_site(key, cfg)
        payload["sites"][key] = result
        payload["all_pages"].extend(result["pages"])
        print(f"  -> {result['pages_crawled']} pages", flush=True)

    payload["all_pages"].sort(key=lambda p: (-p.get("relevance", 0), p["title"]))
    DATA_GENERATED.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(payload['all_pages'])} total pages)")


if __name__ == "__main__":
    main()