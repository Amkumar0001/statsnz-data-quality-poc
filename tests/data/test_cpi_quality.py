"""Data-quality dimensions: completeness, validity, uniqueness, timeliness.

Mapped to the canonical DAMA-DMBOK data quality framework — the same
vocabulary Stats NZ uses internally for data-platform health metrics.
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
    null_count = len(cpi_dataframe[cpi_dataframe[column].isna()])
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


@pytest.mark.quality
def test_uniqueness_composite_primary_key(cpi_dataframe: pd.DataFrame) -> None:
    duplicates = cpi_dataframe.duplicated(subset=["Series_reference", "Period"]).sum()
    assert duplicates == 0, f"{duplicates} duplicate (Series_reference, Period) rows"


@pytest.mark.quality
def test_consistency_each_series_has_full_quarterly_history(
    cpi_dataframe: pd.DataFrame,
) -> None:
    counts = cpi_dataframe.groupby("Series_reference").size()
    assert (counts == counts.iloc[0]).all(), (
        f"series have uneven row counts: {counts.to_dict()}"
    )


@pytest.mark.quality
def test_timeliness_latest_period_within_two_years(cpi_dataframe: pd.DataFrame) -> None:
    parsed = pd.to_datetime(
        cpi_dataframe["Period"].str.replace(".", "-", regex=False) + "-01",
        format="%Y-%m-%d",
    )
    latest = parsed.max()
    cutoff = pd.Timestamp.now() - pd.DateOffset(years=2)
    assert latest >= cutoff, (
        f"latest period {latest.date()} is older than cutoff {cutoff.date()}"
    )


@pytest.mark.quality
def test_accuracy_food_index_increases_monotonically(cpi_dataframe: pd.DataFrame) -> None:
    food = cpi_dataframe.loc[cpi_dataframe["Group"] == "Food"].sort_values(by="Period")
    assert food["Data_value"].is_monotonic_increasing, (
        "food index should be monotonically increasing across the sample window"
    )
