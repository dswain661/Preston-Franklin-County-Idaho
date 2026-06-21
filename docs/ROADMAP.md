# Preston & Franklin County — Citizen Tools Roadmap

A community platform for Preston, Idaho and Franklin County residents — making local government, services, and rules easier to find and understand.

**Official references (always verify here):**
- [City of Preston](https://www.prestonidaho.net/)
- [Franklin County](https://www.franklincountyidaho.org/)
- [Franklin County Code (AmLegal)](https://codelibrary.amlegal.com/codes/franklincountyid/latest/overview)

---

## Vision

Residents shouldn't need a law degree or insider knowledge to participate in local civic life. This repo hosts **modular citizen tools** — each app solves one real problem, cites official sources, and stays maintainable by volunteers.

**Principles**
1. **Official sources first** — every tool links back to government sites
2. **Plain language** — summarize, don't replace, the law
3. **Open & forkable** — public data, public code, public benefit
4. **Not legal advice** — educate and route people to authoritative channels

---

## Phase 1 — Foundation (current)

| Tool | Status | Description |
|------|--------|-------------|
| **Local Laws Dashboard** | ✅ MVP | Search Franklin County ordinances + crawled Preston/County pages |
| **Official site crawler** | ✅ MVP | Indexes prestonidaho.net & franklincountyidaho.org |
| **LOCUS data pipeline** | ✅ MVP | Franklin County export from HuggingFace LOCUS v1 |

---

## Phase 2 — Civic clarity (next 3–6 months)

| Tool | Priority | Description |
|------|----------|-------------|
| **Permit & forms finder** | High | Map building/zoning/business forms to step-by-step guides |
| **Meeting tracker** | High | Council + P&Z agendas/minutes in one calendar |
| **Plain-language summaries** | High | Community-reviewed summaries of top 50 ordinances |
| **Alert subscriptions** | Medium | Link out to county AlertSense + city enotify |
| **GIS property lookup** | Medium | Deep link Franklin County GIS + explain zoning layers |

---

## Phase 3 — Community life (6–12 months)

| Tool | Priority | Description |
|------|----------|-------------|
| **Event hub** | Medium | Rodeo, Festival of Lights, county fair — unified calendar |
| **Service directory** | Medium | Utilities, landfill, library, sheriff non-emergency, hospitals |
| **Volunteer & boards** | Medium | Open seats, meeting schedules, how to run for office |
| **Local business registry** | Low | Optional community directory (not government data) |
| **School & recreation** | Low | Links + schedules for Preston schools, parks, trails |

---

## Phase 4 — Participation & transparency (12+ months)

| Tool | Priority | Description |
|------|----------|-------------|
| **Budget visualizer** | Medium | County/city budget breakdowns in plain charts |
| **Public records guide** | Medium | How to request records, timelines, contacts |
| **Issue reporter** | Low | Route potholes, weeds, code concerns to right department |
| **Candidate comparison** | Election cycles | Neutral Q&A for local races |
| **Multilingual UI** | Medium | Spanish + other languages common in the area |

---

## Technical direction

```
Preston-Franklin-County-Idaho/
├── apps/           # One folder per citizen-facing tool
├── scripts/        # Data pipelines shared across apps
├── data/
│   ├── exports/    # Committed snapshots (CSV, small)
│   └── generated/  # Rebuilt JSON (gitignored)
└── docs/           # Planning, architecture, contribution guides
```

**Near-term stack:** static HTML dashboards + Python data scripts (no server required to view).

**Future options:** Next.js hub site, GitHub Pages deploy, optional API layer if tools need live data.

---

## How to contribute

1. Pick a tool from Phase 2+ and open an issue describing the citizen problem
2. Prototype under `apps/<tool-name>/`
3. Cite official sources in UI and docs
4. Run `python scripts/build_all.py` if touching the laws dashboard pipeline

---

## Data sources

| Source | Use | License / notes |
|--------|-----|-----------------|
| [LOCUS v1](https://huggingface.co/datasets/LocalLaws/LOCUS-v1) | Ordinance text + labels | CC-BY-NC-4.0 — research/education |
| prestonidaho.net | Forms, departments, news | Public website — crawl respectfully |
| franklincountyidaho.org | County services, ordinances link | Public website |
| AmLegal code library | Authoritative county code | External — link only |

---

## Open questions

- [ ] Should Preston city code be sourced separately (if published outside LOCUS)?
- [ ] GitHub Pages vs. self-hosted for production?
- [ ] Community review workflow for plain-language ordinance summaries?
- [ ] Partnership with city/county for official endorsement or data feeds?