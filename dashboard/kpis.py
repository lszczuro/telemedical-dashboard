"""Pure KPI computations for the dashboard."""

from __future__ import annotations

import pandas as pd

__all__ = ["compute_scheduled_visit_volume_by_week_and_type"]


def compute_scheduled_visit_volume_by_week_and_type(visits: pd.DataFrame) -> pd.DataFrame:
    """Return scheduled visit counts by week-ending Sunday and visit type."""

    grouped = (
        visits.assign(
            week=visits["visit_date"].dt.to_period("W-SUN").dt.end_time.dt.normalize()
        )
        .groupby(["week", "visit_type"], dropna=False)
        .size()
        .reset_index(name="visit_count")
        .sort_values(["week", "visit_type"])
        .reset_index(drop=True)
    )
    return grouped[["week", "visit_type", "visit_count"]]
