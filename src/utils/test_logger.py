"""Human-readable test logger.

Python port of the TypeScript logger pattern published in
"Building a Human-Readable Logger Utility for Mobile E2E Test
Automation" (medium.com/@Amkumar001, Jan 2026).

Same shape as the original — module-level functions, no class —
so callers can ``from src.utils.test_logger import log_click,
log_section`` without instantiating anything. Zero external
dependencies; ANSI codes are written directly to stdout.

Hierarchy:

    Section   ─ logical grouping (e.g. "User Authentication")
      Step    ─ a single user action with timestamp + emoji
        SubStep   ─ outcome of the step ("…is now displayed")
        Detail    ─ raw context / error message

Run any test that uses these helpers in a colour-capable terminal
to see the output. Pytest captures stdout by default — pass ``-s``
to keep colours streaming live, or look at the captured stdout block
in the failure report.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Literal, ParamSpec, TypeVar

LogCategory = Literal[
    "scroll",
    "keyboard",
    "click",
    "input",
    "wait",
    "verify",
    "context",
    "navigation",
    "navigate",
    "element",
    "gesture",
    "info",
    "warning",
    "success",
    "error",
    "extract",
    "schema",
    "quality",
    "reconciliation",
]

# ---------------------------------------------------------------------------
# ANSI colour codes
# ---------------------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
GRAY = "\033[90m"
RED = "\033[31m"

_COLOUR_MAP: dict[str, str] = {
    "scroll": BLUE,
    "keyboard": MAGENTA,
    "click": CYAN,
    "input": GREEN,
    "wait": YELLOW,
    "verify": GREEN,
    "context": GRAY,
    "navigation": BLUE,
    "navigate": BLUE,
    "element": CYAN,
    "gesture": MAGENTA,
    "info": CYAN,
    "warning": YELLOW,
    "success": GREEN,
    "error": RED,
    "extract": MAGENTA,
    "schema": MAGENTA,
    "quality": CYAN,
    "reconciliation": BLUE,
}

_EMOJI_MAP: dict[str, str] = {
    "scroll": "📜",
    "keyboard": "⌨️ ",
    "click": "👆",
    "input": "✏️ ",
    "wait": "⏳",
    "verify": "✓",
    "context": "•",
    "navigation": "🧭",
    "navigate": "🧭",
    "element": "•",
    "gesture": "👋",
    "info": "ℹ️ ",  # noqa: RUF001
    "warning": "⚠️ ",
    "success": "✅",
    "error": "❌",
    "extract": "🔍",
    "schema": "📐",
    "quality": "📊",
    "reconciliation": "⚖️ ",
}

_BAR = "═" * 67

# Always write to the *original* stdout, not whatever pytest has swapped in
# for its capture machinery. Otherwise passing tests show no log output —
# the whole point of the logger is to narrate execution as it runs.
_OUT = sys.__stdout__

# Disable colours when the real stdout isn't a tty (CI logs, file redirects)
# or when NO_COLOR is set (https://no-color.org).
_USE_COLOUR = _OUT is not None and _OUT.isatty() and not os.environ.get("NO_COLOR")


def _c(code: str) -> str:
    return code if _USE_COLOUR else ""


def _write(line: str = "") -> None:
    """Print to the original stdout, bypassing pytest's capture buffer."""
    print(line, file=_OUT, flush=True)


# ---------------------------------------------------------------------------
# Module-level state — counters reset between tests via reset_step_counter()
# ---------------------------------------------------------------------------

_step_counter = 0
_section_counter = 0


def reset_step_counter() -> None:
    """Zero the step + section counters. Call at the start of each test."""
    global _step_counter, _section_counter
    _step_counter = 0
    _section_counter = 0


def step_count() -> int:
    """Current step counter — exposed for the test summary banner."""
    return _step_counter


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def _category_colour(category: LogCategory) -> str:
    return _COLOUR_MAP.get(category, RESET)


def _category_emoji(category: LogCategory) -> str:
    return _EMOJI_MAP.get(category, "•")


def _timestamp() -> str:
    # HH:MM:SS.mmm — drop tz, drop trailing microseconds beyond 3 digits
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


# ---------------------------------------------------------------------------
# Core hierarchical primitives
# ---------------------------------------------------------------------------


def log_section(title: str) -> None:
    """Top-level grouping. Resets the step counter for the new section."""
    global _section_counter, _step_counter
    _section_counter += 1
    _step_counter = 0
    _write()
    _write(f"{_c(BOLD)}{_c(CYAN)}{_BAR}{_c(RESET)}")
    _write(f"{_c(BOLD)}{_c(CYAN)}  Section {_section_counter}: {title}{_c(RESET)}")
    _write(f"{_c(BOLD)}{_c(CYAN)}{_BAR}{_c(RESET)}")


def log_step(category: LogCategory, message: str) -> None:
    """A single user-action step. Increments the step counter."""
    global _step_counter
    _step_counter += 1
    colour = _category_colour(category)
    emoji = _category_emoji(category)
    _write(
        f"{_c(GRAY)}[{_timestamp()}]{_c(RESET)} "
        f"{_c(BOLD)}Step {_step_counter}:{_c(RESET)} "
        f"{emoji} {_c(colour)}{message}{_c(RESET)}"
    )


def log_substep(category: LogCategory, message: str) -> None:
    """Outcome / consequence of the previous step (no counter bump)."""
    colour = _category_colour(category)
    emoji = _category_emoji(category)
    _write(f"         └─ {emoji} {_c(colour)}{message}{_c(RESET)}")


def log_detail(message: str) -> None:
    """Subsidiary context (errors, expected/actual, raw values)."""
    _write(f"         {_c(GRAY)}{message}{_c(RESET)}")


# ---------------------------------------------------------------------------
# Pre-built semantic helpers — match the TS port 1:1 where applicable
# ---------------------------------------------------------------------------


def log_click(element_name: str) -> None:
    log_step("click", f"User clicked on '{element_name}'")


def log_set_value(field_name: str, value: str, masked: bool = False) -> None:
    display = "••••••••" if masked else value
    log_step("input", f"User entered '{display}' into '{field_name}'")


def log_wait_for_element(element_name: str, timeout_ms: int = 30_000) -> None:
    log_step(
        "wait",
        f"Waiting for '{element_name}' to be displayed (timeout: {timeout_ms}ms)",
    )


def log_wait_for_element_found(element_name: str) -> None:
    log_substep("success", f"'{element_name}' is now displayed")


def log_verify(element_name: str, visible: bool = True) -> None:
    if visible:
        log_step("verify", f"Verified '{element_name}' is visible")
    else:
        log_step("warning", f"'{element_name}' is NOT visible")


def log_navigate(destination: str) -> None:
    log_step("navigation", f"Navigating to '{destination}'")


def log_scroll(direction: str, target: str | None = None) -> None:
    suffix = f" to find '{target}'" if target else ""
    log_step("scroll", f"Scrolling {direction}{suffix}")


def log_extract(what: str, value: str) -> None:
    log_step("extract", f"Extracted {what}: '{value}'")


def log_error(message: str, error: BaseException | None = None) -> None:
    log_step("error", message)
    if error is not None:
        log_detail(f"Error: {error}")


def log_retry(action: str, attempt: int, max_attempts: int) -> None:
    log_step("warning", f"Retrying '{action}' (attempt {attempt}/{max_attempts})")


# ---------------------------------------------------------------------------
# Data-quality additions (not in the original mobile-E2E article)
# ---------------------------------------------------------------------------


def log_schema_check(dataset: str, passed: bool) -> None:
    if passed:
        log_step("schema", f"Schema contract holds for '{dataset}'")
    else:
        log_step("error", f"Schema contract violated for '{dataset}'")


def log_quality_dimension(dimension: str, column: str | None = None) -> None:
    target = f" on '{column}'" if column else ""
    log_step("quality", f"Checking {dimension}{target}")


def log_reconciliation(
    left_rows: int,
    right_rows: int,
    only_in_left: int,
    only_in_right: int,
    matched: bool,
) -> None:
    if matched:
        log_step("reconciliation", f"Reconciled {left_rows} ↔ {right_rows} rows cleanly")
    else:
        log_step(
            "reconciliation",
            f"Drift detected — only_in_left={only_in_left}, only_in_right={only_in_right}",
        )


# ---------------------------------------------------------------------------
# Test summary banner
# ---------------------------------------------------------------------------


def log_test_summary(test_name: str, passed: bool, duration_ms: float) -> None:
    _write()
    _write(f"{_c(BOLD)}{_BAR}{_c(RESET)}")
    if passed:
        _write(f"{_c(BOLD)}{_c(GREEN)}  ✅ TEST PASSED: {test_name}{_c(RESET)}")
    else:
        _write(f"{_c(BOLD)}{_c(RED)}  ❌ TEST FAILED: {test_name}{_c(RESET)}")
    _write(f"{_c(GRAY)}  Duration: {duration_ms / 1000:.2f}s{_c(RESET)}")
    _write(f"{_c(GRAY)}  Total Steps: {_step_counter}{_c(RESET)}")
    _write(f"{_c(BOLD)}{_BAR}{_c(RESET)}")


# ---------------------------------------------------------------------------
# Higher-order wrapper — apply consistent logging to any callable
# ---------------------------------------------------------------------------

P = ParamSpec("P")
R = TypeVar("R")


def with_logging(
    category: LogCategory,
    description: str | Callable[..., str],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that emits a step before the call and an error log on failure.

    `description` may be either a static string or a callable producing one
    from the wrapped function's args — same idea as the TS HOF.
    """

    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            msg = description(*args, **kwargs) if callable(description) else description
            log_step(category, msg)
            try:
                return fn(*args, **kwargs)
            except BaseException as exc:
                log_error(f"Failed: {msg}", exc)
                raise

        return wrapper

    return decorator
