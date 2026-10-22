"""Simulate 3 distinct EHR source system export formats (pipe-
delimited HL7-style, CSV, JSON-lines) totaling 51,000+ records, each
with real injected schema violations at a known rate -- the ground
truth an ETL quality-check layer must independently catch before
loading."""
from __future__ import annotations

import json
import numpy as np

N_PER_SOURCE = 17000
SEED = 619

VALID_GENDER_CODES = {"M", "F", "U"}


def _make_records(n: int, rng: np.random.Generator, prefix: str):
    records = []
    true_violations = set()
    for i in range(n):
        rec_id = f"{prefix}-{i:06d}"
        age = int(rng.integers(0, 105))
        gender = rng.choice(["M", "F"])
        dob_year = 2026 - age
        record = {"patient_id": rec_id, "record_key": rec_id, "age": age, "gender": gender,
                  "dob_year": dob_year, "diagnosis_code": f"D{rng.integers(100, 999)}"}

        violation_roll = rng.random()
        if violation_roll < 0.01:
            record["age"] = -5
            true_violations.add(rec_id)
        elif violation_roll < 0.02:
            record["gender"] = "X"
            true_violations.add(rec_id)
        elif violation_roll < 0.025:
            record["patient_id"] = ""
            true_violations.add(rec_id)
        elif violation_roll < 0.03:
            record["diagnosis_code"] = None
            true_violations.add(rec_id)

        records.append(record)
    return records, true_violations


def generate_pipe_delimited(n: int = N_PER_SOURCE, seed: int = SEED):
    rng = np.random.default_rng(seed)
    records, violations = _make_records(n, rng, "PIPE")
    lines = []
    for r in records:
        lines.append("|".join(str(r[k]) if r[k] is not None else "" for k in
                               ["patient_id", "record_key", "age", "gender", "dob_year", "diagnosis_code"]))
    return lines, violations


def generate_csv(n: int = N_PER_SOURCE, seed: int = SEED + 1):
    rng = np.random.default_rng(seed)
    records, violations = _make_records(n, rng, "CSV")
    rows = ["patient_id,record_key,age,gender,dob_year,diagnosis_code"]
    for r in records:
        rows.append(",".join(str(r[k]) if r[k] is not None else "" for k in
                              ["patient_id", "record_key", "age", "gender", "dob_year", "diagnosis_code"]))
    return rows, violations


def generate_jsonl(n: int = N_PER_SOURCE, seed: int = SEED + 2):
    rng = np.random.default_rng(seed)
    records, violations = _make_records(n, rng, "JSON")
    lines = [json.dumps(r) for r in records]
    return lines, violations


if __name__ == "__main__":
    pipe_lines, pipe_v = generate_pipe_delimited()
    csv_lines, csv_v = generate_csv()
    json_lines, json_v = generate_jsonl()
    total = len(pipe_lines) + len(csv_lines) + len(json_lines)
    print("total records:", total, "total violations:", len(pipe_v) + len(csv_v) + len(json_v))
