-- Authored-but-not-executed reference: the real Oracle DDL and
-- bulk-load workflow this pipeline would target in production. No
-- Oracle instance is available in this environment, so
-- src/etl_pipeline.py writes to a flat CSV file as the executed
-- mirror of this same standardized-load target, and all measured
-- results in this repo come from that Python/CSV pipeline, not from
-- this script.

CREATE TABLE ehr_standardized (
    patient_id       VARCHAR2(32)  NOT NULL,
    record_key       VARCHAR2(32)  NOT NULL,
    age              NUMBER(3)     CHECK (age BETWEEN 0 AND 120),
    gender           CHAR(1)       CHECK (gender IN ('M', 'F', 'U')),
    dob_year         NUMBER(4),
    diagnosis_code   VARCHAR2(16)  NOT NULL,
    source_format    VARCHAR2(8)   NOT NULL,
    load_timestamp   TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT pk_ehr_standardized PRIMARY KEY (record_key)
);

-- Real Oracle bulk-load pattern: stage each source format's flat
-- file export via SQL*Loader, then validate + merge into the
-- standardized table.
--
-- sqlldr userid=etl_user control=pipe_format.ctl log=pipe_load.log
-- sqlldr userid=etl_user control=csv_format.ctl  log=csv_load.log
-- sqlldr userid=etl_user control=json_format.ctl log=json_load.log
--
-- MERGE INTO ehr_standardized tgt
-- USING staging_ehr src
-- ON (tgt.record_key = src.record_key)
-- WHEN NOT MATCHED THEN INSERT (patient_id, record_key, age, gender,
--     dob_year, diagnosis_code, source_format)
--   VALUES (src.patient_id, src.record_key, src.age, src.gender,
--     src.dob_year, src.diagnosis_code, src.source_format);

-- Pre-load quality check query (the SQL-native equivalent of
-- src/quality_checks.py's rule engine):
SELECT record_key,
       CASE WHEN age NOT BETWEEN 0 AND 120 THEN 'invalid_age' END AS age_flag,
       CASE WHEN gender NOT IN ('M','F','U') THEN 'invalid_gender' END AS gender_flag,
       CASE WHEN patient_id IS NULL OR TRIM(patient_id) = '' THEN 'missing_patient_id' END AS id_flag,
       CASE WHEN diagnosis_code IS NULL THEN 'missing_diagnosis_code' END AS dx_flag
FROM staging_ehr
WHERE age NOT BETWEEN 0 AND 120
   OR gender NOT IN ('M','F','U')
   OR patient_id IS NULL OR TRIM(patient_id) = ''
   OR diagnosis_code IS NULL;
