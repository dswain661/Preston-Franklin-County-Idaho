import json
import re

import pandas as pd

from paths import DATA_GENERATED, FRANKLIN_CSV, LOCUS_JSON, MENTIONS_CSV

TOPIC_LABELS = {
    "Zoning": "Land Use & Zoning",
    "Business": "Business & Commerce",
    "Nuisance": "Nuisance & Quality of Life",
    "Buildings": "Buildings & Construction",
    "Other": "General Regulations",
}

FUNCTION_LABELS = {
    "Rules": "Rules — what you must or must not do",
    "Enforcement": "Enforcement — penalties & violations",
    "Context": "Background — definitions & scope",
    "Process": "Process — how government operates",
}


def clean_header(h: str) -> str:
    return re.sub(r"^#+\s*", "", str(h)).strip()


def excerpt(text: str, n: int = 280) -> str:
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def main() -> None:
    df = pd.read_csv(FRANKLIN_CSV)
    pd.read_csv(MENTIONS_CSV)  # validate export exists

    records = []
    for _, row in df.iterrows():
        header = clean_header(row["header"])
        content = str(row["content"])
        topic = row["topic"] if pd.notna(row["topic"]) else None
        records.append(
            {
                "id": len(records) + 1,
                "header": header,
                "excerpt": excerpt(content),
                "content": content,
                "is_substantive": bool(row["is_substantive"]),
                "function": row["function"],
                "function_label": FUNCTION_LABELS.get(row["function"], row["function"]),
                "topic": topic,
                "topic_label": TOPIC_LABELS.get(topic, "Procedural / Background"),
                "mentions_preston": "preston" in header.lower() or "preston" in content.lower(),
                "enforcement_discretion": round(float(row["enforcement_discretion"]), 2),
                "opacity": round(float(row["opacity"]), 2),
                "paternalism": round(float(row["paternalism"]), 2),
                "problem_salience": round(float(row["problem_salience"]), 2),
                "word_count": len(content.split()),
            }
        )

    substantive = [r for r in records if r["is_substantive"]]
    preston_rows = [r for r in records if r["mentions_preston"]]

    by_function = df["function"].value_counts().to_dict()
    by_topic = {
        TOPIC_LABELS.get(k, k or "Procedural"): int(v)
        for k, v in df["topic"].value_counts(dropna=False).to_dict().items()
        if pd.notna(k)
    }
    by_topic["Procedural / Background"] = int(df["topic"].isna().sum())

    payload = {
        "meta": {
            "jurisdiction": "Franklin County, Idaho",
            "city_focus": "Preston",
            "state": "Idaho",
            "total_ordinances": len(records),
            "substantive_count": len(substantive),
            "preston_mentions": len(preston_rows),
            "disclaimer": (
                "This dashboard summarizes publicly available local law text from the LOCUS dataset. "
                "Labels are machine-assisted and are not legal advice. Always consult official county "
                "sources and qualified counsel for legal decisions."
            ),
        },
        "summary": {
            "by_function": {FUNCTION_LABELS.get(k, k): int(v) for k, v in by_function.items()},
            "by_topic": by_topic,
            "substantive_pct": round(100 * len(substantive) / len(records), 1),
            "avg_opacity": round(df["opacity"].mean(), 2),
            "avg_word_count": round(df["content"].str.split().str.len().mean()),
            "hardest_to_read": sorted(records, key=lambda r: r["opacity"], reverse=True)[:8],
            "most_enforced": sorted(
                [r for r in substantive if r["function"] in ("Rules", "Enforcement")],
                key=lambda r: r["enforcement_discretion"],
                reverse=True,
            )[:8],
        },
        "topic_guides": [
            {
                "key": "Zoning",
                "title": "Land Use & Zoning",
                "plain": "Rules about what can be built where — homes, businesses, farms, and how land is divided.",
                "count": int((df["topic"] == "Zoning").sum()),
            },
            {
                "key": "Business",
                "title": "Business & Commerce",
                "plain": "Licenses, permits, and operating rules for local businesses.",
                "count": int((df["topic"] == "Business").sum()),
            },
            {
                "key": "Nuisance",
                "title": "Nuisance & Quality of Life",
                "plain": "Noise, waste, property upkeep, and behaviors that affect neighbors.",
                "count": int((df["topic"] == "Nuisance").sum()),
            },
            {
                "key": "Buildings",
                "title": "Buildings & Construction",
                "plain": "Building standards, safety codes, and construction requirements.",
                "count": int((df["topic"] == "Buildings").sum()),
            },
            {
                "key": "Other",
                "title": "General Regulations",
                "plain": "Cross-cutting rules that don't fit a single category.",
                "count": int((df["topic"] == "Other").sum()),
            },
        ],
        "preston_highlight": [
            {
                "header": r["header"],
                "excerpt": r["excerpt"],
                "function": r["function"],
                "topic_label": r["topic_label"],
            }
            for r in preston_rows
        ],
        "records": records,
    }

    DATA_GENERATED.mkdir(parents=True, exist_ok=True)
    LOCUS_JSON.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {LOCUS_JSON} ({len(records)} records)")


if __name__ == "__main__":
    main()