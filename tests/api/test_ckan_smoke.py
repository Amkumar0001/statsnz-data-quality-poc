from __future__ import annotations

import pytest


@pytest.mark.smoke
@pytest.mark.live
def test_ckan_search_returns_success(ckan_client) -> None:
    payload = ckan_client.package_search("statistics", rows=5)
    assert payload.get("success") is True


@pytest.mark.smoke
@pytest.mark.live
def test_ckan_search_returns_results(ckan_client) -> None:
    payload = ckan_client.package_search("statistics", rows=5)
    results = payload.get("result", {}).get("results", [])
    assert len(results) > 0, "CKAN search returned no packages"


@pytest.mark.schema
@pytest.mark.live
def test_ckan_package_has_expected_shape(ckan_client) -> None:
    payload = ckan_client.package_search("statistics", rows=1)
    pkg = payload["result"]["results"][0]
    for key in ("id", "name", "title", "resources"):
        assert key in pkg, f"CKAN package missing key '{key}'"
    assert isinstance(pkg["resources"], list)
