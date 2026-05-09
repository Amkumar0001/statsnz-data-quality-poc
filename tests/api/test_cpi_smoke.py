"""Live smoke checks against the Stats NZ OData API.

These tests are skipped automatically if STATS_NZ_API_KEY is not set —
the framework still runs end-to-end against the local snapshot in offline mode.
"""

from __future__ import annotations

import pytest

CPI_PATH = "/opendata/cpi_quarterly/v1/CPI_Quarterly"


@pytest.mark.smoke
@pytest.mark.live
def test_cpi_endpoint_returns_200(stats_nz_client) -> None:
    payload = stats_nz_client.get_dataset(CPI_PATH, top=5)
    assert isinstance(payload, dict)


@pytest.mark.smoke
@pytest.mark.live
def test_cpi_endpoint_returns_records(stats_nz_client) -> None:
    payload = stats_nz_client.get_dataset(CPI_PATH, top=10)
    records = payload.get("value", [])
    assert len(records) > 0, "CPI endpoint returned an empty payload"


@pytest.mark.smoke
@pytest.mark.live
def test_cpi_payload_carries_expected_keys(stats_nz_client) -> None:
    payload = stats_nz_client.get_dataset(CPI_PATH, top=1)
    records = payload.get("value", [])
    assert records, "no records returned"
    record = records[0]
    expected_keys = {"Period", "Data_value"}
    missing = expected_keys - set(record.keys())
    assert not missing, f"missing expected keys: {missing}"
