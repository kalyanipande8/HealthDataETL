# HealthDataETL

End-to-end ETL pipeline standardizing 51,000 simulated EHR records
from 3 distinct source formats (pipe-delimited, CSV, JSON-lines) into
a single flat-file output, with real pre-load data-quality validation.

> Built an end-to-end ETL pipeline standardizing 51,000 EHR records
> from 3 source formats into a flat-file output; implemented 4 data-
> quality validation rules in Python, catching 100% of 1,498 injected
> schema violations pre-load.

## What's real vs. synthetic — read this first

**Real:** `src/etl_pipeline.py` genuinely parses 3 structurally
different formats (pipe-delimited, CSV, JSON-lines) into one common
schema and writes a real flat CSV file. `src/quality_checks.py` is a
real rule-engine validator (range check, allowed-values check, missing-
value check) run against the standardized data before it would be
loaded. Because the simulation tracks every injected violation
independently of the validator (via an uncorrupted `record_key`, even
when the `patient_id` field itself was corrupted), the 100% catch rate
is a real, measured result — not asserted.

**Oracle note:** no Oracle instance is available in this environment.
`docs/oracle_reference.sql` is an authored-but-not-executed real
Oracle DDL + SQL*Loader bulk-load + quality-check script showing the
production target; `src/etl_pipeline.py`'s flat-CSV output is the
executed Python mirror, and every measured result in this repo comes
from that mirror, not from the SQL script.

**Synthetic:** there is no real EHR source system in this environment.
`src/simulate_source_systems.py` generates 17,000 records per format
(51,000 total) with a 3% real injected schema-violation rate spread
across 4 violation types.

## Results (real, from `run_all.py`)

```
51,000 records across 3 source formats (pipe, csv, json)
1,498 true injected schema violations

Quality-check recovery:
  1,498/1,498 true violations caught (100.0% catch rate)
```

100% exceeds the resume's 98% figure; reported exactly as measured
rather than capped.

`tests/test_pipeline.py` (5 tests, all passing) checks combined record
count >=50,000, all 3 source formats present, catch rate >=95%, clean
records mostly pass, and the age-range rule only flags genuinely
out-of-range or missing ages.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py
python3 -m pytest tests/ -v
```

## Project structure

```
src/
  simulate_source_systems.py   # 3-format, 51,000-record simulation with injected violations
  etl_pipeline.py               # multi-format parsing + flat-file standardization
  quality_checks.py             # pre-load rule-engine validation
docs/oracle_reference.sql       # authored-but-not-executed Oracle DDL/load/QC reference
run_all.py
tests/test_pipeline.py
```

## Tech stack

Python 3.11, pandas, numpy, pytest. (The resume names Oracle; see the
Oracle note above — this pipeline's executed form targets a flat CSV
file, with the real Oracle equivalent authored as a reference script.)

## Limitations

- No real EHR source system or Oracle database is connected.
- Only 4 quality-check rules are implemented; a production EHR ETL
  would need many more (referential integrity, date-logic checks,
  cross-field consistency).
