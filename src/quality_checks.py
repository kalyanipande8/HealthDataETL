"""Real pre-load data-quality validation rules: a flat rule list
interpreted by a small dispatch table, catching schema violations
before the standardized flat file is treated as load-ready."""
from __future__ import annotations

import pandas as pd

VALID_GENDER_CODES = {"M", "F", "U"}


def _range_violation(df: pd.DataFrame, field: str, lo, hi) -> pd.Series:
    return ~df[field].between(lo, hi)


def _missing_violation(df: pd.DataFrame, field: str) -> pd.Series:
    return df[field].isna() | (df[field].astype(str).str.strip() == "")


def _allowed_values_violation(df: pd.DataFrame, field: str, allowed: set) -> pd.Series:
    return ~df[field].isin(allowed)


RULES = [
    {"name": "invalid_age", "check": _range_violation, "params": {"field": "age", "lo": 0, "hi": 120}},
    {"name": "invalid_gender", "check": _allowed_values_violation, "params": {"field": "gender", "allowed": VALID_GENDER_CODES}},
    {"name": "missing_patient_id", "check": _missing_violation, "params": {"field": "patient_id"}},
    {"name": "missing_diagnosis_code", "check": _missing_violation, "params": {"field": "diagnosis_code"}},
]


def run_quality_checks(df: pd.DataFrame) -> dict:
    flags = {}
    for rule in RULES:
        mask = rule["check"](df, **rule["params"])
        flags[rule["name"]] = set(df.index[mask])
    return flags


def validate_catch_rate(flags: dict, true_violation_ids: set, df: pd.DataFrame) -> dict:
    any_flagged = set()
    for s in flags.values():
        any_flagged |= s
    flagged_ids = set(df.loc[list(any_flagged), "record_key"]) if any_flagged else set()

    tp = len(flagged_ids & true_violation_ids)
    recall = round(100 * tp / len(true_violation_ids), 2) if true_violation_ids else 100.0
    return {"n_true_violations": len(true_violation_ids), "n_flagged_ids": len(flagged_ids),
            "n_true_positives": tp, "catch_rate_pct": recall}
