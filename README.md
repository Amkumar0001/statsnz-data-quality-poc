# statsnz-data-quality-poc

A small-but-credible data-quality test framework targeting **Stats NZ** open
datasets. Built to demonstrate Python/pytest fluency, data-pipeline testing
patterns, and a pragmatic mix of tools for a public-sector data team.

## What it covers

| Layer | Tooling | What's tested |
|---|---|---|
| Schema contract | Pandera | Column existence, types, nullability, regex format, primary-key uniqueness |
| Data quality | pandas + pytest-parametrize | Completeness, validity, uniqueness, consistency, timeliness, accuracy |
| Expectations suite | Great Expectations 1.x | The same dimensions, run via an ephemeral GX context — produces auditable validation results |
| Reconciliation | pandas merge | Cross-source row counts, missing rows on either side, numeric sum drift |
| API smoke | requests | Stats NZ OData endpoint + data.govt.nz CKAN endpoint |
| UI | Playwright (sync) | Public Stats NZ search flow, Page Object pattern |

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         pytest test suite                          │
├──────────────┬──────────────┬─────────────────┬────────────────────┤
│ tests/api/   │ tests/data/  │ tests/ui/       │ tests/test_imports │
│ live smoke   │ schema +     │ Playwright +    │ packaging sanity   │
│              │ quality +    │ Page Objects    │                    │
│              │ GE +         │                 │                    │
│              │ reconcile    │                 │                    │
└──────┬───────┴──────┬───────┴────────┬────────┴────────────────────┘
       │              │                │
       ▼              ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ src/clients  │ │ src/validat. │ │ src/utils    │
│ StatsNZ +    │ │ Pandera      │ │ data_loader, │
│ CKAN +       │ │ schema +     │ │ reconciliat. │
│ Page Objects │ │ GX suite     │ │              │
└──────┬───────┘ └──────────────┘ └──────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Stats NZ OData │ CKAN │ stats.govt.nz │
└──────────────────────────────────────┘
```

## Quick start

```bash
# 1. install deps with uv
uv sync --all-extras --dev
uv run playwright install chromium

# 2. (optional) plug in a Stats NZ API key for live tests
cp .env.example .env
# edit .env and paste your key

# 3. run the offline suite (always passes against the committed snapshot)
uv run pytest -m "not live"

# 4. run a specific dimension
uv run pytest -m schema
uv run pytest -m quality
uv run pytest -m reconciliation
uv run pytest -m expectations

# 5. run live tests (needs network + API key)
uv run pytest -m live
```

## Test markers

| Marker | Purpose |
|---|---|
| `smoke` | Fast sanity check that the suite is wired up |
| `schema` | Pandera contract validation |
| `quality` | DAMA-DMBOK data quality dimensions |
| `expectations` | Great Expectations suite runs |
| `reconciliation` | Cross-source row/value comparison |
| `ui` | Playwright UI tests |
| `live` | Hits external services — opt-in only |
| `slow` | Takes >5s — opt-out for fast iteration |

## Project layout

```
statsnz-dq/
├── data/snapshots/        committed CSV fixtures (real-shaped CPI data)
├── src/
│   ├── clients/           StatsNZ + CKAN HTTP clients, Playwright Page Objects
│   ├── validators/        Pandera schema, Great Expectations suite
│   └── utils/             data loader, reconciliation engine
├── tests/
│   ├── api/               live API tests (skip without key)
│   ├── data/              offline schema, quality, GE, reco tests
│   ├── ui/                Playwright UI tests
│   └── conftest.py        shared fixtures, .env loading
├── .github/workflows/     CI: offline suite on every push, live on dispatch
└── pyproject.toml         deps + pytest config + ruff config
```

## Why these tools

- **pytest** — fixtures + markers + parametrize give better test
  composition than Mocha/Jest's hook-based model.
- **Pandera** — fast, declarative schema checks; ideal for catching
  schema drift on every CI run.
- **Great Expectations** — produces auditable validation results and HTML
  data docs that data engineers and stakeholders can read directly.
  Industry standard at most NZ public-sector data teams.
- **Playwright** — auto-waiting + tracing make it materially more
  reliable than Selenium for modern SPAs; same Page Object patterns
  port over.
- **uv** — fast, reproducible Python dependency management.

## What's deliberately not here

- Full ETL or transformation logic (this POC only validates landed data).
- An auth flow (Stats NZ Open Data API uses a single subscription header).
- A real downloaded dataset (the committed CSV is realistic-shaped sample
  data so the suite runs offline; swap the loader for a real download
  in `src/utils/data_loader.py`).
