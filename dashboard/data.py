"""Dashboard data loading helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

__all__ = ["TelemediData", "load_all"]


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
