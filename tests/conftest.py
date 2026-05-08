from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pytest
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.data_loader import load_cpi_snapshot  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


@pytest.fixture(scope="session")
def stats_nz_api_key() -> str:
    key = os.getenv("STATS_NZ_API_KEY", "").strip()
    if not key:
        pytest.skip("STATS_NZ_API_KEY not set — register at api.stats.govt.nz to enable live tests")
    return key


@pytest.fixture(scope="session")
def stats_nz_base_url() -> str:
    return os.getenv("STATS_NZ_BASE_URL", "https://api.stats.govt.nz").rstrip("/")


@pytest.fixture(scope="session")
def ckan_base_url() -> str:
    return os.getenv("CKAN_BASE_URL", "https://catalogue.data.govt.nz").rstrip("/")


@pytest.fixture(scope="session")
def statsnz_site_url() -> str:
    return os.getenv("STATSNZ_SITE_URL", "https://www.stats.govt.nz").rstrip("/")


@pytest.fixture
def cpi_dataframe() -> pd.DataFrame:
    return load_cpi_snapshot("cpi_sample.csv")


@pytest.fixture
def cpi_dataframe_api_mirror() -> pd.DataFrame:
    return load_cpi_snapshot("cpi_sample_api.csv")
