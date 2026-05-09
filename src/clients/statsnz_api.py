from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import requests


@dataclass
class StatsNZClient:
    base_url: str
    api_key: str
    timeout: int = 30

    def _headers(self) -> dict[str, str]:
        return {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Accept": "application/json",
        }

    def get_dataset(
        self,
        path: str,
        *,
        top: int | None = None,
        select: list[str] | None = None,
        odata_filter: str | None = None,
    ) -> dict:
        params: dict[str, str] = {}
        if top is not None:
            params["$top"] = str(top)
        if select:
            params["$select"] = ",".join(select)
        if odata_filter:
            params["$filter"] = odata_filter

        url = f"{self.base_url.rstrip('/')}{path}"
        response = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_dataframe(self, path: str, **kwargs) -> pd.DataFrame:
        payload = self.get_dataset(path, **kwargs)
        records = payload.get("value", payload) if isinstance(payload, dict) else payload
        return pd.DataFrame(records)
