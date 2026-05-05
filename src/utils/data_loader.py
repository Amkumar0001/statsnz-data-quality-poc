from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = PROJECT_ROOT / "data" / "snapshots"


def load_cpi_snapshot(name: str = "cpi_sample.csv") -> pd.DataFrame:
    path = SNAPSHOT_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"snapshot not found: {path}")
    return pd.read_csv(path)


def list_snapshots() -> list[Path]:
    return sorted(SNAPSHOT_DIR.glob("*.csv"))
