# Changelog

All notable changes to this POC. Newest first.

## 2026-05-10

- Project skeleton: uv-managed Python 3.11 project, pytest config with
  strict markers, ruff lint config.
- `src/clients/`: Stats NZ OData client, data.govt.nz CKAN client,
  Playwright Page Objects for the public Stats NZ search flow.
- `src/validators/`: Pandera schema for the CPI dataset, Great
  Expectations suite covering the same dimensions.
- `src/utils/`: data loader with explicit dtype handling (Period values
  like `2024.06` would otherwise be coerced to float), reconciliation
  engine with row-overlap and column-sum comparison.
- `tests/data/`: 28 offline tests across schema, quality, expectations,
  and reconciliation. All pass on committed sample snapshot.
- `tests/api/`: live smoke tests against Stats NZ OData (skips without
  key) and data.govt.nz CKAN (no auth).
- `tests/ui/`: Playwright homepage + search UI test against the public
  Stats NZ site, with role-based selectors and the human-readable
  step logger wired through the Page Objects.
- GitHub Actions workflow: offline suite on every push, live suite
  on workflow_dispatch (uses `STATS_NZ_API_KEY` secret).
