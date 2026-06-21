import shutil
from pathlib import Path

from paths import BUNDLE_JSON, DASHBOARD_APP, DATA_GENERATED, LOCUS_JSON

FETCH_BLOCK = """    fetch('dashboard_bundle.json')
      .then(r => r.json())
      .then(init)
      .catch(() => fetch('data.json').then(r => r.json()).then(init))
      .catch(() => {
        document.getElementById('disclaimer').textContent =
          'Could not load dashboard data. Run build_bundle.py or open index-standalone.html.';
      });"""


def main() -> None:
    bundle_path = BUNDLE_JSON if BUNDLE_JSON.exists() else LOCUS_JSON
    data = bundle_path.read_text(encoding="utf-8")
    html = (DASHBOARD_APP / "index.html").read_text(encoding="utf-8")

    if FETCH_BLOCK not in html:
        raise SystemExit("Expected fetch block not found in index.html")

    out = DASHBOARD_APP / "index-standalone.html"
    out.write_text(html.replace(FETCH_BLOCK, f"    init({data});"), encoding="utf-8")

    if BUNDLE_JSON.exists():
        shutil.copy2(BUNDLE_JSON, DASHBOARD_APP / "dashboard_bundle.json")

    print(f"Created {out}")
    print("Open index-standalone.html in a browser (no server required).")


if __name__ == "__main__":
    main()