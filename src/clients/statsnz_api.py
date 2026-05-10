from __future__ import annotations

import sys
from dataclasses import dataclass

import pandas as pd
import requests


def _default_user_agent() -> str:
    """Stats NZ ADE rejects requests without a properly-shaped User-Agent.

    Required format per the API portal docs:
        {application}/{application_version} Language={language}/{language_version}
    """
    py = ".".join(str(v) for v in sys.version_info[:2])
    return f"statsnz-dq/0.1 Language=Python/{py}"


@dataclass
class StatsNZClient:
    """Client for the Aotearoa Data Explorer (ADE) SDMX API.

    Endpoint pattern: /data/{context}/{agencyId}/{resourceId}/{version}/{key}
    Example:          /data/*/STATSNZ/CPI/latest/

    Auth: header ``Ocp-Apim-Subscription-Key``. Format: header ``Accept:
    application/json`` for JSON responses (alt: SDMX XML/CSV).
    """

    base_url: str
    api_key: str
    timeout: int = 30
    user_agent: str = ""

    def __post_init__(self) -> None:
        if not self.user_agent:
            self.user_agent = _default_user_agent()

    def _headers(self) -> dict[str, str]:
        return {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

    def get_dataset(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> dict:
        url = f"{self.base_url.rstrip('/')}{path}"
        response = requests.get(
            url,
            headers=self._headers(),
            params=params or {},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def list_dataflows(self, agency_id: str = "STATSNZ") -> dict:
        """Convenience: list every dataflow published by an agency."""
        return self.get_dataset(f"/structure/dataflow/{agency_id}/ALL/latest")

    def get_dataframe(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> pd.DataFrame:
        """Best-effort DataFrame for SDMX/OData payloads.

        Tries several common record-list keys; if none match, attempts to
        construct a DataFrame from the top level. Most useful for OData-style
        ``{"value": [...]}`` envelopes; for raw SDMX, you'll usually want to
        consume ``get_dataset`` directly and walk the structures yourself.
        """
        payload = self.get_dataset(path, params=params)
        if isinstance(payload, dict):
            for key in ("value", "data", "observations", "results"):
                if key in payload and isinstance(payload[key], list):
                    return pd.DataFrame(payload[key])
        return pd.DataFrame(payload)
