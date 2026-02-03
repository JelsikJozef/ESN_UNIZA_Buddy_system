# Manual Assignment Feature - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ESN UNIZA Buddy System                          │
│                     Manual Assignment Feature (NEW)                      │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                                MODEL LAYER                                │
│                           (UNCHANGED - NO IMPACT)                         │
├──────────────────────────────────────────────────────────────────────────┤
│  • src/model/ingest.py       - Data loading                              │
│  • src/model/validate.py     - Validation                                │
│  • src/model/vectorize.py    - Vectorization                             │
│  • src/model/match.py         - Matching logic                           │
│  • src/model/rank.py          - Ranking algorithm                        │
└──────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                            CONTROLLER LAYER                               │
├──────────────────────────────────────────────────────────────────────────┤
│  EXISTING:                                                                │
│  • src/controller/pipeline.py      - Pipeline orchestration              │
│  • src/controller/cli.py           - CLI interface                       │
│                                                                           │
│  NEW: ⭐                                                                  │
│  • src/controller/assignments.py   - Assignment state management         │
│    ├─ Assignment (dataclass)       - Single assignment                   │
│    └─ AssignmentState (dataclass)  - Collection + logic                  │
│       ├─ add_assignment()          - Create assignment                   │
│       ├─ remove_assignment()       - Delete assignment                   │
│       ├─ is_erasmus_assigned()     - Check status                        │
│       └─ get_assigned_indices()    - Get all assigned                    │
└──────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                              VIEW LAYER                                   │
├──────────────────────────────────────────────────────────────────────────┤
│  EXISTING:                                                                │
│  • src/view/export_xlsx.py         - Ranking export                      │
│                                                                           │
│  NEW: ⭐                                                                  │
│  • src/view/export_assignments.py  - Assignment export                   │
│    ├─ export_assignments_to_csv()  - CSV export                          │
│    ├─ export_assignments_to_xlsx() - Excel export                        │
│    └─ generate_assignment_filename() - Filename generation               │
└──────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                           STREAMLIT GUI LAYER                             │
├──────────────────────────────────────────────────────────────────────────┤
│  MODIFIED: ⭐                                                             │
│  • src/view/gui/state.py                                                 │
│    └─ Added: AssignmentState to session_state                            │
│                                                                           │
│  • src/view/gui/app.py                                                   │
│    ├─ show_results_screen() - MODIFIED                                   │
│    │  ├─ Summary metrics (added assignment count)                        │
│    │  ├─ Ranked table (added Status column)                              │
│    │  ├─ NEW: Manual Assignment section                                  │
│    │  └─ NEW: Current Assignments overview                               │
│    │                                                                      │
│    └─ show_export_screen() - MODIFIED                                    │
│       └─ NEW: Export Assigned Buddies section                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
USER ASSIGNS STUDENT
        ↓
┌───────────────────────────────────┐
│   Streamlit UI (Results Screen)   │
│   • User selects ESN member       │
│   • User selects Erasmus student  │
│   • User clicks "Assign" button   │
└───────────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│   Session State (state.py)        │
│   assignment_state = get_...()    │
└───────────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│   Controller (assignments.py)     │
│   assignment_state.add_assignment()│
│   • Validate (no duplicate)       │
│   • Create Assignment object      │
│   • Add timestamp                 │
│   • Store in state.assignments    │
└───────────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│   UI Feedback                     │
│   • st.success() or st.error()    │
│   • st.rerun() - Refresh UI       │
└───────────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│   Updated Display                 │
│   • Student marked "ASSIGNED"     │
│   • Count updated                 │
│   • Available students filtered   │
└───────────────────────────────────┘
```

---

## Export Flow Diagram

```
USER EXPORTS ASSIGNMENTS
        ↓
┌───────────────────────────────────┐
│   Streamlit UI (Export Screen)    │
│   • User clicks CSV or XLSX       │
└───────────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│   Get Assignment Data             │
│   assignment_state.assignments    │
│   → List[Assignment]              │
└───────────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│   View Layer (export_assignments) │
│   export_assignments_to_csv()     │
│   OR                              │
│   export_assignments_to_xlsx()    │
│   • Convert to DataFrame          │
│   • Format columns                │
│   • Generate file                 │
└───────────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│   Download to User                │
│   st.download_button()            │
│   • Timestamped filename          │
│   • CSV or XLSX format            │
└───────────────────────────────────┘
```

---

## Component Interaction Map

```
┌─────────────────────────────────────────────────────────────────┐
│                       Streamlit Session State                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ st.session_state                                            │ │
│  │  ├─ input: InputState                                       │ │
│  │  ├─ config: ConfigState                                     │ │
│  │  ├─ results: ResultsState                                   │ │
│  │  │   └─ artifacts: PipelineArtifacts (rankings)             │ │
│  │  │                                                           │ │
│  │  └─ assignments: AssignmentState ⭐ NEW                     │ │
│  │      └─ assignments: List[Assignment]                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↑  ↓
            ┌─────────────────┴──┴─────────────────┐
            │                                       │
    ┌───────┴────────┐                    ┌────────┴────────┐
    │  Results Screen │                    │  Export Screen  │
    │  • View rankings│                    │  • Export ranks │
    │  • Assign ⭐    │                    │  • Export CSV   │
    │  • Unassign ⭐  │                    │  • Export XLSX ⭐│
    └────────────────┘                    └─────────────────┘
```

---

## Separation of Concerns

```
┌─────────────────────────────────────────────────────────┐
│              RANKING SYSTEM (Existing)                   │
│  • Runs independently                                    │
│  • Produces rankings for all ESN members                 │
│  • NOT affected by assignments                           │
│  • Remains reproducible                                  │
└─────────────────────────────────────────────────────────┘
                         ↓
                    Rankings exist
                         ↓
┌─────────────────────────────────────────────────────────┐
│           ASSIGNMENT SYSTEM (New) ⭐                     │
│  • Uses rankings as input/guidance                       │
│  • Allows manual override                                │
│  • Tracks which students are taken                       │
│  • Exports final buddy pairs                             │
│  • DOES NOT modify rankings                              │
└─────────────────────────────────────────────────────────┘
                         ↓
                  Two separate outputs:
                         ↓
        ┌────────────────┴────────────────┐
        ↓                                  ↓
┌──────────────────┐            ┌──────────────────┐
│ Ranking Export   │            │ Assignment Export│
│ (Existing)       │            │ (New) ⭐         │
│ • All rankings   │            │ • Assigned pairs │
│ • All candidates │            │ • Timestamps     │
│ • Per ESN member │            │ • Final list     │
└──────────────────┘            └──────────────────┘
```

---

## State Lifecycle

```
SESSION START
    ↓
Initialize session_state
    ├─ input = InputState()
    ├─ config = ConfigState()
    ├─ results = ResultsState()
    └─ assignments = AssignmentState() ⭐ NEW
    ↓
USER LOADS DATA
    ↓
USER RUNS PIPELINE
    ↓
results.artifacts = PipelineArtifacts
    (contains rankings)
    ↓
USER VIEWS RESULTS
    ↓
USER MAKES ASSIGNMENTS ⭐
    ├─ assignments.add_assignment()
    ├─ assignments.add_assignment()
    └─ assignments.add_assignment()
    ↓
USER EXPORTS ASSIGNMENTS ⭐
    └─ CSV/XLSX downloaded
    ↓
SESSION ENDS
    (assignments lost unless exported)
```

---

## Error Prevention Flow

```
USER ATTEMPTS ASSIGNMENT
        ↓
    Validate Input
        ↓
┌───────────────────────────────┐
│ Is student already assigned?  │
└───────────────────────────────┘
        ↓               ↓
       YES             NO
        ↓               ↓
   ┌────────┐      ┌────────────┐
   │ REJECT │      │  ACCEPT    │
   │ Show   │      │  Create    │
   │ Error  │      │  Assignment│
   └────────┘      └────────────┘
                         ↓
                   Update State
                         ↓
                   Refresh UI
                         ↓
                   Show Success
```

---

## UI Component Tree

```
Results Screen
├─ Summary Metrics
│  ├─ ESN Members
│  ├─ Erasmus Students
│  ├─ Questions
│  ├─ Top K
│  └─ Assignments ⭐ NEW
│
├─ ESN Member Selection
│  └─ Dropdown (select member)
│
├─ Ranked Matches Table
│  ├─ Rank
│  ├─ Name
│  ├─ Surname
│  ├─ Status ⭐ NEW (Available/ASSIGNED)
│  ├─ Contact
│  ├─ Compared Questions
│  └─ Same/Different Answers
│
├─ Manual Assignment Section ⭐ NEW
│  ├─ Student Selector (available only)
│  └─ "Assign" Button
│     └─ Success/Error Message
│
├─ Match Details
│  └─ Question-by-question comparison
│
└─ Current Assignments Overview ⭐ NEW
   ├─ Assignments Table
   │  ├─ ESN Name/Surname
   │  ├─ Erasmus Name/Surname
   │  └─ Timestamp
   └─ Remove Assignment
      ├─ Assignment Selector
      └─ "Remove" Button

Export Screen
├─ Download Excel Workbook (existing)
├─ Download Consolidated CSV (existing)
└─ Export Assigned Buddies ⭐ NEW
   ├─ Download CSV
   └─ Download XLSX
```

---

## File Dependency Graph

```
gui_app.py (entry point)
    ↓
src/view/gui/app.py
    ↓
    ├─→ src/view/gui/state.py
    │       ↓
    │       ├─→ src/controller/pipeline.py (existing)
    │       └─→ src/controller/assignments.py ⭐ NEW
    │
    ├─→ src/view/gui/components.py (existing)
    │
    ├─→ src/controller/pipeline.py (existing)
    │       ↓
    │       └─→ src/model/* (all model files)
    │
    └─→ src/view/export_assignments.py ⭐ NEW
            ↓
            └─→ src/controller/assignments.py ⭐ NEW
```

---

## Test Coverage Map

```
src/controller/assignments.py
    ↓
tests/test_assignments.py (11 tests) ✅
    ├─ test_create_assignment
    ├─ test_add_assignment
    ├─ test_add_duplicate_erasmus_fails
    ├─ test_is_erasmus_assigned
    ├─ test_get_assigned_indices
    ├─ test_remove_assignment
    ├─ test_remove_nonexistent_assignment
    ├─ test_get_assignments_for_esn
    ├─ test_clear_all
    └─ test_multiple_esn_can_be_in_state

src/view/export_assignments.py
    ↓
tests/test_export_assignments.py (7 tests) ✅
    ├─ test_export_empty_assignments_csv
    ├─ test_export_assignments_csv
    ├─ test_export_assignments_xlsx
    ├─ test_export_empty_assignments_xlsx
    ├─ test_generate_assignment_filename
    ├─ test_csv_export_with_state
    └─ test_xlsx_export_with_multiple_assignments
```

---

**Last Updated**: 2026-02-03  
**Feature Status**: ✅ Complete and tested
