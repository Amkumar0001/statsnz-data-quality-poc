from __future__ import annotations

import pytest

from src.clients.ckan_api import CkanClient
from src.clients.statsnz_api import StatsNZClient


@pytest.fixture(scope="session")
def stats_nz_client(stats_nz_base_url: str, stats_nz_api_key: str) -> StatsNZClient:
    return StatsNZClient(base_url=stats_nz_base_url, api_key=stats_nz_api_key)


@pytest.fixture(scope="session")
def ckan_client(ckan_base_url: str) -> CkanClient:
    return CkanClient(base_url=ckan_base_url)
