# Goal: investigate why `revenue` has up to 6 rows per `visit_id` and choose a defensible per-visit aggregation rule for future KPIs.

- [17:44] Started session on branch `feat/revenue-cardinality` / worktree branch `vk/a4e1-revenue-cardinal`; loaded `using-superpowers` and `workflow-logger` instructions.
- [17:45] Checked repo structure and README; confirmed source CSVs are external and resolved through `TELEMEDI_DATA_DIR` in `.env`.
- [17:46] Located source CSVs in `/home/lszczuro/telemedi-data`; inspected `revenue.csv` schema and confirmed analysis columns are `amount`, `payment_type`, `transaction_date`, and `refunded` at transaction grain.
- [17:47] Computed exact revenue-row cardinality by `visit_id`; found 6,362 visits in `revenue.csv`, with 2,612 multi-row visits and a maximum of 6 rows per visit.
- [17:49] Classified multi-row visits by which fields vary and cross-checked against `visits.csv`; most multi-row groups mix `amount`, `payment_type`, and `transaction_date`, and the join looks unreliable because 9,999 of 10,000 revenue rows have a different `patient_id` than the same `visit_id` in `visits.csv`.
- [17:51] Evaluated split-payment / installment / refund / retry / line-item hypotheses; partial-refund-like and installment-like shapes exist superficially, but patient/date inconsistencies make them weak evidence of true visit-level payment lifecycle.
- [17:53] Chose a provisional KPI rule: use the earliest non-refunded revenue row per `visit_id` ordered by `transaction_date`, treat visits with only refunded rows as revenue 0, and flag the metric as a best guess until source-key semantics are clarified.

## Revenue cardinality distribution

Visits in `revenue.csv`: 6,362

| revenue rows per `visit_id` | visit count |
| --- | ---: |
| 1 | 3,750 |
| 2 | 1,814 |
| 3 | 613 |
| 4 | 146 |
| 5 | 35 |
| 6 | 4 |

## Multi-row patterns

Among the 2,612 visits with multiple revenue rows, the field-difference patterns are:

| differing fields inside the same `visit_id` | visit count |
| --- | ---: |
| `amount`, `payment_type`, `transaction_date` | 1,867 |
| `amount`, `transaction_date` | 435 |
| `amount`, `payment_type`, `transaction_date`, `refunded` | 247 |
| `amount`, `transaction_date`, `refunded` | 58 |
| `amount`, `payment_type` | 5 |

Additional shape checks:

- Same `amount` across all rows: 0 visits.
- Same `transaction_date` across all rows: 5 visits.
- Same `payment_type` across all rows: 493 visits.
- At least one `refunded=true` row: 307 visits.
- Mix of refunded and non-refunded rows: 305 visits.
- All rows refunded: 2 visits.

The strongest concrete pattern is not a business payment pattern but a data-integrity problem: 9,999 of 10,000 revenue rows have a different `patient_id` than the row with the same `visit_id` in `visits.csv`, and multi-row visits usually contain 2-6 different revenue-side patient IDs. Transaction dates inside one `visit_id` also span a median of 406 days and up to 1,083 days. Example: `VIS003759` has non-refunded revenue rows on `2023-09-30` (`267.57`, `insurance`) and `2024-12-18` (`185.73`, `debit_card`), which does not look like a normal single-visit payment lifecycle.

## Hypothesis and candidate evaluation

Working hypothesis: repeated revenue rows under one `visit_id` are mostly synthetic-key collisions or otherwise unreliable linkage, not clean split payments / installments / retries / line items for one real visit. The evidence is the cross-table mismatch on `patient_id`, the long date gaps, and the frequent combination of different amounts and payment types inside one `visit_id`.

Candidate evaluation:

- Split payments: weak support only. Just 5 visits have all rows on the same date, which is the minimum shape I would expect for a true split payment.
- Installments: superficial support only. 435 visits have the same `payment_type` with different dates and no refunds, but the date gaps are often many months and the rows still fail the visit/patient consistency check.
- Partial refunds: some surface evidence. 305 visits mix `refunded=true` and `refunded=false`, but refund rows often differ in amount, payment type, and date by long intervals, so I do not trust these as true offsetting pairs.
- Retries after failed payment: not supported. No multi-row visit keeps the same `amount` across all rows, so the usual retry signature is absent.
- Separate line items per service: not supported. Only 5 visits share a common transaction date across all rows; that is far too small to explain the overall multiplicity.

## Provisional KPI rule

Best guess until clarified: compute revenue per visit as the earliest non-refunded row for that `visit_id`, ordered by `transaction_date` then `transaction_id`. If every row for a visit is `refunded=true`, set visit revenue to `0`.

Reasoning: `SUM` is the least defensible choice because it clearly overcounts mixed/collided rows; on multi-row visits, non-refunded `SUM` is 2.18x the earliest non-refunded amount at median, 5.69x at p90, and 56.11x at max. `LAST` and `MAX` are also arbitrary, but they are more exposed to unrelated later rows that appear months or years away from the visit. Earliest non-refunded is still only a provisional heuristic, not a trusted business rule, but it is the least inflationary and most stable fallback available from the current data. Refunded rows are excluded from the chosen amount rather than netted into it, because the refund linkage is too weak to support reliable netting.

## Open questions for next session

- Confirm with the data owner whether `revenue.visit_id` is intended to join directly to `visits.visit_id`; the current data strongly suggests that key is not trustworthy.
- Clarify whether `revenue.patient_id` or another hidden identifier should be used to validate visit-revenue linkage before any KPI is published.
- Ask what `refunded=true` means operationally: full reversal, partial reversal, or simply a transaction state flag.
- If the business needs revenue KPIs before clarification, decide whether the provisional earliest-non-refunded rule is acceptable for internal-only analysis or whether revenue KPIs should be blocked entirely.
