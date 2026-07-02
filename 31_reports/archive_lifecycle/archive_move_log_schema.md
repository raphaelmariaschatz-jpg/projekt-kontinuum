# Archive Move Log Schema

Every future archive move must append a JSON object with these fields:

- `timestamp_utc`
- `original_path`
- `archive_path`
- `reason`
- `safety_check`
- `references_before`
- `references_updated`
- `verification_after_move`

The log file is `31_reports/archive_lifecycle/archive_moves.jsonl`.
