# Timestamp Filter Fix - Documentation

## Problem Fixed
Timestamp filter was being saved in configuration but **not applied** to the data during pipeline execution in the GUI.

## Root Cause
The GUI's `run_matching_pipeline()` function was only applying the buddy filter, but skipping the timestamp filter completely. The timestamp filter logic existed in `src/model/ingest.py` for CLI mode, but was not being called in GUI mode.

## Solution Applied

### 1. Added Timestamp Filter Application in GUI
**File**: `buddy_matching/gui/app.py`

Added timestamp filter application in `run_matching_pipeline()` function:
```python
# Apply timestamp filter if enabled
if config_state.timestamp_filter_enabled and config_state.timestamp_filter_column and config_state.timestamp_filter_min:
    original_count = len(erasmus_df)
    try:
        # Parse the cutoff timestamp
        cutoff = pd.to_datetime(
            config_state.timestamp_filter_min,
            format=config_state.timestamp_filter_format if config_state.timestamp_filter_format else None,
            errors='raise'
        )
        
        # Parse the timestamp column
        timestamp_series = pd.to_datetime(
            erasmus_df[config_state.timestamp_filter_column],
            format=config_state.timestamp_filter_format if config_state.timestamp_filter_format else None,
            errors='coerce'
        )
        
        # Apply filter
        erasmus_df = erasmus_df[timestamp_series >= cutoff].copy().reset_index(drop=True)
        filtered_count = len(erasmus_df)
        
        state.log_message(
            f"Applied timestamp filter: {filtered_count}/{original_count} Erasmus students (>= {config_state.timestamp_filter_min})",
            "INFO"
        )
    except Exception as e:
        state.log_message(f"Warning: Failed to apply timestamp filter: {str(e)}", "WARNING")
        st.warning(f"Failed to apply timestamp filter: {str(e)}")
```

### 2. Added Live Preview for Timestamp Filter
**File**: `buddy_matching/gui/components.py`

Added new function `show_timestamp_filter_preview()` to show real-time effect of timestamp filter:
```python
def show_timestamp_filter_preview(
    df: pd.DataFrame,
    column: str,
    min_timestamp: str,
    timestamp_format: str,
    label: str
) -> Tuple[int, int]:
    """Show the effect of a timestamp filter on a dataframe."""
```

This function displays: `"Erasmus: X / Y rows after timestamp filter (>= date)"`

### 3. Integrated Live Preview in Configure Screen
**File**: `buddy_matching/gui/app.py`

Added live preview call in the timestamp filter section of Configure screen:
```python
# Live preview
if timestamp_col and timestamp_min:
    components.show_timestamp_filter_preview(
        erasmus_df, 
        timestamp_col, 
        timestamp_min, 
        timestamp_format,
        "Erasmus"
    )
```

## How It Works Now

### Execution Order (GUI):
1. **Load data** (Input screen)
2. **Configure filters** (Configure screen)
   - Enable timestamp filter
   - Select timestamp column
   - Enter minimum timestamp (e.g., "1/22/2026 14:10:12")
   - Optional: specify format (e.g., "%m/%d/%Y %H:%M:%S")
   - **Live preview shows effect immediately**
3. **Run pipeline** (Run screen)
   - First applies **timestamp filter** (if enabled)
   - Then applies **buddy filter** (if enabled)
   - Proceeds with matching on filtered data

### Filter Application Rules:
- **Timestamp filter applies to**: Erasmus dataset only
- **Filter condition**: `timestamp >= minimum_timestamp`
- **Date parsing**: Uses pandas `to_datetime()` with optional format string
- **Invalid dates**: Rows with unparseable dates are excluded (coerce to NaT)
- **Missing column**: Shows error and skips filter

### Error Handling:
- Invalid timestamp format → Shows warning, skips filter
- Missing timestamp column → Shows warning, skips filter
- Parse errors are logged and displayed to user

## Testing

### Automated Test:
```bash
python test_timestamp_filter.py
```
Expected output: `✅ Timestamp filter works correctly!`

### Manual Test in GUI:
1. **Start GUI**: `streamlit run gui_app.py`
2. **Load data** with timestamp column (e.g., "Timestamp")
3. **Go to Configure screen**
4. **Expand "Timestamp Filter (optional)"**
5. **Enable timestamp filter** checkbox
6. **Select timestamp column**
7. **Enter minimum timestamp**: `1/22/2026 14:10:12`
8. **Enter format**: `%m/%d/%Y %H:%M:%S`
9. **Check live preview**: Should show "Erasmus: X / Y rows after timestamp filter"
10. **Navigate to Run screen**
11. **Click "Run Matching"**
12. **Check logs**: Should see "Applied timestamp filter: X/Y Erasmus students (>= ...)"
13. **Go to Results screen**
14. **Verify**: Only students with timestamp >= cutoff are included

### Example:
If you have 100 Erasmus students with timestamps ranging from 1/20/2026 to 1/25/2026, and you set minimum timestamp to `1/22/2026 14:10:12`:
- Live preview might show: "Erasmus: 60 / 100 rows after timestamp filter"
- After running, logs show: "Applied timestamp filter: 60/100 Erasmus students (>= 1/22/2026 14:10:12)"
- Results will only include those 60 students

## CLI Behavior
**No changes needed** - CLI already had timestamp filter working correctly via `ingest.load_tables()`.

## Configuration
Timestamp filter settings are stored in `ConfigState`:
```python
timestamp_filter_enabled: bool = False
timestamp_filter_column: Optional[str] = None
timestamp_filter_min: str = ""
timestamp_filter_format: str = ""
```

And exported to YAML config:
```yaml
input:
  timestamp_min: "1/22/2026 14:10:12"
  timestamp_column: "Timestamp"
  timestamp_format: "%m/%d/%Y %H:%M:%S"
```

## Files Modified
1. `buddy_matching/gui/app.py` - Added filter application and live preview integration
2. `buddy_matching/gui/components.py` - Added `show_timestamp_filter_preview()` function
3. `test_timestamp_filter.py` - Created test script

## Common Issues & Solutions

### Issue: "Cannot preview timestamp filter: Invalid timestamp_min value"
**Cause**: Timestamp format doesn't match the format string
**Solution**: Adjust format string or timestamp value

### Issue: Filter shows 0 rows
**Cause**: Minimum timestamp is after all data timestamps
**Solution**: Check your minimum timestamp value

### Issue: Filter not applied after running
**Cause**: Filter not enabled, or missing required fields
**Solution**: 
- Check "Enable timestamp filter" checkbox is checked
- Ensure timestamp column is selected
- Ensure minimum timestamp is filled in

### Issue: "Missing timestamp column"
**Cause**: Selected column doesn't exist in Erasmus dataset
**Solution**: Select correct column name from dropdown (case-sensitive)

## Best Practices
1. **Use autodetected timestamp column** when available
2. **Specify format string** if timestamps are in non-standard format
3. **Check live preview** before running to verify filter effect
4. **Combine with buddy filter** for comprehensive filtering
5. **Check logs** after running to confirm filters were applied

## Status
✅ **FIXED and TESTED**
- Timestamp filter now works in GUI
- Live preview shows real-time effect
- Proper error handling and logging
- Consistent behavior with CLI
