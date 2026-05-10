"""Great Expectations suite run on the CPI snapshot.

GX produces auditable validation results and HTML data docs that
data engineers and stakeholders can read directly — useful for
the audit trail beyond what Pandera offers.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.validators.cpi_expectations import cpi_expectations, validate_dataframe


@pytest.mark.expectations
def test_cpi_suite_passes_on_clean_snapshot(cpi_dataframe: pd.DataFrame) -> None:
    result = validate_dataframe(cpi_dataframe)
    assert result.success, "GX suite failed on a clean snapshot"


@pytest.mark.expectations
def test_cpi_suite_catches_null_in_required_column(cpi_dataframe: pd.DataFrame) -> None:
    df = cpi_dataframe.copy()
    df.loc[df.index[0], "Data_value"] = None
    result = validate_dataframe(df)
    assert not result.success, "GX suite should fail when Data_value contains nulls"


@pytest.mark.expectations
def test_cpi_suite_catches_out_of_range_value(cpi_dataframe: pd.DataFrame) -> None:
    df = cpi_dataframe.copy()
    df.loc[df.index[0], "Data_value"] = 99999.0
    result = validate_dataframe(df)
    assert not result.success


@pytest.mark.expectations
def test_suite_contains_expected_dimensions() -> None:
    types = {e.type for e in cpi_expectations()}
    for required in (
        "expect_column_values_to_not_be_null",
        "expect_column_values_to_be_between",
        "expect_column_values_to_match_regex",
        "expect_compound_columns_to_be_unique",
    ):
        assert required in types, f"suite is missing {required}"
