from __future__ import annotations

import re
from dataclasses import dataclass

from playwright.sync_api import Page, expect

from src.utils.test_logger import (
    log_click,
    log_navigate,
    log_set_value,
    log_verify,
    log_wait_for_element,
    log_wait_for_element_found,
)


@dataclass
class StatsNZHomePage:
    """Page Object for the Stats NZ public homepage and search.

    Uses role-/label-based selectors for resilience — IDs and class names
    on this site change frequently across redesigns. Each public method
    emits human-readable step logs through src.utils.test_logger so the
    test transcript reads like a narrative.
    """

    page: Page
    base_url: str

    def open(self) -> StatsNZHomePage:
        log_navigate(self.base_url)
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        return self

    def expect_loaded(self) -> StatsNZHomePage:
        log_wait_for_element("Stats NZ homepage", timeout_ms=30_000)
        expect(self.page).to_have_title(re.compile(r"stats", re.IGNORECASE))
        log_wait_for_element_found("Stats NZ homepage")
        return self

    def search(self, term: str) -> StatsNZSearchResultsPage:
        log_set_value("search box", term)
        search_box = self.page.get_by_role("searchbox").first
        search_box.fill(term)
        log_click("search submit (Enter key)")
        search_box.press("Enter")
        return StatsNZSearchResultsPage(self.page)


@dataclass
class StatsNZSearchResultsPage:
    page: Page

    def expect_results(self, term: str) -> StatsNZSearchResultsPage:
        log_wait_for_element("search results page", timeout_ms=30_000)
        self.page.wait_for_load_state("domcontentloaded")
        expect(self.page).to_have_url(re.compile(r"search", re.IGNORECASE))
        log_wait_for_element_found("search results page")
        body_text = self.page.locator("body").inner_text().lower()
        assert term.lower() in body_text, f"expected '{term}' in results page body"
        log_verify(f"search results contain '{term}'", visible=True)
        return self
