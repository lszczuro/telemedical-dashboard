# Data Consistency Review

This note consolidates the data-consistency findings established so far and records the working assumptions to use if no stakeholder clarification arrives before the KPI work continues.

## Revenue-to-visit linkage

**Evidence from the data**

- Source: session LSZ-17 in [logs/sessions/2026-04-13_revenue-cardinality.md](/var/tmp/vibe-kanban/worktrees/1944-data-consistency/telemedical-dashboard/logs/sessions/2026-04-13_revenue-cardinality.md).
- `revenue.csv` has `10,000` rows but only `6,362` unique `visit_id`s; `2,612` visits have multiple revenue rows and one `visit_id` appears up to `6` times.
- `9,999` of `10,000` revenue rows have a different `patient_id` than the row with the same `visit_id` in `visits.csv`.
- Date alignment is also very weak: only `9` of `10,000` revenue rows (`0.09%`) land on the same day as the joined visit, `127` (`1.27%`) are within `7` days, `566` (`5.66%`) are within `30` days, and `4,911` (`49.11%`) occur before the joined visit date.
- Within a single `visit_id`, transaction dates span a median of `406` days and up to `1,083` days.

**Working interpretation**

`revenue.visit_id` does not currently behave like a trustworthy visit-level foreign key to `visits.visit_id`. The safest working interpretation is that the two columns share an identifier namespace but do not reliably identify the same real-world visit event.

**Confidence**

`likely`

**Note on `revenue.patient_id` mismatch**

The `revenue.patient_id` mismatch is no longer treated as a standalone finding. It is downgraded to a consequence of the broader revenue-linkage problem documented in session LSZ-17: if `revenue.visit_id` is not a reliable join key, the near-total `patient_id` disagreement is expected fallout rather than a separate defect category.

## Cancelled duration semantics

**Evidence from the data**

- Source: ad-hoc query on `/home/lszczuro/telemedi-data/visits.csv` run in this session.
- `completed`: `7,823` rows, `0` zero-duration rows, median `32` minutes, mean `32.23`, range `5` to `60`.
- `cancelled`: `1,385` rows, `115` zero-duration rows (`8.30%`), `1,270` non-zero rows (`91.70%`), median `5` minutes, mean `5.11`, range `0` to `10`.
- `no_show`: `792` rows, `792` zero-duration rows (`100%`), median `0`, mean `0.00`, range `0` to `0`.

**Working interpretation**

- `completed`: an actual consultation took place and `duration_min` reflects visit length.
- `cancelled`: the row was not a completed consultation, but `duration_min` likely records short operational handling time around the cancellation rather than clinical visit time.
- `no_show`: the patient did not attend and no time was recorded beyond the missed booking itself.

**Confidence**

`likely`

## Residual observation: diagnosis is populated for non-completed visits

**Evidence from the data**

- Source: [logs/sessions/2026-04-13_data-inventory.md](/var/tmp/vibe-kanban/worktrees/1944-data-consistency/telemedical-dashboard/logs/sessions/2026-04-13_data-inventory.md).
- `diagnosis_category` has `0` nulls in `visits.csv`.
- That means all `1,385` `cancelled` rows and all `792` `no_show` rows still carry a diagnosis category.
- At the same time, `satisfaction_score` is null for all `cancelled` and `no_show` rows and never null for `completed`, which suggests status-specific semantics do exist elsewhere in the table.

**Working interpretation**

`diagnosis_category` may represent the scheduled reason for visit or intake classification rather than a post-consult diagnosis. That would make it usable for demand-mix analysis but not as evidence that a consultation actually happened.

**Confidence**

`unknown`

## Fallback assumptions if no clarification arrives

- Revenue KPIs: do not treat `revenue.visit_id` as confirmed visit-level linkage. If revenue must still be shown, label it as a fallback metric based on matching IDs rather than confirmed visit-level revenue.
- Cancelled visits: treat `cancelled` as a non-completed visit status and exclude its `duration_min` from any metric intended to represent clinician consultation time.
- Diagnosis category: treat `diagnosis_category` as schedulable/intake metadata that can exist before completion, not as proof that a visit was completed.
