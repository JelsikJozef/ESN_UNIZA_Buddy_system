# ESN UNIZA Buddy Matching System

This repository implements an **automated buddy matching system** for ESN UNIZA coordinators, providing both **CLI** and **GUI** interfaces.

## What it does
- Loads **Erasmus** and **ESN** datasets from **CSV** or **XLSX**.
- Applies the buddy-interest filter **only to Erasmus**:
  - `Are you interested in getting a buddy? == "Yes"` (value and column name are configurable).
- Uses only the **explicitly configured question columns** from `config.yml` (or selected via GUI).
- Encodes answers using **AB** encoding:
  - valid: `A` or `B`
  - invalid/empty: ignored **for that question only** (NaN-aware matching)
- Computes similarity using **unweighted Hamming distance** (lower is better).
- Produces **ranking-only** results: Top-K Erasmus candidates **per ESN member**.
- Exports a timestamped Excel workbook to `outputs/` (Summary + per-ESN-member sheets).

## Requirements
- Python 3.9+
- Dependencies in `requirements.txt`

## Install
```bash
pip install -r requirements.txt
```

## Run

### Option 1: GUI (Recommended for non-technical users)
```bash
streamlit run gui_app.py
```

The GUI provides:
- **Input**: Upload XLSX or CSV files, preview data, autodetect question columns
- **Configure**: Interactive parameter configuration without editing YAML
  - All settings persist when navigating between pages
  - Configuration summary shows current settings at a glance
  - Live preview shows filter effects in real-time (buddy filter, timestamp filter)
- **Run**: Execute matching with progress tracking
- **Results**: Browse matches interactively by ESN member, view question-by-question comparisons
- **Export**: Download Excel workbook and consolidated CSV
- **Logs**: View run history and debug logs

### Option 2: CLI (For automation and power users)
```bash
python -m buddy_matching --config config.yml

# Optional: print CSV separators tried and column headers during load
python -m buddy_matching --config config.yml --debug-csv

# Or enable debug via env var
set DEBUG_CSV=1
python -m buddy_matching --config config.yml
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
- `identifier_column`: used **only** for deterministic tie-breaking when multiple students have the same distance
  - typically set to `Timestamp` (earlier submissions get priority in ties)
  - if missing or non-unique in Erasmus: falls back to original Erasmus row order
  - ensures reproducible and fair ranking
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
- `Summary` sheet with run statistics
- one sheet per ESN member (when enabled)

Per-ESN-member sheet columns (core fields):
- `Rank`
- `Student Name`
- `Student Surname`
- `Whatsapp contact` (or detected contact column name)
- `Compared questions` - number of questions where both ESN member and student provided valid answers
- `Number of same answers` - count of matching answers (accounts for NaN values)
- `Number of different answers` - count of differing answers (Hamming distance)

Plus all answered, non-question Erasmus fields are appended for context.

## Key Features

### NaN-Aware Matching
The system correctly handles missing or invalid answers:
- Only questions with valid answers from **both** ESN member and student are compared
- `Compared questions` = count of questions where both provided A or B
- `Same answers` = `Compared questions` - `Different answers`
- This ensures accurate similarity metrics even when data quality varies

### GUI Features
- **No YAML editing required**: All configuration through interactive UI
- **Data validation**: Real-time feedback on column health and filter effects
- **Question autodetection**: Automatically identifies likely question columns
- **Interactive results browser**: View matches per ESN member with detailed comparisons
- **Export options**: Excel workbook + consolidated CSV

### CLI Features
- **Automation-friendly**: Script-ready with config files
- **Deterministic**: Same config + data = same results
- **Debug mode**: Detailed logging for troubleshooting

## Project Structure

This project follows a **strict MVC (Model-View-Controller) architecture**:

```
src/
├── model/          # Business logic (ingest, validate, vectorize, match, rank)
├── view/           # Output rendering (Excel export, Streamlit GUI)
└── controller/     # Orchestration (CLI, pipeline)
```

For detailed architecture documentation, see:
- **PROJECT_STRUCTURE.md** - Complete structure guide
- **architecture.md** - MVC specification and business rules

## Testing

Tests use small CSV fixtures from `tests/data/`.

```bash
pytest tests/
```
