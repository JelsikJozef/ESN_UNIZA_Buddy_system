# Architecture (MVC) — ESN UNIZA Buddy Matching System

## 1. Purpose

This application matches incoming Erasmus students with ESN members (buddies) based on a shared binary questionnaire exported from Google Forms to CSV/Excel.

The system:
- Loads two datasets: **Erasmus students** and **ESN members**.
- Filters **only Erasmus students** to include those who answered  
  **"Are you interested in getting a buddy?" = "Yes"**.
- Uses only the **common A/B questionnaire questions** present in both datasets.
- Validates schema and answers.
- Vectorizes answers into fixed-length binary vectors.
- Computes similarity using **unweighted Hamming distance**.
- Produces ranking tables: **for each ESN member, a Top-K list of most similar Erasmus students**.
- Exports results into an Excel workbook (Summary + per-ESN-member sheets).

---

## 2. Key Business Rules

### BR1 — Buddy interest filter (mandatory, Erasmus only)
- The buddy-interest filter is applied **only to the Erasmus dataset**.
- The ESN dataset does **not** contain this column and is **never filtered**.
- Only Erasmus rows where:
- Are you interested in getting a buddy? == "Yes"
- are included in matching.
- Filtering happens **before** vectorization and matching.

### BR2 — Equal weights
- All questionnaire questions have equal importance.
- Similarity metric: **unweighted Hamming distance**.
- Lower distance = more similar.

### BR3 — Ranking-only output
- The system outputs **ranked candidate lists (Top-K)**.
- No capacity constraints.
- No final assignment algorithm.

---

## 3. MVC Overview

The project follows the **Model–View–Controller (MVC)** pattern.

Responsibilities are strictly separated to ensure:
- determinism,
- testability,
- clarity of responsibilities,
- easy future extension.

### 3.1 Model (Domain + Data Processing)
Responsible for:
- Data ingestion
- Filtering
- Validation
- Vectorization
- Similarity computation
- Ranking preparation

The Model must **not**:
- write output files,
- print user-facing messages (except through raised errors),
- handle CLI arguments.

### 3.2 View (Output Rendering)
Responsible for:
- Transforming matching results into a human-readable format
- Exporting Excel workbooks
- Ensuring deterministic and consistent output formatting

The View must **not**:
- perform matching logic,
- validate input data,
- apply buddy-interest filtering.

### 3.3 Controller (Orchestration + CLI)
Responsible for:
- Loading configuration
- Orchestrating the pipeline in the correct order
- Handling errors and user feedback
- Managing file paths and timestamped outputs
- Providing a stable CLI interface

The Controller must **not**:
- contain business logic,
- implement matching or export logic.

---

## 4. Components and Responsibilities (MVC Mapping)

### 4.1 Model Layer Modules

#### 4.1.1 `model/ingest`
Responsibilities:
- Load Erasmus and ESN datasets from CSV/XLSX.
- Preserve original column names exactly as in the files.
- Preserve original row order.
- Apply buddy-interest filtering **only to the Erasmus dataset**.

Inputs:
- Input file path(s)
- Erasmus sheet name (if XLSX)
- ESN sheet name (if XLSX)
- Buddy-interest column name
- Buddy-interest accepted value

Outputs:
- `erasmus_table`
- `esn_table`

#### 4.1.2 `model/validate`
Responsibilities:
- Verify required metadata columns exist.
- Verify the identifier column exists.
- Verify that **all configured question columns exist in both datasets**.
- Validate answer values in question columns.

Validation rules:
- Valid answer: `"A"` or `"B"`
- Invalid answer: any other value or empty

Invalid answers:
- Do **not** invalidate the entire row.
- Are handled later by ignoring the answer for that question only.

Validation failures (hard stop):
- Missing required columns
- Missing identifier column
- Missing question columns

#### 4.1.3 `model/vectorize`
Responsibilities:
- Convert questionnaire answers into binary vectors.
- Use **exact question column order defined in configuration**.
- Handle invalid answers by excluding that question from comparison for that participant only.

Outputs:
- `erasmus_vectors`
- `esn_vectors`
- Metadata mapping (identifier, name, surname)

#### 4.1.4 `model/match`
Responsibilities:
- Compute **unweighted Hamming distance** between ESN members and Erasmus students.

Distance definition:
- Distance = number of differing answers
- Questions are ignored if **at least one side has an invalid answer**

Outputs:
- Distance lists per ESN member

#### 4.1.5 `model/rank`
Responsibilities:
- For each ESN member:
- sort Erasmus students by ascending distance
- apply deterministic tie-breaking

Tie-breaking rules:
- Primary: configured identifier column
- Fallback: original row order from the Erasmus dataset

Outputs:
- Ranked Top-K match lists per ESN member

---

## 4.2 View Layer Modules

#### 4.2.1 `view/export_xlsx`
Responsibilities:
- Create output workbook in the configured output directory.
- Generate the following sheets:

**Summary sheet**
- Run timestamp
- Number of ESN members
- Number of Erasmus students after filtering
- Number of questionnaire questions
- Matching metric used

**Per-ESN-member sheets**
- One sheet per ESN member
- Columns:
- Rank
- Student Name
- Student Surname
- Distance (Hamming)

Additional constraints:
- Enforce Excel-safe sheet names
- Stable column order
- Deterministic output

---

## 4.3 Controller Layer Modules

#### 4.3.1 `controller/cli`
Responsibilities:
- Provide CLI entrypoint, e.g.:
- python -m buddy_matching --config config.yml
- - Load and validate configuration structure.
- Execute the pipeline in strict order:
1. ingest
2. validate
3. vectorize
4. match
5. rank
6. export
- Convert raised errors into concise, user-friendly CLI messages.

Outputs:
- Exit status
- Printed path to generated output file

---

## 5. Data Schema Expectations

### 5.1 Required metadata columns

**Erasmus dataset**
- `Timestamp`
- `Name`
- `Surname`
- `Are you interested in getting a buddy?`

**ESN dataset**
- `Timestamp`
- `Name`
- `Surname`

### 5.2 Questionnaire columns
- Questionnaire questions are identified by **exact column header strings from the CSV/XLSX files**.
- These column names (including line breaks and emojis) are explicitly listed in:
- schema.question_columns
- - Both datasets must contain **all configured question columns**.
- No auto-detection of question columns is allowed.

### 5.3 Answer encoding
Supported:
- `AB`: values `"A"` or `"B"`

If a particular answer is:
- empty, or
- not `"A"` or `"B"`,

then:
- that answer is considered invalid,
- the corresponding question is ignored **for that participant only**,
- it does not count as a match or a mismatch.

### 5.4 Identifier column
- A single identifier column is defined in configuration (e.g. `Timestamp`).
- The identifier is used **only** for deterministic tie-breaking.
- It must not influence similarity computation.

---

## 6. Output Requirements

### 6.1 Workbook structure
- One Excel file per run
- `Summary` sheet (always)
- One sheet per ESN member (default behavior)

### 6.2 Per-ESN-member sheet content
- Sorted by ascending distance
- Rank 1 = best match (lowest distance)
- Minimum columns:
- Rank
- Student Name
- Student Surname
- Distance (Hamming)

---

## 7. Testing Requirements

All critical Model and View logic must be covered by automated tests using `pytest`.

Tests must use **small CSV fixtures** stored in `tests/data/`.

Minimum required test coverage:
- Ingest: Erasmus buddy-interest filtering
- Validate: missing required columns
- Vectorize: stable question order, invalid answer handling
- Match: correct unweighted Hamming distance
- Rank: correct Top-K ordering and deterministic tie-breaking
- View: Excel file creation and required sheets

Tests must **not** depend on real production files.


