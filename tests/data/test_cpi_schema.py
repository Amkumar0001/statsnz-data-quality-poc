"""Schema-contract validation for the CPI dataset using Pandera.

Schema drift is the #1 silent failure mode in data pipelines —
column renamed, type widened, nullability changed. These tests assert
that any new snapshot still matches the contract our downstream
consumers depend on.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.validators.cpi_schema import cpi_schema


@pytest.mark.schema
def test_snapshot_matches_contract(cpi_dataframe: pd.DataFrame) -> None:
    cpi_schema.validate(cpi_dataframe, lazy=True)
