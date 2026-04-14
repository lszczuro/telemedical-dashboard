"""Streamlit entry point for the dashboard MVP."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.data import load_all
from dashboard.kpis import (
    compute_cancellation_rate_by_week,
    compute_doctor_utilization_minutes,
    compute_gross_revenue_by_week,
    compute_no_show_rate_by_week,
    compute_refund_rate_by_week,
    compute_satisfaction_by_visit_type,
    compute_scheduled_visit_volume_by_week_and_type,
)

REVENUE_DISCLAIMER = (
    "Revenue metrics are shown from `revenue.csv` only and are not linked to "
    "visit-level operational KPIs because the revenue-to-visit join is not reliable."
)
KPI_1_CAPTION = (
    "Scheduled visit volume per week, segmented by consultation format. "
    "Anchor demand metric for the Head of Operations."
)
KPI_2_CAPTION = (
    "Cancellation rate across all booked visits. Includes every `cancelled` row, "
    "including those with non-zero recorded duration."
)
KPI_3_CAPTION = "No-show rate across all booked visits with `status = 'no_show'` only."
KPI_4_CAPTION = (
    "Completed-visit satisfaction by consultation format. Tooltip shows the "
    "sample size so small cohorts are visible next to the average."
)
KPI_5_CAPTION = (
    "Completed clinician minutes ranked across the top 10 and bottom 5 doctors. "
    "Doctors with zero completed visits are intentionally absent for now."
)


def _last_complete_week(visit_dates: pd.Series) -> pd.Timestamp:
    max_date = visit_dates.max().normalize()
    current_week_end = max_date.to_period("W-SUN").end_time.normalize()
    if max_date < current_week_end:
        return current_week_end - pd.Timedelta(days=7)
    return current_week_end


def _format_percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


def _format_percentage_point_delta(current_value: float, previous_value: float) -> str:
    delta = (current_value - previous_value) * 100
    return f"{delta:+.1f} pp"


def _render_trend_tile(
    title: str,
    series: pd.DataFrame,
    value_column: str,
    value_formatter,
    delta_formatter,
    *,
    delta_color: str,
    help_text: str,
) -> None:
    current_value = series.iloc[-1][value_column]
    previous_value = series.iloc[-2][value_column] if len(series) > 1 else current_value
    st.metric(
        title,
        value_formatter(current_value),
        delta_formatter(current_value, previous_value),
        delta_color=delta_color,
        help=help_text,
    )
    sparkline_data = series.set_index("week")[[value_column]]
    st.line_chart(sparkline_data, height=100)


def build_satisfaction_chart(satisfaction_by_visit_type: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(satisfaction_by_visit_type)
        .mark_bar()
        .encode(
            x=alt.X(
                "avg_satisfaction:Q", title="Average satisfaction", scale=alt.Scale(domain=[0, 5])
            ),
            y=alt.Y("visit_type:N", title="Visit type", sort="-x"),
            color=alt.Color("visit_type:N", title="Visit type", legend=None),
            tooltip=[
                alt.Tooltip("visit_type:N", title="Visit type"),
                alt.Tooltip("avg_satisfaction:Q", title="Average satisfaction", format=".2f"),
                alt.Tooltip("completed_visit_count:Q", title="Completed visits", format=","),
            ],
        )
        .properties(title="Patient Satisfaction by Visit Type")
    )


def build_utilization_chart(utilization_minutes: pd.DataFrame) -> alt.Chart:
    ranked = utilization_minutes.copy()
    top_n = 10
    bottom_n = 5

    ranked["rank_desc"] = ranked["utilization_minutes"].rank(method="first", ascending=False)
    ranked["rank_asc"] = ranked["utilization_minutes"].rank(method="first", ascending=True)
    filtered = ranked.loc[(ranked["rank_desc"] <= top_n) | (ranked["rank_asc"] <= bottom_n)].copy()
    filtered["segment"] = filtered["rank_desc"].le(top_n).map({True: "Top 10", False: "Bottom 5"})
    filtered = filtered.sort_values(["utilization_minutes", "doctor_id"], ascending=[False, True])

    return (
        alt.Chart(filtered)
        .mark_bar()
        .encode(
            x=alt.X("utilization_minutes:Q", title="Utilization minutes"),
            y=alt.Y("doctor_id:N", title="Doctor", sort="-x"),
            color=alt.Color(
                "segment:N",
                title="Ranking slice",
                scale=alt.Scale(domain=["Top 10", "Bottom 5"], range=["#1f77b4", "#ff7f0e"]),
            ),
            tooltip=[
                alt.Tooltip("doctor_id:N", title="Doctor"),
                alt.Tooltip("specialization:N", title="Specialization"),
                alt.Tooltip("utilization_minutes:Q", title="Utilization minutes", format=","),
                alt.Tooltip("segment:N", title="Shown as"),
            ],
        )
        .properties(title="Doctor Utilization Minutes")
    )


def main() -> None:
    st.set_page_config(page_title="Telemedi Operations Dashboard", layout="wide")
    st.title("Telemedi Operations Dashboard")
    st.write(
        "For the Head of Operations: weekly demand first and revenue explicitly "
        "separated until attribution is trustworthy."
    )

    data = load_all()
    scheduled_volume = compute_scheduled_visit_volume_by_week_and_type(data.visits)
    cancellation_rate = compute_cancellation_rate_by_week(data.visits)
    no_show_rate = compute_no_show_rate_by_week(data.visits)
    satisfaction_by_visit_type = compute_satisfaction_by_visit_type(data.visits)
    doctor_utilization = compute_doctor_utilization_minutes(data.visits, data.doctors)
    gross_revenue = compute_gross_revenue_by_week(data.revenue)
    refund_rate = compute_refund_rate_by_week(data.revenue)
    last_complete_week = _last_complete_week(data.visits["visit_date"])

    weekly_scheduled_summary = (
        scheduled_volume.groupby("week", as_index=False)["visit_count"].sum().sort_values("week")
    )
    completed_scheduled_summary = weekly_scheduled_summary.loc[
        weekly_scheduled_summary["week"] <= last_complete_week
    ].reset_index(drop=True)
    completed_cancellation_rate = cancellation_rate.loc[
        cancellation_rate["week"] <= last_complete_week
    ].reset_index(drop=True)
    completed_no_show_rate = no_show_rate.loc[
        no_show_rate["week"] <= last_complete_week
    ].reset_index(drop=True)

    tile_columns = st.columns(3)
    with tile_columns[0]:
        _render_trend_tile(
            "Scheduled Visits",
            completed_scheduled_summary,
            "visit_count",
            lambda value: f"{int(value):,}",
            lambda current_value, previous_value: f"{int(current_value - previous_value):+d}",
            delta_color="normal",
            help_text="Current value uses the last complete week ending Sunday.",
        )
    with tile_columns[1]:
        _render_trend_tile(
            "Cancellation Rate",
            completed_cancellation_rate,
            "rate",
            _format_percentage,
            _format_percentage_point_delta,
            delta_color="inverse",
            help_text=KPI_2_CAPTION,
        )
    with tile_columns[2]:
        _render_trend_tile(
            "No-show Rate",
            completed_no_show_rate,
            "rate",
            _format_percentage,
            _format_percentage_point_delta,
            delta_color="inverse",
            help_text=KPI_3_CAPTION,
        )

    scheduled_volume_chart = (
        alt.Chart(scheduled_volume)
        .mark_line(point=True)
        .encode(
            x=alt.X("week:T", title="Week ending"),
            y=alt.Y("visit_count:Q", title="Scheduled visits"),
            color=alt.Color("visit_type:N", title="Visit type"),
        )
        .properties(title="Scheduled Visit Volume by Week and Visit Type")
    )

    gross_revenue_chart = (
        alt.Chart(gross_revenue)
        .mark_line(point=True)
        .encode(
            x=alt.X("week:T", title="Week ending"),
            y=alt.Y("gross_revenue:Q", title="Gross revenue"),
        )
        .properties(title="Gross Revenue Trend")
    )

    refund_rate_chart = (
        alt.Chart(refund_rate)
        .mark_line(point=True)
        .encode(
            x=alt.X("week:T", title="Week ending"),
            y=alt.Y("refund_rate:Q", title="Refund rate", axis=alt.Axis(format=".0%")),
        )
        .properties(title="Refund Rate Trend")
    )

    st.altair_chart(scheduled_volume_chart, use_container_width=True)
    st.caption(KPI_1_CAPTION)

    middle_left, middle_right = st.columns(2)
    with middle_left:
        st.altair_chart(
            build_satisfaction_chart(satisfaction_by_visit_type), use_container_width=True
        )
        st.caption(KPI_4_CAPTION)

    with middle_right:
        st.altair_chart(build_utilization_chart(doctor_utilization), use_container_width=True)
        st.caption(KPI_5_CAPTION)

    st.divider()
    st.subheader("Revenue Panel")
    st.warning(REVENUE_DISCLAIMER)
    st.altair_chart(gross_revenue_chart, use_container_width=True)
    st.altair_chart(refund_rate_chart, use_container_width=True)


if __name__ == "__main__":
    main()
