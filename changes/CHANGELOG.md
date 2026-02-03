# Changelog - GUI Fixes

## Version: 2026-02-03

### ✨ New Features

#### Config Import Feature
- **Feature**: YAML configuration file import
- **Capability**: Load saved configuration files (config.yml) into the GUI
- **Key Features**:
  - Upload config.yml via file uploader
  - Automatically populate all configuration settings
  - Support for partial configurations
  - Graceful handling of missing keys
  - Compatible with CLI config.yml format
  - Roundtrip compatible with Config Export
- **Implementation**:
  - New function: `apply_config_to_state()` in `src/view/gui/app.py`
  - Updated config import UI (replaced TODO with working implementation)
- **Testing**: 7 new unit tests (100% pass rate)
- **Documentation**: `changes/CONFIG_IMPORT_FEATURE.md`
- **Benefits**:
  - Quick configuration reuse across sessions
  - Easy sharing of configurations between users
  - Configuration version control support
  - Time-saving for repeated tasks
- **Status**: ✅ Complete and tested

#### Manual Buddy Assignment Feature (MAJOR)
- **Feature**: Manual assignment of Erasmus students to ESN buddies
- **Capability**: ESN coordinators can now manually pair students with buddies through the GUI
- **Key Features**:
  - Assign students directly from ranked results
  - Duplicate prevention (one student = one buddy)
  - Visual status indicators (Available/ASSIGNED)
  - Remove assignments (unassign)
  - View all assignments in one place
  - Export assignments as CSV and Excel
  - Session-based state management
- **Architecture**: 
  - New controller: `src/controller/assignments.py` (assignment state management)
  - New export: `src/view/export_assignments.py` (CSV/XLSX export)
  - Modified: `src/view/gui/app.py` (Results & Export screens)
  - Modified: `src/view/gui/state.py` (assignment state integration)
- **Testing**: 18 new unit tests (100% pass rate)
- **Documentation**:
  - `changes/MANUAL_ASSIGNMENT_FEATURE.md` (technical documentation)
  - `changes/MANUAL_ASSIGNMENT_GUIDE.md` (user guide)
- **Impact**: Enables manual curation of buddy pairs while maintaining automatic ranking as guidance
- **Backward Compatibility**: ✅ No breaking changes, CLI unchanged, ranking algorithm unchanged

---

## Version: 2026-02-02

### 🐛 Bug Fixes

#### 1. Configuration State Persistence (CRITICAL)
- **Issue**: Configuration settings were lost when navigating between pages
- **Root Cause**: Widget `key` parameters created separate state entries disconnected from dataclass state
- **Fix**: Removed unnecessary `key` parameters, ensured widgets read from and write to `ConfigState` dataclass
- **Impact**: All configuration settings now persist correctly across page navigation
- **Files Modified**: 
  - `buddy_matching/gui/app.py` (Configure screen widgets)

#### 2. Timestamp Filter Not Applied (HIGH)
- **Issue**: Timestamp filter was saved in config but not applied to data during pipeline execution
- **Root Cause**: GUI's `run_matching_pipeline()` only applied buddy filter, skipped timestamp filter
- **Fix**: Added timestamp filter application before pipeline execution
- **Impact**: Timestamp filter now correctly filters Erasmus dataset before matching
- **Files Modified**:
  - `buddy_matching/gui/app.py` (Added filter application in `run_matching_pipeline()`)

### ✨ New Features

#### 1. Configuration Summary Panel
- Added collapsible "Current Configuration Summary" at top of Configure screen
- Shows: Question columns count, Required columns count, Top K, Filter statuses
- Purpose: Provides visual confirmation that settings are preserved
- **Files Modified**: `buddy_matching/gui/app.py`

#### 2. Live Preview for Timestamp Filter
- Shows real-time effect of timestamp filter: "Erasmus: X / Y rows after timestamp filter"
- Helps users verify filter before running matching
- Displays warning if date parsing fails
- **Files Modified**: 
  - `buddy_matching/gui/components.py` (Added `show_timestamp_filter_preview()`)
  - `buddy_matching/gui/app.py` (Integrated preview in Configure screen)

#### 3. Enhanced Logging
- Added log message: "Applied timestamp filter: X/Y Erasmus students (>= date)"
- Shows timestamp filter effect in Run screen logs
- **Files Modified**: `buddy_matching/gui/app.py`

### 📚 Documentation

#### New Documentation Files:
- `FIX_STATE_PERSISTENCE.md` - Technical explanation of state persistence fix
- `FIX_TIMESTAMP_FILTER.md` - Technical explanation of timestamp filter fix
- `VERIFICATION_GUIDE.md` - User guide for testing state persistence
- `QUICK_TEST_TIMESTAMP_FILTER.md` - Quick test guide for timestamp filter
- `COMPLETE_FIX_SUMMARY.md` - Comprehensive summary (SK + EN)

#### Updated Documentation:
- `readme.md` - Updated GUI features section, clarified `identifier_column` purpose

#### Test Files:
- `test_state_fix.py` - Automated test for ConfigState persistence
- `test_timestamp_filter.py` - Automated test for timestamp filter logic

### 🔧 Technical Changes

#### State Management:
- Removed widget keys from Configure screen: 
  - All filter widgets (buddy, timestamp)
  - Schema widgets (required columns, identifier, questions)
  - Matching widgets (top_k)
  - Output widgets (per_esner_sheets, include_extra_fields, output_prefix)
- Ensured all widgets use `value=config_state.field` pattern
- Immediate dataclass update after widget interaction

#### Filter Application Order:
```
1. Load data (input_override or from files)
2. Apply timestamp filter (if enabled) ← NEW
3. Apply buddy filter (if enabled)
4. Pass filtered data to pipeline
```

#### Error Handling:
- Added try-catch for timestamp parsing
- Display warnings for invalid timestamps
- Graceful fallback if filter fails

### 🧪 Testing

#### Automated Tests:
```bash
python test_state_fix.py          # ✅ All state persistence tests passed
python test_timestamp_filter.py   # ✅ Timestamp filter works correctly
```

#### Manual Testing:
- Configuration persistence verified across all pages
- Timestamp filter tested with various date formats
- Live previews verified for both filters
- Logs verified for filter application messages

### ⚠️ Breaking Changes
**NONE** - All changes are backward compatible:
- CLI functionality unchanged
- Matching algorithm unchanged
- Export format unchanged
- Config file structure unchanged

### 📊 Impact Summary

| Component | Before | After |
|-----------|--------|-------|
| Config persistence | ❌ Lost on navigation | ✅ Persists correctly |
| Timestamp filter (GUI) | ❌ Not applied | ✅ Applied correctly |
| Live previews | Buddy only | ✅ Buddy + Timestamp |
| Config summary | ❌ None | ✅ Shows current state |
| Logging | Basic | ✅ Detailed filter logs |
| Error handling | Basic | ✅ User-friendly messages |

### 🎯 User-Facing Improvements

1. **Reliable configuration** - Settings no longer disappear unexpectedly
2. **Working timestamp filter** - Can now filter old applications effectively
3. **Visual feedback** - Live previews and summary show current state
4. **Better UX** - Clear logs and error messages guide users
5. **Confidence** - Users can trust the system to preserve their work

### 🔄 Migration Notes

**No migration needed** - Changes are transparent to users:
- Existing `config.yml` files work without modification
- No database schema changes
- No data format changes
- Existing workflows continue working

### 🚀 Deployment

#### Requirements:
- Python 3.9+
- All dependencies in `requirements.txt` (unchanged)

#### Deployment Steps:
```bash
# 1. Pull latest code
git pull

# 2. No new dependencies needed
# pip install -r requirements.txt  # Optional refresh

# 3. Restart Streamlit
streamlit run gui_app.py
```

#### Verification:
```bash
# Run automated tests
python test_state_fix.py
python test_timestamp_filter.py

# Both should output: ✅ Success
```

### 📝 Notes

- **State persistence fix** is critical for user experience - resolves major UX issue
- **Timestamp filter fix** enables semester-based filtering - key functional requirement
- **No performance impact** - Filters run on already-loaded dataframes
- **Memory efficient** - Dataclass state is lightweight
- **Production ready** - Fully tested and documented

### 🙏 Credits

- Issue reported by: User (configuration disappearing, timestamp filter not working)
- Fixed by: GitHub Copilot
- Tested by: Automated tests + manual verification
- Date: 2026-02-02

---

**Status**: ✅ **DEPLOYED TO MAIN** - Ready for production use
