"""Pure KPI computations for the dashboard."""

from __future__ import annotations

import pandas as pd

__all__ = [
    "compute_scheduled_visit_volume_by_week_and_type",
    "compute_cancellation_rate_by_week",
    "compute_no_show_rate_by_week",
    "compute_satisfaction_by_visit_type",
    "compute_doctor_utilization_minutes",
    "compute_gross_revenue_by_week",
    "compute_refund_rate_by_week",
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


def compute_satisfaction_by_visit_type(visits: pd.DataFrame) -> pd.DataFrame:
    """Return average satisfaction and sample size by visit type for completed visits."""

    completed_visits = visits.loc[visits["status"] == "completed"]
    grouped = (
        completed_visits.groupby("visit_type", dropna=False)["satisfaction_score"]
        .agg(avg_satisfaction="mean", completed_visit_count="size")
        .reset_index()
        .sort_values("visit_type")
        .reset_index(drop=True)
    )
    return grouped[["visit_type", "avg_satisfaction", "completed_visit_count"]]


def compute_doctor_utilization_minutes(
    visits: pd.DataFrame, doctors: pd.DataFrame
) -> pd.DataFrame:
    """Return completed-visit utilization minutes by doctor and specialization."""

    # Exclude cancelled handling-time rows per docs/data-consistency-review.md.
    completed_visits = visits.loc[visits["status"] == "completed"]
    utilization = (
        completed_visits.groupby("doctor_id", dropna=False)["duration_min"]
        .sum()
        .reset_index(name="utilization_minutes")
    )
    result = (
        utilization.merge(doctors[["doctor_id", "specialization"]], on="doctor_id", how="inner")
        .sort_values(["utilization_minutes", "doctor_id"], ascending=[False, True])
        .reset_index(drop=True)
    )
    return result[["doctor_id", "specialization", "utilization_minutes"]]


def compute_gross_revenue_by_week(revenue: pd.DataFrame) -> pd.DataFrame:
    """Return gross revenue summed by week-ending Sunday."""

    grouped = (
        revenue.assign(
            week=revenue["transaction_date"].dt.to_period("W-SUN").dt.end_time.dt.normalize()
        )
        .groupby("week", dropna=False)["amount"]
        .sum()
        .reset_index(name="gross_revenue")
        .sort_values("week")
        .reset_index(drop=True)
    )
    return grouped[["week", "gross_revenue"]]


# Use refunded amount / total amount so the rate reflects financial impact, not just
# transaction frequency. This intentionally operates on `revenue.csv` only.
def compute_refund_rate_by_week(revenue: pd.DataFrame) -> pd.DataFrame:
    """Return weekly refund rate as refunded amount divided by total amount."""

    weekly = revenue.assign(
        week=revenue["transaction_date"].dt.to_period("W-SUN").dt.end_time.dt.normalize(),
        refunded_amount=revenue["amount"].where(revenue["refunded"], 0.0),
    ).groupby("week", dropna=False)[["amount", "refunded_amount"]].sum()

    result = (
        weekly.assign(refund_rate=weekly["refunded_amount"] / weekly["amount"])
        .reset_index()[["week", "refund_rate"]]
        .sort_values("week")
        .reset_index(drop=True)
    )
    return result
