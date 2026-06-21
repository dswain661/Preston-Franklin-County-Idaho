"""Merge LOCUS ordinance data with crawled official website sources."""

import json

from paths import BUNDLE_JSON, DATA_GENERATED, LOCUS_JSON, OFFICIAL_JSON


def main() -> None:
    locus = json.loads(LOCUS_JSON.read_text(encoding="utf-8"))
    official = json.loads(OFFICIAL_JSON.read_text(encoding="utf-8"))

    official_pages = []
    for page in official["all_pages"]:
        official_pages.append({
            "url": page["url"],
            "title": page["title"],
            "excerpt": page["excerpt"],
            "source": page["source"],
            "source_key": page["source_key"],
            "relevance": page.get("relevance", 0),
            "external": page.get("external", False),
            "search_text": f"{page['title']} {page['excerpt']} {page['url']}".lower(),
        })

    bundle = {
        **locus,
        "official_sources": {
            "crawled_at": official["crawled_at"],
            "references": official["references"],
            "preston_count": official["sites"]["preston"]["pages_crawled"],
            "county_count": official["sites"]["franklin_county"]["pages_crawled"],
            "key_links": {
                "preston": official["sites"]["preston"]["key_links"][:15],
                "franklin_county": official["sites"]["franklin_county"]["key_links"][:15],
            },
            "pages": official_pages,
        },
    }

    bundle["meta"]["disclaimer"] = (
        "This dashboard combines machine-labeled ordinance text (LOCUS dataset) with crawled content "
        "from official City of Preston and Franklin County websites. Labels are not legal advice. "
        "Always verify against official sources and qualified counsel."
    )

    DATA_GENERATED.mkdir(parents=True, exist_ok=True)
    BUNDLE_JSON.write_text(json.dumps(bundle, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {BUNDLE_JSON}")
    print(f"  ordinances: {len(bundle['records'])}")
    print(f"  official pages: {len(official_pages)}")


if __name__ == "__main__":
    main()