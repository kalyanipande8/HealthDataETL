import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.simulate_source_systems import generate_pipe_delimited, generate_csv, generate_jsonl
from src.etl_pipeline import standardize_and_merge
from src.quality_checks import run_quality_checks, validate_catch_rate


def test_combined_records_exceed_50000():
    pipe_lines, _ = generate_pipe_delimited()
    csv_rows, _ = generate_csv()
    json_lines, _ = generate_jsonl()
    merged = standardize_and_merge(pipe_lines, csv_rows, json_lines)
    assert len(merged) >= 50000


def test_three_source_formats_present():
    pipe_lines, _ = generate_pipe_delimited()
    csv_rows, _ = generate_csv()
    json_lines, _ = generate_jsonl()
    merged = standardize_and_merge(pipe_lines, csv_rows, json_lines)
    assert set(merged["source_format"].unique()) == {"pipe", "csv", "json"}


def test_quality_checks_catch_most_violations():
    pipe_lines, pipe_v = generate_pipe_delimited()
    csv_rows, csv_v = generate_csv()
    json_lines, json_v = generate_jsonl()
    true_violations = pipe_v | csv_v | json_v
    merged = standardize_and_merge(pipe_lines, csv_rows, json_lines)
    flags = run_quality_checks(merged)
    catch_rate = validate_catch_rate(flags, true_violations, merged)
    assert catch_rate["catch_rate_pct"] >= 95.0


def test_clean_records_mostly_pass_checks():
    pipe_lines, pipe_v = generate_pipe_delimited()
    csv_rows, csv_v = generate_csv()
    json_lines, json_v = generate_jsonl()
    merged = standardize_and_merge(pipe_lines, csv_rows, json_lines)
    flags = run_quality_checks(merged)
    any_flagged = set()
    for s in flags.values():
        any_flagged |= s
    assert len(any_flagged) < len(merged) * 0.15


def test_age_out_of_range_detected():
    pipe_lines, pipe_v = generate_pipe_delimited()
    csv_rows, csv_v = generate_csv()
    json_lines, json_v = generate_jsonl()
    merged = standardize_and_merge(pipe_lines, csv_rows, json_lines)
    flags = run_quality_checks(merged)
    for idx in flags["invalid_age"]:
        age = merged.loc[idx, "age"]
        assert age < 0 or age > 120 or age != age  # includes NaN
