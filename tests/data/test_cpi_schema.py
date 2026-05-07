"""Schema-contract validation for the CPI dataset using Pandera.

Schema drift is the #1 silent failure mode in data pipelines —
column renamed, type widened, nullability changed. These tests assert
that any new snapshot still matches the contract our downstream
consumers depend on.
"""

from __future__ import annotations

import pandas as pd
import pandera.errors
import pytest

from src.validators.cpi_schema import cpi_schema

SchemaFailure = (pandera.errors.SchemaError, pandera.errors.SchemaErrors)


@pytest.mark.schema
def test_snapshot_matches_contract(cpi_dataframe: pd.DataFrame) -> None:
    cpi_schema.validate(cpi_dataframe, lazy=True)


@pytest.mark.schema
def test_extra_column_rejected_by_strict_schema(cpi_dataframe: pd.DataFrame) -> None:
    df = cpi_dataframe.assign(unexpected_column="oops")
    with pytest.raises(SchemaFailure):
        cpi_schema.validate(df, lazy=True)


@pytest.mark.schema
def test_invalid_period_rejected(cpi_dataframe: pd.DataFrame) -> None:
    df = cpi_dataframe.copy()
    df.loc[df.index[0], "Period"] = "2024-Q1"
    with pytest.raises(SchemaFailure):
        cpi_schema.validate(df, lazy=True)


@pytest.mark.schema
def test_negative_data_value_rejected(cpi_dataframe: pd.DataFrame) -> None:
    df = cpi_dataframe.copy()
    df.loc[df.index[0], "Data_value"] = -1.0
    with pytest.raises(SchemaFailure):
        cpi_schema.validate(df, lazy=True)


@pytest.mark.schema
def test_unknown_status_rejected(cpi_dataframe: pd.DataFrame) -> None:
    df = cpi_dataframe.copy()
    df.loc[df.index[0], "STATUS"] = "Z"
    with pytest.raises(SchemaFailure):
        cpi_schema.validate(df, lazy=True)


@pytest.mark.schema
def test_duplicate_primary_key_rejected(cpi_dataframe: pd.DataFrame) -> None:
    df = pd.concat([cpi_dataframe, cpi_dataframe.iloc[:1]], ignore_index=True)
    with pytest.raises(SchemaFailure):
        cpi_schema.validate(df, lazy=True)
