"""Live smoke checks against the Aotearoa Data Explorer (ADE) SDMX API.

ADE is SDMX 2.0/2.1-shaped. Two base paths exist on the same domain:

    Data queries:      /ade-api/rest/v2/data/{context}/{agencyId}/...
    Structure queries: /ade-api/rest/v2/structure/{type}/{agencyId}/...

For a smoke check we hit the structure listing (operation 02) which
returns the full catalogue of dataflows STATSNZ publishes — proves
auth + the User-Agent format + the SDMX response shape, all without
hard-coding a dataflow ID that can change.

Tests skip automatically if STATS_NZ_API_KEY is not set.
"""

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
    """The structure listing should advertise multiple dataflows.

    Stats NZ codes dataflows with 3-letter subject prefixes
    (e.g. AGR_AGR_001 = agriculture, BDS_BDS_001 = business demography).
    For a smoke check we just want evidence the catalogue is non-empty —
    finding the specific dataflow ID for any given subject is a
    follow-up query once we know what we want to consume.
    """
    payload = stats_nz_client.get_dataset(CATALOGUE_PATH)
    references = payload.get("references", {}) or {}
    assert len(references) >= 5, (
        f"catalogue suspiciously sparse: {len(references)} references; "
        f"sample: {list(references.keys())[:3]}"
    )
