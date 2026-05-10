"""Hierarchical, human-readable test logger.

Section → Step → SubStep → Detail. Writes to the original stdout so
output isn't swallowed by pytest's sys-mode capture.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Literal, ParamSpec, TypeVar

LogCategory = Literal[
    "scroll", "keyboard", "click", "input", "wait", "verify",
    "context", "navigation", "navigate", "element", "gesture",
    "info", "warning", "success", "error", "extract",
    "schema", "quality", "reconciliation",
]

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
    "scroll": BLUE, "keyboard": MAGENTA, "click": CYAN, "input": GREEN,
    "wait": YELLOW, "verify": GREEN, "context": GRAY, "navigation": BLUE,
    "navigate": BLUE, "element": CYAN, "gesture": MAGENTA, "info": CYAN,
    "warning": YELLOW, "success": GREEN, "error": RED, "extract": MAGENTA,
    "schema": MAGENTA, "quality": CYAN, "reconciliation": BLUE,
}

_EMOJI_MAP: dict[str, str] = {
    "scroll": "📜", "keyboard": "⌨️ ", "click": "👆", "input": "✏️ ",
    "wait": "⏳", "verify": "✓", "context": "•", "navigation": "🧭",
    "navigate": "🧭", "element": "•", "gesture": "👋",
    "info": "ℹ️ ",  # noqa: RUF001
    "warning": "⚠️ ", "success": "✅", "error": "❌", "extract": "🔍",
    "schema": "📐", "quality": "📊", "reconciliation": "⚖️ ",
}

_BAR = "═" * 67

# Original stdout — pytest's capture replaces sys.stdout, this stays put.
_OUT = sys.__stdout__
_USE_COLOUR = _OUT is not None and _OUT.isatty() and not os.environ.get("NO_COLOR")

_step_counter = 0
_section_counter = 0


def _c(code: str) -> str:
    return code if _USE_COLOUR else ""


def _write(line: str = "") -> None:
    print(line, file=_OUT, flush=True)


def _category_colour(category: LogCategory) -> str:
    return _COLOUR_MAP.get(category, RESET)


def _category_emoji(category: LogCategory) -> str:
    return _EMOJI_MAP.get(category, "•")


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def reset_step_counter() -> None:
    global _step_counter, _section_counter
    _step_counter = 0
    _section_counter = 0


def step_count() -> int:
    return _step_counter


def log_section(title: str) -> None:
    global _section_counter, _step_counter
    _section_counter += 1
    _step_counter = 0
    _write()
    _write(f"{_c(BOLD)}{_c(CYAN)}{_BAR}{_c(RESET)}")
    _write(f"{_c(BOLD)}{_c(CYAN)}  Section {_section_counter}: {title}{_c(RESET)}")
    _write(f"{_c(BOLD)}{_c(CYAN)}{_BAR}{_c(RESET)}")


def log_step(category: LogCategory, message: str) -> None:
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
    colour = _category_colour(category)
    emoji = _category_emoji(category)
    _write(f"         └─ {emoji} {_c(colour)}{message}{_c(RESET)}")


def log_detail(message: str) -> None:
    _write(f"         {_c(GRAY)}{message}{_c(RESET)}")


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


P = ParamSpec("P")
R = TypeVar("R")


def with_logging(
    category: LogCategory,
    description: str | Callable[..., str],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
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
