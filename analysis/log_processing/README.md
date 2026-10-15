# Log processing

Code that reads the session logs written by the application (session manifest, `events.jsonl`, per-round summaries) and derives the round-level metrics used in the analysis: execution time, recorded failure events by type, voice events and rejection reasons, reset and integrity checks, and the validity of each round. It also decodes the six-character questionnaire code and checks it against the condition order stored by the application.

The raw logs are not shared (they contain timestamps and device identifiers; see [`docs/data_access.md`](../../docs/data_access.md)), so this code is provided to document how the metrics were computed. The definitions of the resulting variables are in [`docs/data_dictionary.md`](../../docs/data_dictionary.md).

```bash
pip install -r requirements.txt
python offline_experiment_analysis.py --run-dir <session folder> --out-dir <output folder>
python offline_experiment_analysis.py --self-test
```

Trials with `valid_for_analysis = false` are kept in the per-trial output for diagnostics and excluded from the condition aggregates. Runs whose validation report contains red flags are not exported unless `--allow-red-flags` is given.

Some identifiers in this code refer to versions of the log schema (for example `p45f_storage_schema_version`); they are field names of the logs, not study conditions.
