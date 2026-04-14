# KPI Scope

## 1. Stakeholder framing

The dashboard is for the **Head of Operations**. This stakeholder makes weekly and monthly decisions about doctor scheduling, where no-show and cancellation interventions are needed, which visit types or diagnosis categories are creating operational pressure, and whether service quality is holding while demand shifts. The current data is strongest on the visits side, not on clean visit-linked economics, so the most useful gap to fill is operational visibility: where booked demand is turning into completed care, where it is leaking out through cancellations and no-shows, how clinician time is being consumed, and whether the completed experience remains acceptable for patients.

## 2. KPI longlist

### Visits-side KPIs: operations, quality, utilization

- **Scheduled visit volume**: counts booked visits to show total operational demand; source columns: `visits.visit_id`, `visits.visit_date`.
- **Completed visit volume**: counts visits with `status = 'completed'` to show delivered consultations; source columns: `visits.visit_id`, `visits.visit_date`, `visits.status`.
- **Completion rate**: share of all booked visits that end as `completed`; source columns: `visits.visit_id`, `visits.status`.
- **Cancellation rate**: share of visits with `status = 'cancelled'` to show operational leakage before care happens; source columns: `visits.visit_id`, `visits.status`.
- **No-show rate**: share of visits with `status = 'no_show'` to show attendance failure; source columns: `visits.visit_id`, `visits.status`.
- **Visit type mix**: distribution of visits across consultation formats or service modes; source columns: `visits.visit_id`, `visits.visit_type`.
- **Diagnosis demand mix**: distribution of scheduled demand by reason or intake category; source columns: `visits.visit_id`, `visits.diagnosis_category`.
- **Average completed consultation duration**: mean consultation length for completed care only; source columns: `visits.visit_id`, `visits.status`, `visits.duration_min`.
- **Average patient satisfaction**: mean satisfaction for completed visits as a quality signal; source columns: `visits.visit_id`, `visits.status`, `visits.satisfaction_score`.
- **Doctor utilization minutes**: total completed consultation minutes by doctor or period to show clinical capacity usage; source columns: `visits.visit_id`, `visits.doctor_id`, `visits.visit_date`, `visits.status`, `visits.duration_min`.

### Revenue-side KPIs: totals, refunds, payment mix

- **Gross revenue total**: sum of transaction amounts to show revenue throughput in the revenue table alone; source columns: `revenue.transaction_id`, `revenue.amount`, `revenue.transaction_date`.
- **Refunded amount total**: sum of amounts where `refunded = true` to show revenue reversal volume; source columns: `revenue.transaction_id`, `revenue.amount`, `revenue.refunded`, `revenue.transaction_date`.
- **Refund rate**: share of transactions or amount that end up refunded to show payment friction; source columns: `revenue.transaction_id`, `revenue.amount`, `revenue.refunded`, `revenue.transaction_date`.
- **Payment type mix**: distribution of transaction volume and value by payment method; source columns: `revenue.transaction_id`, `revenue.payment_type`, `revenue.amount`.

### Explicitly rejected cross-cutting KPIs: would require a reliable revenue-to-visit join

- **Revenue per visit**: revenue normalized by delivered visits, which would require trustworthy visit-level linkage; source columns: `revenue.visit_id`, `revenue.amount`, `revenue.refunded`, `visits.visit_id`, `visits.status`.
- **Revenue by visit type**: revenue split across `visit_type`, which would require mapping revenue rows to the right visit record; source columns: `revenue.visit_id`, `revenue.amount`, `visits.visit_id`, `visits.visit_type`.
- **Revenue by doctor or specialization**: doctor-level monetization, which would require joining revenue rows to `visits.doctor_id` and then `doctors.specialization`; source columns: `revenue.visit_id`, `revenue.amount`, `visits.visit_id`, `visits.doctor_id`, `doctors.specialization`.
- **Revenue by diagnosis category**: economic performance by clinical demand type, which would require joining revenue rows to `visits.diagnosis_category`; source columns: `revenue.visit_id`, `revenue.amount`, `visits.visit_id`, `visits.diagnosis_category`.

## 3. KPI shortlist with rationale

### 1. Scheduled visit volume by week and visit type

This is the anchor demand KPI for the Head of Operations. It answers: *how much demand is entering the system, when, and in what form?* It is computed as the count of `visits.visit_id`, grouped by `visit_date` at weekly grain and segmented by `visit_type`. There is no known consistency caveat that invalidates this metric because the visits table is complete on those fields and the requested foreign keys hold. The decision it supports is capacity planning: whether to rebalance doctor schedules, reserve coverage for specific visit types, or investigate peaks in demand before they turn into service problems.

### 2. Cancellation rate

This answers: *where are booked visits being lost before care is delivered?* It is computed as `count(status = 'cancelled') / count(all visits)` for a chosen time grain. The caveat from [data-consistency-review.md](data-consistency-review.md) matters here: cancelled rows can carry `duration_min > 0`, but that time should be treated as operational handling time, not completed consultation time. That caveat does **not** block the cancellation-rate KPI itself; it simply means the same rows must remain in the cancellation numerator and must not be reclassified as delivered care. The operational decision is whether to tighten reminder workflows, booking windows, or schedule buffers in teams or periods with elevated cancellations.

### 3. No-show rate

This answers: *where are patients failing to attend after booking?* It is computed as `count(status = 'no_show') / count(all visits)` over time and optionally by visit type or diagnosis category. The relevant caveat is again from [data-consistency-review.md](data-consistency-review.md): `no_show` rows have `duration_min = 0` consistently, which supports treating them as a clean attendance-failure status distinct from cancelled visits. The decision it supports is intervention targeting: where to add reminders, confirmation flows, overbooking rules, or stricter booking policies.

### 4. Average patient satisfaction for completed visits

This answers: *is the delivered care experience stable while operations are scaled or rebalanced?* It is computed as the average of `satisfaction_score` for rows where `status = 'completed'`. The consistency review matters because satisfaction is null for all cancelled and no-show rows and populated for completed rows, so the metric should stay explicitly limited to completed visits rather than treating nulls as zeros. The decision it supports is quality management: where to investigate specific service lines, doctors, or demand segments that show deteriorating patient experience.

### 5. Doctor utilization minutes from completed consultations

This answers: *how much clinician capacity is actually being consumed by completed care?* It is computed as the sum of `duration_min` for `status = 'completed'`, grouped by `doctor_id` and time period, with optional rollups by specialization or region through the clean doctor dimension. The critical caveat from [data-consistency-review.md](data-consistency-review.md) is that cancelled rows with non-zero `duration_min` must be excluded because that duration likely represents cancellation handling rather than consultation time. The decision it supports is staffing and schedule design: which doctors or cohorts are over- or under-loaded, and where supply should be shifted.

### 6. Gross revenue trend, labeled as unlinked from visits

This answers a narrower question for the Head of Operations: *is the payment stream moving up or down over time, independent of visit-level operational attribution?* It is computed inside `revenue.csv` only as the sum of `amount` by `transaction_date`, without attempting to join to visits. The caveat is explicit and material: [data-consistency-review.md](data-consistency-review.md) concludes that `revenue.visit_id` is not a trustworthy visit-level foreign key, and J. confirmed in [email-draft.md](email-draft.md) that the task should proceed with our own assumptions because part of the data is random. This KPI therefore belongs in a separate revenue panel and must not be narrated as “revenue generated by visits shown above.” The decision it supports is limited but still useful: whether a billing or payment-processing issue may need attention in periods where transaction totals move sharply.

### 7. Refund rate, labeled as unlinked from visits

This answers: *is there a payment-quality problem that operations should be aware of, even if it cannot be tied back to specific visits?* It is computed within `revenue.csv` as either `count(refunded = true) / count(all transactions)` or `sum(amount where refunded = true) / sum(amount)` at the chosen time grain. The same separation caveat applies: it must not be interpreted as refunds caused by particular doctors, visit types, or diagnosis groups because the revenue-to-visit join is unreliable per [data-consistency-review.md](data-consistency-review.md). The operational decision it supports is whether to escalate payment friction or refund spikes as a separate process issue, not whether to change visit routing.

## 4. Explicit rejections

### Revenue per visit

This KPI is rejected. It is the most tempting naive metric, but it depends on a trustworthy visit-level join between `revenue.visit_id` and `visits.visit_id`, which [data-consistency-review.md](data-consistency-review.md) explicitly rejects: the IDs share a namespace but do not reliably identify the same real-world visit event. The recruiter reply from J. in [email-draft.md](email-draft.md) confirms that the correct approach is to proceed with our own assumptions because part of the data is random. Publishing “revenue per visit” would create false precision and would be analytically misleading.

### Revenue by doctor or specialization

This KPI is rejected because it would require assigning revenue rows to `visits.doctor_id` and then to doctor attributes in `doctors.csv`. That path inherits the same broken revenue-to-visit linkage, so any doctor leaderboard or specialization profitability view would mostly reflect matching-ID collisions rather than true economic performance. A naive analyst could easily build it because the join keys exist syntactically; that is exactly why it needs to be rejected explicitly.

### Revenue by diagnosis category

This KPI is rejected because it would require joining revenue to `visits.diagnosis_category`, which is already only safe to interpret as schedulable or intake metadata rather than confirmed post-consult diagnosis for non-completed visits. Even if diagnosis semantics were perfect, the revenue join is not. Combining two uncertain layers would produce a polished but indefensible chart about which clinical categories are “worth more,” and that would be a bad decision basis for the chosen stakeholder.

## 5. Dashboard layout sketch

```md
Top row: 4 operational tiles | Scheduled visits | Cancellation rate | No-show rate | Avg satisfaction (completed only)

Middle row:
- Left: weekly visit volume time series split by visit type
- Right: doctor utilization chart or heatmap using completed-consultation minutes only

Bottom row:
- Left: diagnosis demand mix or visit type mix panel for operational routing context
- Right: revenue panel with gross revenue trend + refund rate
  Disclaimer: "Revenue metrics are shown from `revenue.csv` only and are not linked to visit-level operational KPIs because the revenue-to-visit join is not reliable."
```

The information hierarchy is deliberate. The Head of Operations should first see operational flow and service leakage, then capacity usage, then supporting context, and only then the separate revenue view with a prominent disclaimer instead of a buried footnote.

## 6. Output location and implementation boundary

This scope decision is recorded in `docs/kpi-scope.md` as the second decision document in `docs/` after [data-consistency-review.md](data-consistency-review.md). Together those two documents define the implementation boundary: build the dashboard around operational KPIs for the Head of Operations, include a clearly segregated revenue panel, and reject any metric that pretends the current data can support reliable revenue-to-visit attribution.
