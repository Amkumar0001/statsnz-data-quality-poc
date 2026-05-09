from __future__ import annotations

import pytest
import requests

from src.clients.ckan_api import CkanClient
from src.clients.statsnz_api import StatsNZClient


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = "statsnz-dq/0.1 (+https://github.com/aman/statsnz-data-quality-poc)"
    return s


@pytest.fixture(scope="session")
def stats_nz_client(stats_nz_base_url: str, stats_nz_api_key: str) -> StatsNZClient:
    return StatsNZClient(base_url=stats_nz_base_url, api_key=stats_nz_api_key)


@pytest.fixture(scope="session")
def ckan_client(ckan_base_url: str) -> CkanClient:
    return CkanClient(base_url=ckan_base_url)
