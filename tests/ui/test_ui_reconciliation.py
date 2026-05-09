"""End-to-end UI ↔ API reconciliation.

This is the gold-standard data-pipeline regression test:
  1. Drive the public UI to download a CSV.
  2. Pull the same dataset via the OData API.
  3. Reconcile row counts, schema, and value sums.

The download flow on Stats NZ uses session cookies and varies by dataset,
so this test is `skipped` by default and stands as a documented pattern.
Replace `_download_csv_via_ui` with the real selectors when you're ready
to wire it up against a specific dataset.
"""

from __future__ import annotations

import pytest


@pytest.mark.ui
@pytest.mark.reconciliation
@pytest.mark.live
@pytest.mark.skip(reason="placeholder — wire up against a real Stats NZ dataset download")
def test_ui_csv_matches_api(page, stats_nz_client) -> None:
    raise NotImplementedError
