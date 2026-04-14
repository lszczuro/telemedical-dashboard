# Dashboard MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first runnable Streamlit dashboard slice that loads Telemedi CSVs, computes KPI #1, renders it with the required placeholders and disclaimer, and documents how to run it.

**Architecture:** Add a small `dashboard/` package with strict responsibility boundaries: `data.py` for environment-aware CSV decoding, `kpis.py` for pure pandas aggregation, and `app.py` for Streamlit layout only. Keep the implementation minimal, avoid schema validation and caching, and verify behavior manually because automated tests are explicitly out of scope for this story.

**Tech Stack:** Python, pandas, Streamlit, Altair, python-dotenv

---

## File Structure

- Create: `dashboard/__init__.py`
- Create: `dashboard/app.py`
- Create: `dashboard/data.py`
- Create: `dashboard/kpis.py`
- Create or modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `logs/sessions/2026-04-14_dashboard-mvp.md`

### Task 1: Project Scaffolding and Dependencies

**Files:**
- Create: `dashboard/__init__.py`
- Create or modify: `pyproject.toml`
- Modify: `logs/sessions/2026-04-14_dashboard-mvp.md`

- [ ] **Step 1: Create the dashboard package marker**

```python
# dashboard/__init__.py
```

- [ ] **Step 2: Add pinned runtime dependencies in `pyproject.toml`**

Use a minimal project file if none exists:

```toml
[project]
name = "telemedi-dashboard"
version = "0.1.0"
description = "Telemedi recruitment dashboard MVP"
requires-python = ">=3.11"
dependencies = [
  "altair==5.5.0",
  "pandas==2.2.3",
  "python-dotenv==1.1.1",
  "streamlit==1.44.1",
]
```

- [ ] **Step 3: Log dependency format and package choice**

Append a bullet to `logs/sessions/2026-04-14_dashboard-mvp.md` recording that dependencies are declared in `pyproject.toml` and that `altair` is the chosen chart library.

- [ ] **Step 4: Verify the project metadata parses**

Run: `python - <<'PY'\nimport tomllib, pathlib\nprint(tomllib.loads(pathlib.Path('pyproject.toml').read_text()))\nPY`

Expected: the command prints a parsed Python dict with the `project` table and the four dependency strings.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml dashboard/__init__.py logs/sessions/2026-04-14_dashboard-mvp.md
git commit -m "build: scaffold dashboard package"
```

### Task 2: Data Loading Module

**Files:**
- Create: `dashboard/data.py`
- Modify: `logs/sessions/2026-04-14_dashboard-mvp.md`

- [ ] **Step 1: Implement the frozen data container and env-aware loader**

```python
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


@dataclass(frozen=True)
class TelemediData:
    visits: pd.DataFrame
    patients: pd.DataFrame
    doctors: pd.DataFrame
    revenue: pd.DataFrame


def load_all() -> TelemediData:
    load_dotenv()
    data_dir = os.getenv("TELEMEDI_DATA_DIR", "").strip()
    if not data_dir:
        raise RuntimeError("Missing required environment variable: TELEMEDI_DATA_DIR")

    root = Path(data_dir)
    return TelemediData(
        visits=pd.read_csv(root / "visits.csv", parse_dates=["visit_date"]),
        patients=pd.read_csv(root / "patients.csv"),
        doctors=pd.read_csv(root / "doctors.csv"),
        revenue=pd.read_csv(root / "revenue.csv", parse_dates=["transaction_date"]),
    )
```

- [ ] **Step 2: Keep the error contract explicit**

Ensure the missing-env error text names `TELEMEDI_DATA_DIR` exactly, and do not call `load_dotenv()` at module import time.

- [ ] **Step 3: Log the loader-shape decision**

Append a bullet to `logs/sessions/2026-04-14_dashboard-mvp.md` recording that the app uses a frozen `TelemediData` container returned by a combined `load_all()` function.

- [ ] **Step 4: Verify the module imports cleanly**

Run: `python -c "from dashboard.data import TelemediData, load_all; print(TelemediData.__name__, callable(load_all))"`

Expected: `TelemediData True`

- [ ] **Step 5: Verify the fail-fast path**

Run: `env -u TELEMEDI_DATA_DIR python -c "from dashboard.data import load_all; load_all()"`

Expected: the command exits non-zero with a readable message containing `Missing required environment variable: TELEMEDI_DATA_DIR`.

- [ ] **Step 6: Commit**

```bash
git add dashboard/data.py logs/sessions/2026-04-14_dashboard-mvp.md
git commit -m "feat: add dashboard data loading"
```

### Task 3: KPI #1 Aggregation Module

**Files:**
- Create: `dashboard/kpis.py`
- Modify: `logs/sessions/2026-04-14_dashboard-mvp.md`

- [ ] **Step 1: Implement the pure KPI function**

```python
from __future__ import annotations

import pandas as pd


def compute_scheduled_visit_volume_by_week_and_type(visits: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        visits.assign(week=visits["visit_date"].dt.to_period("W-SUN").dt.end_time.dt.normalize())
        .groupby(["week", "visit_type"], dropna=False)
        .size()
        .reset_index(name="visit_count")
        .sort_values(["week", "visit_type"])
        .reset_index(drop=True)
    )
    return grouped[["week", "visit_type", "visit_count"]]
```

- [ ] **Step 2: Keep the module pure**

Do not import Streamlit, dotenv, or environment helpers in `dashboard/kpis.py`.

- [ ] **Step 3: Log the KPI boundary**

Append a bullet to `logs/sessions/2026-04-14_dashboard-mvp.md` recording that KPI #1 is computed in a pure pandas module returning tidy `week`, `visit_type`, `visit_count` output.

- [ ] **Step 4: Verify the function contract with an inline sample**

Run:

```bash
python - <<'PY'
import pandas as pd
from dashboard.kpis import compute_scheduled_visit_volume_by_week_and_type

visits = pd.DataFrame(
    {
        "visit_date": pd.to_datetime(["2026-04-06", "2026-04-07", "2026-04-13"]),
        "visit_type": ["video", "video", "chat"],
    }
)

result = compute_scheduled_visit_volume_by_week_and_type(visits)
print(result.to_dict(orient="records"))
PY
```

Expected: two rows for week-ending Sundays with keys `week`, `visit_type`, and `visit_count`.

- [ ] **Step 5: Commit**

```bash
git add dashboard/kpis.py logs/sessions/2026-04-14_dashboard-mvp.md
git commit -m "feat: add scheduled volume kpi"
```

### Task 4: Streamlit App Layout and README

**Files:**
- Create: `dashboard/app.py`
- Modify: `README.md`
- Modify: `logs/sessions/2026-04-14_dashboard-mvp.md`

- [ ] **Step 1: Implement the Streamlit page shell and KPI chart**

```python
from __future__ import annotations

import altair as alt
import streamlit as st

from dashboard.data import load_all
from dashboard.kpis import compute_scheduled_visit_volume_by_week_and_type


DISCLAIMER = (
    "Revenue metrics are shown from `revenue.csv` only and are not linked to "
    "visit-level operational KPIs because the revenue-to-visit join is not reliable."
)


def main() -> None:
    st.set_page_config(page_title="Telemedi Operations Dashboard", layout="wide")
    st.title("Telemedi Operations Dashboard")
    st.write(
        "For the Head of Operations: a weekly view of incoming demand, upcoming KPI slots, "
        "and the locked revenue caveat for later expansion."
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
    st.caption(
        "Scheduled visit volume per week, segmented by consultation format. "
        "Anchor demand metric for the Head of Operations."
    )

    st.subheader("Coming next")
    st.write("KPI #2: Cancellation rate")
    st.write("KPI #3: No-show rate")
    st.write("KPI #4: Average patient satisfaction")
    st.write("KPI #5: Doctor utilization minutes")

    st.subheader("Revenue Panel")
    st.warning(DISCLAIMER)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Update `README.md` with exactly three run lines**

Add these three lines under the data section:

```md
Install dependencies: `pip install .`
Set `TELEMEDI_DATA_DIR` in your environment as shown in [`.env.example`](.env.example).
Run the app: `streamlit run dashboard/app.py`
```

- [ ] **Step 3: Log the UI contract completion**

Append a bullet to `logs/sessions/2026-04-14_dashboard-mvp.md` recording that the app layout now matches the locked order: title and framing, KPI #1 chart, placeholders, revenue disclaimer panel.

- [ ] **Step 4: Verify the Python modules compile**

Run: `python -m compileall dashboard`

Expected: successful compilation of `dashboard/app.py`, `dashboard/data.py`, and `dashboard/kpis.py`.

- [ ] **Step 5: Verify the app starts with data configured**

Run: `TELEMEDI_DATA_DIR=/path/to/data streamlit run dashboard/app.py --server.headless true`

Expected: Streamlit starts without missing-file warnings when the directory contains the four CSVs, and the dashboard renders the title, chart, placeholders, and warning panel.

- [ ] **Step 6: Verify the missing-env behavior from the app entry point**

Run: `env -u TELEMEDI_DATA_DIR streamlit run dashboard/app.py --server.headless true`

Expected: startup fails fast with a human-readable error that names `TELEMEDI_DATA_DIR`.

- [ ] **Step 7: Commit**

```bash
git add dashboard/app.py README.md logs/sessions/2026-04-14_dashboard-mvp.md
git commit -m "feat: add dashboard mvp app"
```

### Task 5: Final Acceptance Sweep

**Files:**
- Modify: `logs/sessions/2026-04-14_dashboard-mvp.md`

- [ ] **Step 1: Re-run the key manual verification commands**

Run:

```bash
python -m compileall dashboard
python -c "from dashboard.data import TelemediData, load_all; print(TelemediData.__name__, callable(load_all))"
python - <<'PY'
import pandas as pd
from dashboard.kpis import compute_scheduled_visit_volume_by_week_and_type
sample = pd.DataFrame({"visit_date": pd.to_datetime(["2026-04-06"]), "visit_type": ["video"]})
print(compute_scheduled_visit_volume_by_week_and_type(sample).columns.tolist())
PY
```

Expected: compile succeeds, `TelemediData True` prints, and the KPI function reports `['week', 'visit_type', 'visit_count']`.

- [ ] **Step 2: Log the acceptance sweep**

Append a bullet to `logs/sessions/2026-04-14_dashboard-mvp.md` listing the verification commands run and whether the app-start checks passed with and without `TELEMEDI_DATA_DIR`.

- [ ] **Step 3: Commit**

```bash
git add logs/sessions/2026-04-14_dashboard-mvp.md
git commit -m "docs: log dashboard mvp verification"
```
