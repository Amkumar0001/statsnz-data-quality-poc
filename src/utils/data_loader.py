from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = PROJECT_ROOT / "data" / "snapshots"

CPI_STRING_COLUMNS = [
    "Series_reference",
    "Period",
    "STATUS",
    "UNITS",
    "Subject",
    "Group",
    "Series_title_1",
]


def load_cpi_snapshot(name: str = "cpi_sample.csv") -> pd.DataFrame:
    path = SNAPSHOT_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"snapshot not found: {path}")
    # Period values like '2024.06' look numeric — pin string dtypes so
    # pandas doesn't silently coerce them to float.
    return pd.read_csv(
        path,
        dtype={col: "string" for col in CPI_STRING_COLUMNS} | {"Data_value": "float64"},
    )


def list_snapshots() -> list[Path]:
    return sorted(SNAPSHOT_DIR.glob("*.csv"))
