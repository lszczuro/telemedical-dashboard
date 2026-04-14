# Dashboard MVP Design

## Goal

Deliver the smallest end-to-end Streamlit dashboard artifact that loads the four Telemedi source CSVs, computes KPI #1 from `docs/kpi-scope.md`, renders it for the Head of Operations, and reserves the revenue panel contract with the required disclaimer.

## Scope

This design covers only the first dashboard vertical slice:

- Runnable Streamlit app at `dashboard/app.py`
- Data loading isolated in `dashboard/data.py`
- KPI #1 computation isolated in `dashboard/kpis.py`
- KPI #1 rendered as a weekly time-series chart segmented by `visit_type`
- Visible placeholder area for KPIs #2 through #5
- Revenue disclaimer panel at the bottom of the page
- Dependency declaration and minimal README run instructions

Out of scope:

- KPI implementations beyond KPI #1
- Revenue metric computation
- Validation frameworks or explicit data schemas
- Caching
- Custom styling beyond Streamlit defaults
- Automated tests in this story

## Stakeholder and Information Hierarchy

The dashboard serves the **Head of Operations**. The page must preserve the layout contract from section 5 of `docs/kpi-scope.md` even though only one KPI is implemented now.

Top to bottom:

1. Page title and one-line framing for the Head of Operations
2. KPI #1 chart: scheduled visit volume by week and visit type
3. Visible placeholders for KPIs #2 through #5
4. Revenue panel with disclaimer at the bottom

The revenue panel remains visually separate from operational KPIs so later work cannot accidentally present revenue as attributable to visit-level operational data.

## Architecture

The dashboard will be implemented as a small `dashboard/` package with three focused modules:

- `dashboard/app.py`: Streamlit entry point and page layout only
- `dashboard/data.py`: environment resolution and CSV decoding
- `dashboard/kpis.py`: pure pandas KPI computation

This keeps I/O, transformation, and presentation concerns separate. `kpis.py` stays free of Streamlit imports so the KPI logic remains easy to test later without app runtime dependencies.

## Data Loading Design

`dashboard/data.py` will expose a single `load_all()` function that returns a frozen dataclass named `TelemediData` with four fields:

- `visits: pd.DataFrame`
- `patients: pd.DataFrame`
- `doctors: pd.DataFrame`
- `revenue: pd.DataFrame`

Reason for this shape:

- Clean attribute access in the app layer
- Immutable container semantics for loaded source datasets
- IDE autocomplete and clearer call sites than raw dict access

`load_all()` will call `load_dotenv()` inside the function, not at module import time. This avoids import side effects and keeps pure-data modules easy to reuse in later tests.

Path resolution rules:

- Read `TELEMEDI_DATA_DIR` from the environment after `load_dotenv()`
- If the variable is missing or empty, raise a human-readable error that explicitly names `TELEMEDI_DATA_DIR`
- Build source paths relative to that directory
- Read the four required source files with `pandas.read_csv`

Date parsing is treated as decoding and belongs in the I/O layer. The loaders will parse date columns during CSV reads:

- `visits.csv`: `parse_dates=["visit_date"]`
- `revenue.csv`: `parse_dates=["transaction_date"]`
- `patients.csv` and `doctors.csv`: no date parsing unless later inspection shows a real date column is present and required by the app

No schema validation, coercion framework, or caching is included in this story.

## KPI #1 Computation Design

`dashboard/kpis.py` will implement one pure function for KPI #1:

`compute_scheduled_visit_volume_by_week_and_type(visits: pd.DataFrame) -> pd.DataFrame`

Behavior:

- Treat every row in `visits` as a scheduled visit
- Group by weekly buckets derived from `visit_date`
- Segment by `visit_type`
- Return a tidy DataFrame with exactly these columns:
  - `week`
  - `visit_type`
  - `visit_count`

Week grain:

- Monday-start, Sunday-end ISO-style weeks
- Implemented with pandas weekly grouping using `W-SUN`
- The output `week` value is labeled by the week-ending Sunday timestamp

This function performs only aggregation logic. It does not import Streamlit, read environment variables, or format UI strings.

## Visualization Design

The chart library choice is `altair`.

Reason for the choice:

- Integrates cleanly with Streamlit
- Matches the tidy KPI output shape naturally
- Supports explicit chart title, axis labeling, and line color encoding with low implementation overhead

The KPI #1 chart will be a multi-series line chart:

- X-axis: `week`
- Y-axis: `visit_count`
- Color encoding: `visit_type`
- Title communicates the metric directly
- Caption explains the business meaning: scheduled visit volume per week, segmented by consultation format, as the anchor demand metric for the Head of Operations

## Streamlit Page Structure

`dashboard/app.py` will:

1. Set up the page and top-level title
2. Render one line of stakeholder framing
3. Call `load_all()` and pass `data.visits` into the KPI function
4. Render the KPI #1 chart
5. Render visible “Coming next” placeholders for KPIs #2 to #5
6. Render the revenue disclaimer panel at the bottom

The revenue panel will use `st.warning` with a short heading and the disclaimer body from `docs/kpi-scope.md`:

> Revenue metrics are shown from `revenue.csv` only and are not linked to visit-level operational KPIs because the revenue-to-visit join is not reliable.

This locks the visual contract now so later revenue charts are added inside the already-disclaimed section.

## Dependencies and Project Files

Dependencies will be declared in `pyproject.toml`, not `requirements.txt`.

Dependencies:

- `streamlit`
- `pandas`
- `altair`
- `python-dotenv`

Versions will be pinned to current stable releases available during implementation.

Supporting files:

- Update `README.md` with exactly three run lines:
  - install dependencies
  - set `TELEMEDI_DATA_DIR` with reference to `.env.example`
  - run the Streamlit app

## Error Handling

The only required fail-fast path in this story is missing configuration:

- If `TELEMEDI_DATA_DIR` is not set, loading fails immediately with a readable error naming that variable

Other file-level or data-quality issues are allowed to surface through pandas exceptions in this MVP. The story goal is a runnable artifact, not a full validation and diagnostics layer.

## Implementation Boundary

This design deliberately stops at one operational KPI and one revenue disclaimer panel. It enables later stories to add more KPI functions and Streamlit sections by following the same separation of concerns:

- decode source data in `data.py`
- compute KPI logic in `kpis.py`
- render layout and messaging in `app.py`
