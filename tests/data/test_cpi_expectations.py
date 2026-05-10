"""Great Expectations suite run on the CPI snapshot.

GX overlaps with Pandera — it's here for two reasons:
1. The GX HTML data docs are a strong portfolio artefact.
2. Real Stats NZ pipelines often use GX checkpoints in production;
   showing fluency in both tools matters in the interview.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.validators.cpi_expectations import cpi_expectations, validate_dataframe


@pytest.mark.expectations
def test_cpi_suite_passes_on_clean_snapshot(cpi_dataframe: pd.DataFrame) -> None:
    result = validate_dataframe(cpi_dataframe)
    failed = [r for r in result.results if not r.success]
    assert result.success, (
        f"GX suite failed; failed expectations: "
        f"{[r.expectation_config.type for r in failed]}"
    )


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
    types = {e.expectation_type for e in cpi_expectations()}
    for required in (
        "expect_column_values_to_not_be_null",
        "expect_column_values_to_be_between",
        "expect_column_values_to_match_regex",
        "expect_compound_columns_to_be_unique",
    ):
        assert required in types, f"suite is missing {required}"
