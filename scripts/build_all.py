"""Run the full data pipeline for the local laws dashboard."""

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent

STEPS = [
    ("build_data.py", "Build LOCUS JSON from Franklin County export"),
    ("crawl_official_sites.py", "Crawl Preston + Franklin County websites"),
    ("build_bundle.py", "Merge ordinance + official source data"),
    ("make_standalone.py", "Generate standalone dashboard HTML"),
]


def run(step: str, label: str) -> None:
    print(f"\n==> {label}")
    subprocess.run([sys.executable, str(SCRIPTS / step)], check=True)


def main() -> None:
    for step, label in STEPS:
        run(step, label)
    print("\nDone. Open apps/local-laws-dashboard/index-standalone.html")


if __name__ == "__main__":
    main()