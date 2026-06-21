# Preston & Franklin County, Idaho — Citizen Tools

Open-source civic tools for residents of **Preston** and **Franklin County, Idaho**. Making local government, services, and laws easier to find and understand.

**Live tools (in development):**
- [Local Laws Dashboard](apps/local-laws-dashboard/) — search ordinances + official city/county pages
- [Meeting → YouTube](scripts/meeting_publish/) — fixed Zoom join + local record + auto upload (runs on your PC)

**Official sources (always verify):**
- https://www.prestonidaho.net/
- https://www.franklincountyidaho.org/
- https://codelibrary.amlegal.com/codes/franklincountyid/latest/overview

> Educational tools only — not legal advice.

---

## Quick start

```bash
git clone https://github.com/dswain661/Preston-Franklin-County-Idaho.git
cd Preston-Franklin-County-Idaho
pip install -r requirements.txt
python scripts/build_all.py
```

Open **`apps/local-laws-dashboard/index-standalone.html`** in your browser.

### Rebuild only ordinance data (skip crawl)

```bash
python scripts/build_data.py
python scripts/build_bundle.py
python scripts/make_standalone.py
```

### Refresh official website index (~4–6 min)

```bash
python scripts/crawl_official_sites.py
python scripts/build_bundle.py
python scripts/make_standalone.py
```

---

## Repository structure

| Path | Purpose |
|------|---------|
| `apps/` | Citizen-facing tools (one folder per app) |
| `scripts/` | Data pipelines |
| `data/exports/` | Committed CSV snapshots |
| `data/generated/` | Build output (regenerate locally) |
| `docs/ROADMAP.md` | Full vision — tools beyond legal |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for data flow and [docs/ROADMAP.md](docs/ROADMAP.md) for planned tools (permits, meetings, events, GIS, and more).

---

## Contributing

1. Read `docs/ROADMAP.md` and pick a tool or improvement
2. Branch, build under `apps/<name>/`
3. Cite official government URLs in the UI
4. Open a PR

---

## License

Code: MIT (see LICENSE). LOCUS ordinance labels: [CC-BY-NC-4.0](https://huggingface.co/datasets/LocalLaws/LOCUS-v1). Government website content remains under respective public authorities.