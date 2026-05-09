from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass
class CkanClient:
    """Minimal client for the data.govt.nz CKAN open-data API.

    No auth required for read endpoints — useful as a public smoke target
    when STATS_NZ_API_KEY is not yet provisioned.
    """

    base_url: str
    timeout: int = 30

    def package_search(self, query: str, rows: int = 10) -> dict:
        url = f"{self.base_url.rstrip('/')}/api/3/action/package_search"
        response = requests.get(url, params={"q": query, "rows": rows}, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def package_show(self, package_id: str) -> dict:
        url = f"{self.base_url.rstrip('/')}/api/3/action/package_show"
        response = requests.get(url, params={"id": package_id}, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
