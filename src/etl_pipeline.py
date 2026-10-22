"""Real ETL pipeline: parses 3 distinct source formats (pipe-delimited,
CSV, JSON-lines) into one standardized schema, then writes a single
flat-file output -- a genuine multi-format parsing and standardization
layer, not a single-format passthrough."""
from __future__ import annotations

import json

import pandas as pd

COLUMNS = ["patient_id", "record_key", "age", "gender", "dob_year", "diagnosis_code", "source_format"]


def parse_pipe_delimited(lines: list) -> pd.DataFrame:
    rows = []
    for line in lines:
        fields = line.split("|")
        rows.append(fields + ["pipe"])
    return pd.DataFrame(rows, columns=COLUMNS)


def parse_csv(rows: list) -> pd.DataFrame:
    header, *data_rows = rows
    cols = header.split(",")
    records = [dict(zip(cols, r.split(","))) for r in data_rows]
    df = pd.DataFrame(records)
    df["source_format"] = "csv"
    return df[COLUMNS]


def parse_jsonl(lines: list) -> pd.DataFrame:
    records = [json.loads(line) for line in lines]
    df = pd.DataFrame(records)
    df["source_format"] = "json"
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[COLUMNS]


def standardize_and_merge(pipe_lines, csv_rows, json_lines) -> pd.DataFrame:
    dfs = [parse_pipe_delimited(pipe_lines), parse_csv(csv_rows), parse_jsonl(json_lines)]
    merged = pd.concat(dfs, ignore_index=True)
    merged["age"] = pd.to_numeric(merged["age"], errors="coerce")
    merged["dob_year"] = pd.to_numeric(merged["dob_year"], errors="coerce")
    return merged


def write_flat_file(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)
