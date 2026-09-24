"""KPI calculations. Pure functions: DataFrame in, numbers out."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from .config import MONTH_CODE_TO_NAME


@dataclass(frozen=True)
class KPIs:
    total_births: int
    n_geographies: int
    avg_births_per_month: Optional[float]
    top_geography: Optional[str]
    top_geography_births: Optional[int]
    top_month: Optional[str]
    top_month_births: Optional[int]


def _top_label(totals: pd.Series) -> tuple[str, int]:
    """Name and value of the largest entry; mention ties instead of hiding them."""
    best = totals.max()
    winners = totals[totals == best].index.tolist()
    label = str(winners[0])
    if len(winners) > 1:
        label += f" (+{len(winners) - 1} tied)"
    return label, int(best)


def compute_kpis(df: pd.DataFrame) -> KPIs:
    """Summarize the currently filtered data."""
    if df.empty:
        return KPIs(0, 0, None, None, None, None, None)

    total = int(df["births"].sum())
    n_months = df["month_code"].nunique()

    by_geo = df.groupby("state_of_residence")["births"].sum()
    by_month = df.groupby("month_code")["births"].sum()
    by_month.index = by_month.index.map(MONTH_CODE_TO_NAME)  # chronological order kept

    top_geo, top_geo_births = _top_label(by_geo)
    top_month, top_month_births = _top_label(by_month)

    return KPIs(
        total_births=total,
        n_geographies=int(df["state_of_residence"].nunique()),
        avg_births_per_month=total / n_months,
        top_geography=top_geo,
        top_geography_births=top_geo_births,
        top_month=top_month,
        top_month_births=top_month_births,
    )


def effective_top_n(n_geographies: int, requested: int) -> int:
    """How many geographies each end of the top/bottom chart can show without overlap."""
    return max(0, min(requested, n_geographies // 2))
