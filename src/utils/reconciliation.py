from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ReconciliationReport:
    """Summary of a row-by-row comparison between two DataFrames."""

    left_rows: int
    right_rows: int
    common_rows: int
    only_in_left: int
    only_in_right: int
    column_sum_diffs: dict[str, float] = field(default_factory=dict)

    @property
    def matched(self) -> bool:
        return (
            self.left_rows == self.right_rows
            and self.only_in_left == 0
            and self.only_in_right == 0
            and all(abs(v) < 1e-6 for v in self.column_sum_diffs.values())
        )


def reconcile(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    keys: list[str],
    numeric_columns: list[str] | None = None,
) -> ReconciliationReport:
    """Reconcile two DataFrames on a composite key.

    Counts overlap, flags rows missing from either side, and computes
    sum differences on numeric columns — the three checks every reco
    pipeline does.
    """
    merged = left.merge(
        right,
        on=keys,
        how="outer",
        suffixes=("_left", "_right"),
        indicator=True,
    )

    only_left = int((merged["_merge"] == "left_only").sum())
    only_right = int((merged["_merge"] == "right_only").sum())
    common = int((merged["_merge"] == "both").sum())

    sum_diffs: dict[str, float] = {}
    for col in numeric_columns or []:
        left_total = float(left[col].sum())
        right_total = float(right[col].sum())
        sum_diffs[col] = round(left_total - right_total, 6)

    return ReconciliationReport(
        left_rows=len(left),
        right_rows=len(right),
        common_rows=common,
        only_in_left=only_left,
        only_in_right=only_right,
        column_sum_diffs=sum_diffs,
    )
