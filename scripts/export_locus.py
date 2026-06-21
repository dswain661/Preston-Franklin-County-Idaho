"""Export Franklin County, Idaho rows from the LOCUS v1 HuggingFace dataset."""

from pathlib import Path

import pandas as pd

from paths import DATA_EXPORTS, FRANKLIN_CSV, MENTIONS_CSV

PARQUET_URL = (
    "https://huggingface.co/api/datasets/LocalLaws/LOCUS-v1/"
    "parquet/default/train/2.parquet"
)


def main() -> None:
    DATA_EXPORTS.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PARQUET_URL)
    mask = (df["state"].str.lower() == "id") & (df["county"].str.lower() == "franklincounty")
    county = df.loc[mask].copy()
    mentions = county[
        county["header"].str.lower().str.contains("preston", na=False)
        | county["content"].str.lower().str.contains("preston", na=False)
    ].copy()

    county.to_csv(FRANKLIN_CSV, index=False)
    mentions.to_csv(MENTIONS_CSV, index=False)
    print(f"Wrote {FRANKLIN_CSV} ({len(county)} rows)")
    print(f"Wrote {MENTIONS_CSV} ({len(mentions)} rows)")


if __name__ == "__main__":
    main()