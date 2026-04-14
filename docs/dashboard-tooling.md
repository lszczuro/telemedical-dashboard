# Dashboard Tooling Decision

## 1. Constraints

- **Telemedi-stated tool set:** the recruitment posting explicitly names `Power BI`, `Metabase`, and `Streamlit`, so the decision should start from those options instead of inventing a custom stack.
- **Approach-first evaluation:** J. replied on **14 Apr 2026** that the task is "przede wszystkim o podejście do tematu" and that part of the data is random, which means the final artifact should make assumptions, caveats, and reasoning visible rather than hiding them behind polished output alone.
- **Fixed KPI scope:** [kpi-scope.md](kpi-scope.md) already locks the dashboard around the **Head of Operations**, with operational KPIs first and a revenue panel that stays explicitly separate from visit-linked metrics.
- **Data and environment shape:** source CSVs are outside the repo and are resolved through `TELEMEDI_DATA_DIR` in `.env`, per [README.md](../README.md). The chosen tool therefore needs a simple local file-loading path rather than a production-grade ingestion pipeline.
- **No deployment target:** this is a recruitment task, not a production rollout. The deliverable only needs to run locally and communicate the analytical approach clearly.
- **Timebox remaining:** implementation now sits inside the remaining time of a roughly `6-8h` recruitment exercise, so setup overhead matters more than long-term platform sophistication.
- **Revenue disclaimer must stay prominent:** [data-consistency-review.md](data-consistency-review.md) and [kpi-scope.md](kpi-scope.md) require revenue metrics to remain visibly segregated because `revenue.visit_id` is not a trustworthy visit-level join.

## 2. Candidate Evaluation

### Streamlit

`Streamlit` handles the KPI set in [kpi-scope.md](kpi-scope.md) directly: it can load the CSVs from `TELEMEDI_DATA_DIR`, compute the operational metrics in Python, render tiles, trend charts, mix charts, and a clearly separated revenue panel in one codebase. Its setup cost is low for a `6-8h` task because the app can stay as a small Python package plus a single entry-point script, with no metadata modeling layer, no BI server, and no GUI configuration step. It also makes the *approach* highly visible: the KPI logic, caveat handling, and revenue disclaimer all live in versioned files that the recruitment team can inspect. For the AI workflow story, that is the cleanest path because AI-assisted reasoning stays visible end-to-end in markdown, Python, and commit history rather than disappearing into manual dashboard clicks.

### Metabase

`Metabase` could render most of the KPIs, especially the visit-side charts and summary cards, and it would support a separate revenue section if the source tables were loaded into a database first. The problem is setup cost: for a short recruitment task it adds database loading, Metabase configuration, and dashboard authoring overhead before any KPI narrative is visible. Its "approach first" visibility is mixed. The final dashboard would look credible, but much of the reasoning would live outside the repo in saved questions and GUI state, which weakens the trace from assumptions to artifact. The AI workflow story is also weaker because AI can help with SQL drafts and documentation, but the actual dashboard assembly is partly hidden inside the product UI.

### Power BI Desktop

`Power BI Desktop` is a realistic candidate because Telemedi named it explicitly and it is a common tool for operations dashboards. It can certainly represent the KPI set, including tiles, time series, slicers, and a clearly boxed revenue section with a disclaimer text box. The friction is disproportionately high here: the task environment is repository-first and local, while Power BI Desktop introduces OS constraints, manual model setup, and a file-based artifact that is much harder to review in git. That undermines the "approach first" criterion because the reasoning is less inspectable than the final visuals. The AI workflow story also becomes weaker because the main deliverable lives in a GUI-authored `.pbix` file where AI assistance is harder to show cleanly and reviewers cannot diff the logic easily.

## 3. Decision

**Chosen tool: `Streamlit`**

### 5x why chain

1. **Why choose Streamlit?** Because it is the fastest path from the fixed KPI scope to a runnable local dashboard while keeping all logic, caveats, and presentation decisions in plain files under version control.
2. **Why does that matter here?** Because J.'s 14 Apr 2026 reply makes the evaluation criterion the analytical approach, not just the final screenshot, and code-plus-docs expose that approach more clearly than GUI state.
3. **Why is code visibility more important than BI-tool convenience?** Because this task already depends on explicit assumptions from [data-consistency-review.md](data-consistency-review.md) and [kpi-scope.md](kpi-scope.md), especially the revenue disclaimer; those assumptions need to stay visible in the implementation, not buried in a dashboard editor.
4. **Why is Streamlit better than Metabase and Power BI Desktop on that axis?** `Metabase` adds database and GUI configuration overhead that hides part of the logic, while `Power BI Desktop` adds even more manual modeling friction plus a binary artifact that is awkward to review, diff, and explain in an AI-assisted workflow log.
5. **Why is that the right trade-off for the Head of Operations stakeholder?** Because the stakeholder needs a simple, readable operational dashboard with obvious KPI definitions, trend context, and a prominent revenue caveat, and Streamlit lets the implementation optimize directly for clarity and decision support instead of BI-platform ceremony.

### Why Streamlit over each rejected candidate

- **Over Metabase:** no database/bootstrap layer is required, KPI logic can stay in Python next to the documentation, and the repo remains the single source of truth for both computation and UI wording.
- **Over Power BI Desktop:** no Windows/Desktop dependency is introduced, the output stays reviewable in git, and the AI workflow remains inspectable instead of ending in an opaque `.pbix` file.

### Stakeholder fit

The [Head of Operations defined in `kpi-scope.md`](kpi-scope.md) needs quick answers about demand, leakage, utilization, and service quality. `Streamlit` is sufficient for that because it supports a compact, narrative dashboard where operational KPIs lead, secondary segmentation follows, and the revenue panel stays visibly separate instead of competing with the main operational story.

### Revenue disclaimer handling

This choice also helps with the revenue-side disclaimer. In `Streamlit`, the disclaimer can sit directly above the revenue panel as normal app text, styled as an alert or caption that is impossible to miss. That is safer than tools where disclaimer text becomes an optional dashboard note or a small annotation detached from the chart it qualifies.

### Concrete implementation path

The implementation path is: use `streamlit` for the UI, `pandas` for CSV loading and KPI computation, and a small `dashboard/` package for app code. The likely structure is `dashboard/app.py` plus one or two helper modules such as `dashboard/data.py` and `dashboard/kpis.py`, run locally with `streamlit run dashboard/app.py`.

## 4. Explicit Rejections

### Custom `Next.js` + charting library dashboard

This is the most tempting wrong choice. It would maximize UI freedom, but it is over-engineered for the timebox and misaligned with the prompt, which asks for a defensible tooling choice in the context of Telemedi's own listed tools. It would spend scarce time on frontend scaffolding, package selection, and chart plumbing while making the submission look like a generic product prototype rather than a focused analytics exercise. It also creates extra room to polish visuals while under-investing in the explicit KPI caveats and assumptions that the recruitment team asked to see.

### Spreadsheet export (`Excel` or `Google Sheets`)

This is rejected because it weakens the AI-workflow story and the decision record. A spreadsheet can show numbers, but it does not preserve the end-to-end analytical reasoning nearly as well as a repo-based app plus docs. It also makes the disclaimer and stakeholder framing easier to dilute across tabs, comments, or formatting rather than keeping them structurally tied to the dashboard view.

## 5. First Implementation Story

The next branch should create the initial dashboard entry point only: `dashboard/app.py` as the runnable Streamlit app, plus the smallest necessary helper module for file loading if needed. The entry command should be `streamlit run dashboard/app.py`. The smallest viable working version is a local app that reads the four CSVs from `$TELEMEDI_DATA_DIR`, confirms the load in the UI, renders one placeholder operational chart from `visits.csv`, and shows the revenue disclaimer text in a dedicated panel even before the full KPI set is implemented.

## 6. Output Location

This decision record lives in `docs/dashboard-tooling.md` as the third pre-implementation document in `docs/`, after [data-consistency-review.md](data-consistency-review.md) and [kpi-scope.md](kpi-scope.md). Together, those three documents define the implementation boundary: what data assumptions are safe, which KPIs belong in scope, and which dashboard stack the follow-up implementation stories must use.
