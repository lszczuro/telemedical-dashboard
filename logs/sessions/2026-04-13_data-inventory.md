# Session Goal
Understand the structure, completeness, and basic relational integrity of the 4 source CSV files to guide KPI selection and validation needs.

- [14:41] Started data inventory session and resolved `TELEMEDI_DATA_DIR` from `.env`.
- [14:41] Located `patients.csv`, `doctors.csv`, `visits.csv`, and `revenue.csv` in `/home/lszczuro/telemedi-data`.
- [14:42] Scanned all four CSVs with an ad-hoc `python3` script using the standard library; collected row counts, inferred types, null counts, categorical cardinalities, and date ranges.
- [14:42] Verified requested foreign keys and checked visit-status null semantics plus extra revenue-to-visit consistency signals.

## patients.csv

- Row count: 3,000
- Columns and inferred types: `patient_id` string, `age_group` string, `gender` string, `region` string, `registration_date` date, `subscription_type` string
- Date range: `registration_date` 2019-01-01 to 2025-11-30
- Unique categorical values: `age_group` 6, `gender` 3, `region` 7, `subscription_type` 3
- Nulls per column: `patient_id` 0, `age_group` 0, `gender` 0, `region` 0, `registration_date` 0, `subscription_type` 0
- Observation: Clean dimension table with no missing data and low-cardinality categoricals, so it is safe to use as a reference table for segmentation KPIs.

## doctors.csv

- Row count: 50
- Columns and inferred types: `doctor_id` string, `specialization` string, `experience_years` int, `rating` float, `active_since` date, `region` string
- Date range: `active_since` 2018-02-11 to 2024-05-16
- Unique categorical values: `specialization` 10, `region` 7
- Nulls per column: `doctor_id` 0, `specialization` 0, `experience_years` 0, `rating` 0, `active_since` 0, `region` 0
- Observation: Also clean and complete; small enough to trust for doctor-level grouping and to use as the target for `visits.doctor_id` validation.

## visits.csv

- Row count: 10,000
- Columns and inferred types: `visit_id` string, `patient_id` string, `doctor_id` string, `visit_date` date, `visit_type` string, `duration_min` int, `status` string, `diagnosis_category` string, `satisfaction_score` int
- Date range: `visit_date` 2023-01-01 to 2025-12-30
- Unique categorical values: `visit_type` 3, `status` 3, `diagnosis_category` 10
- Nulls per column: `visit_id` 0, `patient_id` 0, `doctor_id` 0, `visit_date` 0, `visit_type` 0, `duration_min` 0, `status` 0, `diagnosis_category` 0, `satisfaction_score` 2,177
- Null semantics: `satisfaction_score` is null for all 1,385 `cancelled` visits and all 792 `no_show` visits, and never null for 7,823 `completed` visits, which looks consistent with business meaning
- Foreign keys: every `patient_id` in `visits` exists in `patients`; every `doctor_id` in `visits` exists in `doctors`
- Observation: Requested FKs hold and the score-null pattern makes sense, but `diagnosis_category` is still populated for all `cancelled` and `no_show` rows and 1,270 `cancelled` visits have non-zero `duration_min`, which should be treated as a validation hotspot before KPI design.

## revenue.csv

- Row count: 10,000
- Columns and inferred types: `transaction_id` string, `visit_id` string, `patient_id` string, `amount` float, `payment_type` string, `transaction_date` date, `refunded` bool
- Date range: `transaction_date` 2023-01-01 to 2025-12-30
- Unique categorical values: `payment_type` 4, `refunded` 2
- Nulls per column: `transaction_id` 0, `visit_id` 0, `patient_id` 0, `amount` 0, `payment_type` 0, `transaction_date` 0, `refunded` 0
- Foreign keys: every `visit_id` in `revenue` exists in `visits`
- Observation: The requested FK holds, but the table is not one-row-per-visit (`6,362` unique `visit_id`s across `10,000` rows, with `2,612` visits repeated and up to `6` revenue rows for one visit) and `revenue.patient_id` disagrees with `visits.patient_id` in `9,999` rows, so any revenue KPI should key on `visit_id` first and treat `revenue.patient_id` as unreliable until clarified.
