import json
import os

from src.simulate_source_systems import generate_pipe_delimited, generate_csv, generate_jsonl
from src.etl_pipeline import standardize_and_merge, write_flat_file
from src.quality_checks import run_quality_checks, validate_catch_rate


def main():
    pipe_lines, pipe_v = generate_pipe_delimited()
    csv_rows, csv_v = generate_csv()
    json_lines, json_v = generate_jsonl()
    true_violations = pipe_v | csv_v | json_v

    merged = standardize_and_merge(pipe_lines, csv_rows, json_lines)

    os.makedirs("results", exist_ok=True)
    write_flat_file(merged, "results/standardized_ehr_flat_file.csv")

    flags = run_quality_checks(merged)
    catch_rate = validate_catch_rate(flags, true_violations, merged)

    summary = {"n_records": len(merged), "n_sources": merged["source_format"].nunique(),
               "n_true_violations": len(true_violations), "quality_check_recovery": catch_rate}

    with open("results/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
