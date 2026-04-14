# Email Draft

Subject: Clarification on revenue-to-visit linkage in the recruitment dataset

Hi Telemedi Recruitment Team,

I am preparing KPI definitions for the recruitment task and want to confirm one data semantic before I lock in the assumptions.

Primary question:

Is `revenue.visit_id` intended to join directly to `visits.visit_id` as a visit-level revenue link?

The reason I’m asking is that the current data shape does not behave like a stable visit-level join: `revenue.csv` has `10,000` rows but only `6,362` unique `visit_id`s, `9,999` of `10,000` joined rows disagree on `patient_id`, only `0.09%` of revenue rows fall on the same day as the joined visit, and `49.11%` are dated before the joined visit. My current working interpretation is that the IDs share a namespace but do not reliably identify the same real visit. If that interpretation is wrong, the most helpful answer would be “yes, it should join directly” or “no, it actually means X”.

Secondary question:

For `visits.status = 'cancelled'`, should `duration_min` be treated as short operational handling time rather than consultation time?

The distribution suggests that interpretation: `completed` visits have median duration `32` minutes, `no_show` is always `0`, and `cancelled` has median duration `5` minutes with values only between `0` and `10`. My working interpretation is that cancelled rows are not completed consultations, even when `duration_min` is non-zero. If that is wrong, the most helpful answer would be “yes, treat it as non-consult operational time” or “no, it actually represents X”.

Fallback assumptions if I do not receive a reply before the deadline:

- Revenue linkage fallback: I will treat visit-level revenue as unconfirmed and explicitly label any revenue KPI as a fallback based on matching IDs rather than confirmed visit linkage.
- Cancelled duration fallback: I will exclude `cancelled.duration_min` from any KPI that is meant to represent completed consultation time.

Best regards,

[Your Name]

## Decision Log

- Decision: `hold`
- Timestamp: `2026-04-13 18:09 CEST`
- Reasoning: the clarification is useful, but sending external communication is a user-controlled action and this task does not need to block on a response. The draft is ready to send if needed, and the fallback assumptions above let the project proceed safely without waiting.

## Reply received

**From:** J., Telemedi recruitment
**Date:** 14 Apr 2026
**Content:** "Celne uwagi! Proszę przyjąć własne założenia, chodzi tu 
przede wszystkim o podejście do tematu, część danych jest losowych."

**Interpretation:** Hypothesis B (synthetic data with random elements)
confirmed. Fallback assumptions from `data-consistency-review.md` are 
the correct path forward. Proceeding with own assumptions explicitly 
labeled in the dashboard.