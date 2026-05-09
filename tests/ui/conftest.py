from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, statsnz_site_url: str) -> dict:
    return {
        **browser_context_args,
        "base_url": statsnz_site_url,
        "viewport": {"width": 1366, "height": 900},
        "ignore_https_errors": True,
    }
