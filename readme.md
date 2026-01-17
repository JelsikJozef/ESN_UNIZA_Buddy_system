# ESN UNIZA Buddy Matching MVP

## Run
```bash
python -m buddy_matching --config config.yml
```
Outputs a timestamped Excel workbook in `outputs/`.

## Input schema (MVP)
- Required columns: `Timestamp`, `Name`, `Surname`, and Erasmus-only `Are you interested in getting a buddy?`
- Identifier column (tie-break): `Timestamp` (falls back to row order if missing/non-unique)
- Question columns: exact headers listed in `config.yml` (`schema.question_columns`)
- Answers: only `A` or `B` are encoded; other/empty values are ignored per question
- Buddy-interest filter applies only to Erasmus rows where the column equals the configured value
