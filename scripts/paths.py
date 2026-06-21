from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_EXPORTS = ROOT / "data" / "exports"
DATA_GENERATED = ROOT / "data" / "generated"
DASHBOARD_APP = ROOT / "apps" / "local-laws-dashboard"

FRANKLIN_CSV = DATA_EXPORTS / "franklin_county_idaho.csv"
MENTIONS_CSV = DATA_EXPORTS / "preston_mentions.csv"
LOCUS_JSON = DATA_GENERATED / "data.json"
OFFICIAL_JSON = DATA_GENERATED / "official_sources.json"
BUNDLE_JSON = DATA_GENERATED / "dashboard_bundle.json"