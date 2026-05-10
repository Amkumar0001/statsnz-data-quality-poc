from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_src_modules_importable() -> None:
    from src.clients import ckan_api, statsnz_api, statsnz_pages  # noqa: F401
    from src.utils import data_loader, reconciliation  # noqa: F401
    from src.validators import cpi_expectations, cpi_schema  # noqa: F401
