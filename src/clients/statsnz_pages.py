from __future__ import annotations

import re
from dataclasses import dataclass

from playwright.sync_api import Page, expect


@dataclass
class StatsNZHomePage:
    """Page Object for the Stats NZ public homepage and search.

    Uses role-/label-based selectors for resilience — IDs and class names
    on this site change frequently across redesigns.
    """

    page: Page
    base_url: str

    def open(self) -> StatsNZHomePage:
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        return self

    def expect_loaded(self) -> StatsNZHomePage:
        expect(self.page).to_have_title(re.compile(r"stats", re.IGNORECASE))
        return self

    def search(self, term: str) -> StatsNZSearchResultsPage:
        search_box = self.page.get_by_role("searchbox").first
        search_box.fill(term)
        search_box.press("Enter")
        return StatsNZSearchResultsPage(self.page)


@dataclass
class StatsNZSearchResultsPage:
    page: Page

    def expect_results(self, term: str) -> StatsNZSearchResultsPage:
        self.page.wait_for_load_state("domcontentloaded")
        expect(self.page).to_have_url(re.compile(r"search", re.IGNORECASE))
        body_text = self.page.locator("body").inner_text().lower()
        assert term.lower() in body_text, f"expected '{term}' in results page body"
        return self
