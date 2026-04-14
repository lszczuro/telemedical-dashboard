"""Pure KPI computations for the dashboard."""

from __future__ import annotations

import pandas as pd

__all__ = [
    "compute_scheduled_visit_volume_by_week_and_type",
    "compute_cancellation_rate_by_week",
    "compute_no_show_rate_by_week",
]


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


# Cancellation rate counts all `cancelled` rows, including non-zero durations, over all visits.
def compute_cancellation_rate_by_week(visits: pd.DataFrame) -> pd.DataFrame:
    """Return weekly cancellation rate labeled by week-ending Sunday."""

    grouped = (
        visits.assign(
            week=visits["visit_date"].dt.to_period("W-SUN").dt.end_time.dt.normalize(),
            is_cancelled=visits["status"].eq("cancelled"),
        )
        .groupby("week", dropna=False)
        .agg(rate=("is_cancelled", "mean"))
        .reset_index()
        .sort_values("week")
        .reset_index(drop=True)
    )
    return grouped[["week", "rate"]]


# No-show rate counts only `no_show` rows over all visits across the same weekly denominator.
def compute_no_show_rate_by_week(visits: pd.DataFrame) -> pd.DataFrame:
    """Return weekly no-show rate labeled by week-ending Sunday."""

    grouped = (
        visits.assign(
            week=visits["visit_date"].dt.to_period("W-SUN").dt.end_time.dt.normalize(),
            is_no_show=visits["status"].eq("no_show"),
        )
        .groupby("week", dropna=False)
        .agg(rate=("is_no_show", "mean"))
        .reset_index()
        .sort_values("week")
        .reset_index(drop=True)
    )
    return grouped[["week", "rate"]]
