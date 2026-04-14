# Goal: investigate what `visits.status = 'cancelled'` means when `duration_min > 0`, compare it with `no_show` and `completed`, and decide KPI treatment for no-show rate, cancellation rate, and doctor utilization.
- [15:08] Started session for cancelled-duration semantics, loaded the required skills, reviewed prior repo findings, and confirmed the requested session slug `cancelled-duration-semantics`.
- [15:09] Loaded `/home/lszczuro/telemedi-data/visits.csv`, verified the status groups needed for this story, and recreated the key row counts: `1,385` cancelled, `792` no-show, and `7,823` completed visits.
- [15:10] Computed duration summaries for `cancelled` with `duration_min > 0`, `no_show`, and `completed`; confirmed `cancelled` with duration is tightly bounded at `1-10` minutes, `no_show` is always `0`, and `completed` spans `5-60` minutes.
- [15:11] Compared distribution shape across groups; found cancelled-with-duration has quartiles `3/6/8` and no values above `10`, while completed has quartiles `18/32/46`, so the cancelled rows do not look like shortened versions of completed consultations.
- [15:12] Chose a working semantic interpretation and metric treatment: treat cancelled-with-duration rows as genuine cancellations with short operational handling time, not as completed or no-show visits and not as doctor utilization minutes.

## Duration summaries

Context: within all `1,385` cancelled rows, `115` have `duration_min = 0` and `1,270` have `duration_min > 0`.

| group | rows | q1 | median | q3 | max | notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `cancelled` with `duration_min > 0` | `1,270` | `3` | `6` | `8` | `10` | Values are nearly uniform across the integers `1-10`; mean `5.57`. |
| `no_show` | `792` | `0` | `0` | `0` | `0` | Uniformly zero duration. |
| `completed` | `7,823` | `18` | `32` | `46` | `60` | Broad spread across `5-60`; mean `32.23`. |

Additional comparison points:

- `cancelled` with duration has no values above `10`, while `completed` extends to `60`.
- Only `11.50%` of completed visits fall in the `5-10` minute range, which is where the upper half of cancelled-with-duration rows sits.
- `61.65%` of cancelled-with-duration rows are `>= 5` minutes, but they still remain far below the completed median of `32`.
- The shape difference from `no_show` is also clean: `no_show` is always `0`, so non-zero cancelled rows behave like a distinct status semantics rather than a relabeled no-show.

## Interpretations considered

1. Started-then-aborted consultation: a clinician may have begun the visit and stopped early, leaving a short but real clinical encounter.
2. Cancellation-handling time: the visit did not complete, but staff or the clinician spent a few minutes in operational work around the cancellation, and that time landed in `duration_min`.

Chosen interpretation: option 2 is more defensible. If these were mostly partial consultations, I would expect at least some tail into completed-like durations, or at minimum values above `10`. Instead the non-zero cancelled durations are tightly capped at `10`, roughly flat across `1-10`, and far shorter than completed visits (`6` median versus `32`). Combined with `no_show` being uniformly `0`, the cleanest reading is that `cancelled` and `no_show` are distinct operational states: `no_show` means nobody engaged enough to log time, while `cancelled` can include a small amount of administrative or aborted-start handling time without meaning the consultation was completed.

## Metric decisions

- No-show rate: exclude cancelled-with-duration rows from the no-show numerator. They remain cancellations, not no-shows.
- Cancellation rate: include all `status = 'cancelled'` rows in the cancellation numerator, including the `1,270` rows with non-zero duration.
- Doctor utilization: exclude cancelled-with-duration `duration_min` from utilization minutes. Treat utilization as completed-consultation time only, not cancellation-handling time.

## Open questions for next session

- Confirm with the data owner whether cancelled `duration_min` is expected to mean cancellation handling / triage / admin time, or whether some rows can reflect a clinically meaningful partial encounter.
- If operations needs a broader workload metric later, decide whether cancelled-with-duration should feed a separate non-utilization bucket such as admin handling minutes rather than being dropped entirely from time-based reporting.
