# Operational leakage KPIs: cancellation rate and no-show rate

- [20:13] Reviewed AGENTS.md, workflow-logger guidance, KPI scope, and data consistency docs for operational leakage KPIs.
- [20:13] Confirmed existing dashboard structure: KPI #1 chart in `dashboard/app.py`, KPI logic isolated in pure pandas `dashboard/kpis.py`.
- [20:13] Decision: use `st.metric` for current value and delta plus a tiny `st.line_chart` beneath each tile; this fits Streamlit's built-in delta styling and keeps sparkline implementation minimal.
- [20:13] Decision: define the current period as the last complete week (week-ending Sunday) rather than the currently running partial week to avoid unstable end-of-range values.
- [20:16] Decision: use week-over-week delta in the KPI tiles instead of a smoothed moving average so the dashboard signals immediate operational shifts.
- [20:16] Decision: keep the KPI #1 full Altair chart below the tile row and use the first tile slot for a compact scheduled-visits weekly summary.
- [20:16] Added pure pandas KPI functions for weekly cancellation rate and no-show rate in `dashboard/kpis.py` using `W-SUN` week-ending Sunday labels.
- [20:16] Reworked `dashboard/app.py` top row into three tiles: scheduled visits summary, cancellation rate, and no-show rate, each using the last complete week and a small trend chart.
- [20:16] Removed KPI #2 and KPI #3 from the "Coming next" section and left only KPI #4 and KPI #5 placeholders.
- [20:18] Verified syntax with `python3 -m compileall dashboard`; runtime verification initially failed because the base interpreter lacked `pandas` and `streamlit`.
- [20:19] Created a local `.venv` and installed the project there with `./.venv/bin/pip install .` so KPI and app-start checks could run against the actual dependency set.
- [20:19] Verified the new KPI functions on an inline sample: weekly cancellation and no-show rates returned tidy `week`/`rate` output with `W-SUN` week-ending Sunday labels.
- [20:19] Verified against the dataset via `load_all()`: max visit date is `2025-12-30`, so the dashboard correctly treats `2025-12-28` as the last complete week for tile values and deltas.
- [20:19] Verified `./.venv/bin/streamlit run dashboard/app.py --server.headless true --server.port 8501` started successfully and served the dashboard before shutdown.
- [20:20] Created and switched to the requested feature branch `feat/operational-leakage-kpis` so the work is aligned with the intended PR branch.
