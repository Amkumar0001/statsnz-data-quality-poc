"""Playwright UI smoke against stats.govt.nz.

Marked `live` because the public site is outside our control — selectors
and copy can change. Run locally before each release; skip in offline CI.
"""

from __future__ import annotations

import pytest

from src.clients.statsnz_pages import StatsNZHomePage


@pytest.mark.ui
@pytest.mark.live
def test_homepage_loads(page, statsnz_site_url: str) -> None:
    home = StatsNZHomePage(page=page, base_url=statsnz_site_url).open()
    home.expect_loaded()


@pytest.mark.ui
@pytest.mark.live
def test_search_returns_results(page, statsnz_site_url: str) -> None:
    home = StatsNZHomePage(page=page, base_url=statsnz_site_url).open()
    results = home.search("CPI")
    results.expect_results("CPI")
