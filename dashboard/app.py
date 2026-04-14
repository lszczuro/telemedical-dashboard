"""Streamlit entry point for the dashboard MVP."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.data import load_all
from dashboard.kpis import (
    compute_cancellation_rate_by_week,
    compute_no_show_rate_by_week,
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


def main() -> None:
    st.set_page_config(page_title="Telemedi Operations Dashboard", layout="wide")
    st.title("Telemedi Operations Dashboard")
    st.write(
        "For the Head of Operations: weekly demand first, remaining KPI slots visible, "
        "and revenue explicitly separated until attribution is trustworthy."
    )

    data = load_all()
    scheduled_volume = compute_scheduled_visit_volume_by_week_and_type(data.visits)
    cancellation_rate = compute_cancellation_rate_by_week(data.visits)
    no_show_rate = compute_no_show_rate_by_week(data.visits)
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

    chart = (
        alt.Chart(scheduled_volume)
        .mark_line(point=True)
        .encode(
            x=alt.X("week:T", title="Week ending"),
            y=alt.Y("visit_count:Q", title="Scheduled visits"),
            color=alt.Color("visit_type:N", title="Visit type"),
        )
        .properties(title="Scheduled Visit Volume by Week and Visit Type")
    )

    st.altair_chart(chart, use_container_width=True)
    st.caption(KPI_1_CAPTION)

    upcoming_kpis = [
        "KPI #4 placeholder: Average patient satisfaction",
        "KPI #5 placeholder: Doctor utilization minutes",
    ]
    if len(upcoming_kpis) >= 2:
        st.subheader("Coming next")
        for item in upcoming_kpis:
            st.info(item)

    st.subheader("Revenue Disclaimer")
    st.warning(REVENUE_DISCLAIMER)


if __name__ == "__main__":
    main()
