from __future__ import annotations

import pandas as pd
import pytest

from src.utils.reconciliation import reconcile

KEYS = ["Series_reference", "Period"]


@pytest.mark.reconciliation
def test_snapshots_are_identical(
    cpi_dataframe: pd.DataFrame, cpi_dataframe_api_mirror: pd.DataFrame
) -> None:
    report = reconcile(
        cpi_dataframe,
        cpi_dataframe_api_mirror,
        keys=KEYS,
        numeric_columns=["Data_value"],
    )
    assert report.matched, (
        f"reconciliation drift — only_in_left={report.only_in_left}, "
        f"only_in_right={report.only_in_right}, sum_diffs={report.column_sum_diffs}"
    )


@pytest.mark.reconciliation
def test_drift_in_api_mirror_is_detected(
    cpi_dataframe: pd.DataFrame, cpi_dataframe_api_mirror: pd.DataFrame
) -> None:
    drifted = cpi_dataframe_api_mirror.copy()
    drifted.loc[drifted.index[0], "Data_value"] += 5.0
    report = reconcile(
        cpi_dataframe, drifted, keys=KEYS, numeric_columns=["Data_value"]
    )
    assert not report.matched
    assert abs(report.column_sum_diffs["Data_value"]) == 5.0


@pytest.mark.reconciliation
def test_missing_row_in_one_source_is_detected(
    cpi_dataframe: pd.DataFrame, cpi_dataframe_api_mirror: pd.DataFrame
) -> None:
    truncated = cpi_dataframe_api_mirror.iloc[1:].copy()
    report = reconcile(cpi_dataframe, truncated, keys=KEYS)
    assert report.only_in_left == 1
    assert report.only_in_right == 0


@pytest.mark.reconciliation
def test_row_only_in_right_is_detected(
    cpi_dataframe: pd.DataFrame, cpi_dataframe_api_mirror: pd.DataFrame
) -> None:
    extra_row = cpi_dataframe.iloc[-1:].copy()
    extra_row.loc[:, "Period"] = "2024.09"
    extended = pd.concat([cpi_dataframe_api_mirror, extra_row], ignore_index=True)
    report = reconcile(cpi_dataframe, extended, keys=KEYS)
    assert report.only_in_left == 0
    assert report.only_in_right == 1
