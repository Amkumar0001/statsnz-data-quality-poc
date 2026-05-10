from __future__ import annotations

import time
from collections.abc import Generator

import pytest

from src.utils.test_logger import (
    log_section,
    log_test_summary,
    reset_step_counter,
)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, statsnz_site_url: str) -> dict:
    return {
        **browser_context_args,
        "base_url": statsnz_site_url,
        "viewport": {"width": 1366, "height": 900},
        "ignore_https_errors": True,
    }


@pytest.fixture(autouse=True)
def _human_readable_logger(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    reset_step_counter()
    log_section(request.node.name)
    started = time.perf_counter()
    passed = False
    try:
        yield
        passed = True
    finally:
        duration_ms = (time.perf_counter() - started) * 1000
        log_test_summary(request.node.name, passed, duration_ms)
