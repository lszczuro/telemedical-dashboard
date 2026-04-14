"""Streamlit entry point for the dashboard MVP."""

from __future__ import annotations

import altair as alt
import streamlit as st

from dashboard.data import load_all
from dashboard.kpis import compute_scheduled_visit_volume_by_week_and_type

REVENUE_DISCLAIMER = (
    "Revenue metrics are shown from `revenue.csv` only and are not linked to "
    "visit-level operational KPIs because the revenue-to-visit join is not reliable."
)
KPI_1_CAPTION = (
    "Scheduled visit volume per week, segmented by consultation format. "
    "Anchor demand metric for the Head of Operations."
)


def main() -> None:
    st.set_page_config(page_title="Telemedi Operations Dashboard", layout="wide")
    st.title("Telemedi Operations Dashboard")
    st.write(
        "For the Head of Operations: weekly demand first, remaining KPI slots visible, "
        "and revenue explicitly separated until attribution is trustworthy."
    )

    data = load_all()
    scheduled_volume = compute_scheduled_visit_volume_by_week_and_type(data.visits)

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

    st.subheader("Upcoming KPIs")
    st.info("KPI #2 placeholder: Cancellation rate")
    st.info("KPI #3 placeholder: No-show rate")
    st.info("KPI #4 placeholder: Average patient satisfaction")
    st.info("KPI #5 placeholder: Doctor utilization minutes")

    st.subheader("Revenue Disclaimer")
    st.warning(REVENUE_DISCLAIMER)


if __name__ == "__main__":
    main()
