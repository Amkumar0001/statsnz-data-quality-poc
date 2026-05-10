from __future__ import annotations

import pytest

CATALOGUE_PATH = "/structure/dataflow/STATSNZ"


@pytest.mark.smoke
@pytest.mark.live
def test_ade_endpoint_returns_200(stats_nz_client) -> None:
    payload = stats_nz_client.get_dataset(CATALOGUE_PATH)
    assert isinstance(payload, dict), f"expected JSON object, got {type(payload).__name__}"


@pytest.mark.smoke
@pytest.mark.live
def test_ade_response_has_sdmx_envelope(stats_nz_client) -> None:
    payload = stats_nz_client.get_dataset(CATALOGUE_PATH)
    sdmx_keys = {"data", "structures", "structure", "meta", "references", "resources"}
    actual_keys = set(payload.keys())
    assert sdmx_keys & actual_keys, (
        f"unexpected SDMX response shape; top-level keys: {sorted(actual_keys)}"
    )


@pytest.mark.smoke
@pytest.mark.live
def test_ade_catalogue_is_populated(stats_nz_client) -> None:
    payload = stats_nz_client.get_dataset(CATALOGUE_PATH)
    references = payload.get("references", {}) or {}
    assert len(references) >= 5, (
        f"catalogue suspiciously sparse: {len(references)} references; "
        f"sample: {list(references.keys())[:3]}"
    )
