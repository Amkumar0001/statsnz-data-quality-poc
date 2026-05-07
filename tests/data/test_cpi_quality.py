"""Data-quality dimensions: completeness and validity.

Mapped to the canonical DAMA-DMBOK data quality framework.
More dimensions land in the next pass.
"""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.mark.quality
@pytest.mark.parametrize(
    "column",
    ["Series_reference", "Period", "Data_value", "STATUS", "Subject", "Group"],
)
def test_completeness_no_nulls_in_required_columns(
    cpi_dataframe: pd.DataFrame, column: str
) -> None:
    null_count = int(cpi_dataframe[column].isna().sum())
    assert null_count == 0, f"{column} has {null_count} nulls"


@pytest.mark.quality
def test_validity_data_value_within_range(cpi_dataframe: pd.DataFrame) -> None:
    assert cpi_dataframe["Data_value"].between(0, 10000).all()


@pytest.mark.quality
def test_validity_period_format(cpi_dataframe: pd.DataFrame) -> None:
    pattern = r"^\d{4}\.(?:03|06|09|12)$"
    assert cpi_dataframe["Period"].str.match(pattern).all()


@pytest.mark.quality
def test_validity_series_reference_format(cpi_dataframe: pd.DataFrame) -> None:
    pattern = r"^CPIQ\.[A-Z0-9]+$"
    assert cpi_dataframe["Series_reference"].str.match(pattern).all()
