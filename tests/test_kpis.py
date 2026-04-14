from __future__ import annotations

import pandas as pd

from dashboard.kpis import (
    compute_doctor_utilization_minutes,
    compute_satisfaction_by_visit_type,
)


def test_compute_satisfaction_by_visit_type_uses_only_completed_rows() -> None:
    visits = pd.DataFrame(
        {
            "visit_type": ["video", "video", "video", "chat", "chat", "phone"],
            "status": [
                "completed",
                "completed",
                "cancelled",
                "completed",
                "no_show",
                "completed",
            ],
            "satisfaction_score": [4.0, 2.0, None, 5.0, None, 3.0],
        }
    )

    result = compute_satisfaction_by_visit_type(visits)

    assert result.to_dict(orient="records") == [
        {
            "visit_type": "chat",
            "avg_satisfaction": 5.0,
            "completed_visit_count": 1,
        },
        {
            "visit_type": "phone",
            "avg_satisfaction": 3.0,
            "completed_visit_count": 1,
        },
        {
            "visit_type": "video",
            "avg_satisfaction": 3.0,
            "completed_visit_count": 2,
        },
    ]


def test_compute_doctor_utilization_minutes_sums_only_completed_visits() -> None:
    visits = pd.DataFrame(
        {
            "doctor_id": [101, 101, 102, 102, 103, 104],
            "status": [
                "completed",
                "cancelled",
                "completed",
                "no_show",
                "cancelled",
                "completed",
            ],
            "duration_min": [30, 45, 20, 0, 10, 50],
        }
    )
    doctors = pd.DataFrame(
        {
            "doctor_id": [101, 102, 103, 104, 105],
            "specialization": [
                "Dermatology",
                "Cardiology",
                "General Medicine",
                "Pediatrics",
                "Neurology",
            ],
        }
    )

    result = compute_doctor_utilization_minutes(visits, doctors)

    assert result.to_dict(orient="records") == [
        {
            "doctor_id": 104,
            "specialization": "Pediatrics",
            "utilization_minutes": 50,
        },
        {
            "doctor_id": 101,
            "specialization": "Dermatology",
            "utilization_minutes": 30,
        },
        {
            "doctor_id": 102,
            "specialization": "Cardiology",
            "utilization_minutes": 20,
        },
    ]
