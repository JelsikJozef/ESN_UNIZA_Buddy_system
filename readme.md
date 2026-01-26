# ESN UNIZA Buddy Matching System — MVP

This repository implements the **First MVP** described in `architecture.md`.

## What it does (MVP)
- Loads **Erasmus** and **ESN** datasets from **CSV** or **XLSX**.
- Applies the buddy-interest filter **only to Erasmus**:
  - `Are you interested in getting a buddy? == "Yes"` (value and column name are configurable).
- Uses only the **explicitly configured question columns** from `config.yml`.
- Encodes answers using **AB** encoding:
  - valid: `A` or `B`
  - invalid/empty: ignored **for that question only**
- Computes similarity using **unweighted Hamming distance** (lower is better).
- Produces **ranking-only** results: Top-K Erasmus candidates **per ESN member**.
- Exports a timestamped Excel workbook to `outputs/` (Summary + per-ESN-member sheets).

## Requirements
- Python 3.x
- Dependencies in `requirements.txt`

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
python -m buddy_matching --config config.yml

# Optional: print CSV separators tried and column headers during load
python -m buddy_matching --config config.yml --debug-csv

# Or enable debug via env var
set DEBUG_CSV=1 & python -m buddy_matching --config config.yml
```
The CLI prints the generated Excel path and writes the workbook into the configured `output.out_dir`.

## Configuration (`config.yml`)
All behavior is driven by `config.yml`.

### `input`
- `format`: `csv` or `xlsx`
- `file_path`:
  - for `csv`: directory containing both CSV files
  - for `xlsx`: path to the workbook
- CSV mode only:
  - `erasmus_csv`: filename for Erasmus CSV
  - `esn_csv`: filename for ESN CSV
  - `csv_separator`: optional single-character delimiter override (defaults to auto-detecting `;` then `,`)
  - `timestamp_min`: optional ISO/date string; removes Erasmus rows with timestamp earlier than this value
  - `timestamp_column`: override for the timestamp column header (defaults to `schema.identifier_column` or `Timestamp`)
  - `timestamp_format`: optional `datetime.strptime` pattern for parsing both `timestamp_min` and the column values (e.g. `%m/%d/%Y %H:%M:%S`)
- XLSX mode only:
  - `erasmus_sheet`: sheet name for Erasmus
  - `esn_sheet`: sheet name for ESN
- Erasmus-only filter:
  - `buddy_interest_column`: exact Erasmus header string
  - `buddy_interest_value`: accepted value (e.g. `"Yes"`)

### `schema`
- `required_columns`: required metadata columns in **both** datasets (e.g. `Timestamp`, `Name`, `Surname`)
- `identifier_column`: used **only** for deterministic tie-breaking
  - if missing or non-unique in Erasmus: falls back to original Erasmus row order
- `question_columns`: list of **exact** header strings (including newlines/emojis)
  - validation fails if any is missing from either dataset
- `answer_encoding`: must be `AB`

### `matching`
- `metric`: must be `hamming`
- `top_k`: integer (Top-K Erasmus candidates per ESN member)

### `output`
- `out_dir`: output directory (default: `outputs`)
- `per_esner_sheets`: if `true`, generates one sheet per ESN member

## Input schema expectations
### Erasmus dataset
Must contain:
- all `schema.required_columns`
- `input.buddy_interest_column`
- all `schema.question_columns`

### ESN dataset
Must contain:
- all `schema.required_columns`
- all `schema.question_columns`

## Output
The exported workbook contains:
- `Summary` sheet
- one sheet per ESN member (when enabled)

Per-ESN-member sheet columns (core fields):
- `Rank`
- `Student Name`
- `Student Surname`
- `Whatsapp contact` (or detected Whatsapp column name)
- `Number of same answers`
- `Number of different answers`
Plus all answered, non-question Erasmus fields are appended for context.

## Testing
Tests use small CSV fixtures from `tests/data/`.

```bash
pytest
```
