# Fix: Configuration State Persistence Issue

## Problem
Configuration settings were disappearing when navigating between pages in the Streamlit GUI.

## Root Cause
Streamlit widgets with `key` parameters create separate entries in `st.session_state`. When a widget has both a `key` and a `value` parameter, but the `value` isn't consistently set from the state object, the widget gets reset to its default value on each page reload.

The code was updating dataclass objects (`config_state.buddy_filter_enabled = ...`) but the widgets were using keys that created separate session state entries, causing a disconnect between the dataclass state and the widget state.

## Solution Applied

### Changed: Removed widget `key` parameters from Configure screen
All configuration widgets in `show_configure_screen()` now rely on their `value` parameters being set from `config_state` dataclass, and the dataclass is updated after each widget interaction.

**Before:**
```python
buddy_enabled = st.checkbox(
    "Enable buddy interest filter",
    value=config_state.buddy_filter_enabled,
    key="buddy_filter_enabled"  # This created a separate state entry
)
config_state.buddy_filter_enabled = buddy_enabled
```

**After:**
```python
buddy_enabled = st.checkbox(
    "Enable buddy interest filter",
    value=config_state.buddy_filter_enabled  # Widget value comes from dataclass
)
config_state.buddy_filter_enabled = buddy_enabled  # Dataclass updated immediately
```

### Widgets Fixed
1. **Buddy Filter Section:**
   - `buddy_filter_enabled` checkbox
   - `buddy_filter_column` selectbox
   - `buddy_filter_value` text input

2. **Timestamp Filter Section:**
   - `timestamp_filter_enabled` checkbox
   - `timestamp_filter_column` selectbox
   - `timestamp_filter_min` text input
   - `timestamp_filter_format` text input

3. **Required Columns Section:**
   - `required_columns` multiselect

4. **Identifier Column Section:**
   - `identifier_column` selectbox

5. **Question Columns Section:**
   - `question_columns` multiselect
   - "Select Autodetected" button
   - "Clear Selection" button
   - "Show Question Health Report" checkbox

6. **Matching Settings:**
   - `top_k` slider

7. **Output Settings:**
   - `per_esner_sheets` checkbox
   - `include_extra_fields` checkbox
   - `output_prefix` text input

8. **Config Import/Export:**
   - "Export Config to YAML" button
   - YAML file uploader

9. **Run Screen:**
   - "Run Matching" button

### Added: Configuration Summary Display
Added a collapsible "Current Configuration Summary" section at the top of the Configure screen showing:
- Number of question columns selected
- Number of required columns
- Top K value
- Buddy filter status
- Timestamp filter status
- Per-ESN sheets setting

This provides immediate visual feedback that settings are being preserved.

## How to Verify the Fix

### Test Procedure:
1. **Start the GUI:**
   ```bash
   streamlit run buddy_matching/gui/app.py
   ```

2. **Load Data (Input Screen):**
   - Upload your XLSX file or CSV files
   - Click "Load Data"
   - Verify data preview appears

3. **Configure Settings (Configure Screen):**
   - Enable buddy filter
   - Select a buddy interest column
   - Change the accepted value (e.g., "Yes")
   - Select 5-10 question columns manually
   - Change Top K to a specific value (e.g., 15)
   - Enable "Include extra Erasmus fields"

4. **Navigate Away:**
   - Click on "Run" in the sidebar

5. **Return to Configure:**
   - Click on "Configure" in the sidebar

6. **Verify Settings Persist:**
   - ✓ Buddy filter should still be enabled
   - ✓ Selected buddy interest column should be preserved
   - ✓ Accepted value should match what you set
   - ✓ Question columns should show the same count/selection
   - ✓ Top K should be 15
   - ✓ "Include extra Erasmus fields" should be checked
   - ✓ Configuration Summary shows correct values

7. **Test Run Screen:**
   - Go to "Run" screen
   - Pre-run checklist should show:
     - ✓ Input data loaded
     - ✓ X question columns selected (your count)
     - ✓ Buddy filter configured

## Technical Details

### State Management Architecture
The GUI uses dataclass objects stored in `st.session_state` for state management:

```python
st.session_state.config = ConfigState()  # Dataclass instance
```

All configuration values are stored in this dataclass and persisted across page navigations automatically by Streamlit's session state mechanism.

### Widget Pattern
The correct pattern for state persistence is:

1. Read current state from dataclass for widget `value`
2. Widget returns user's selection
3. Immediately update dataclass with new value
4. No `key` parameter unless widget needs to be uniquely identified for callbacks

### Why This Works
- Streamlit's `session_state` persists dataclass objects across reruns
- Widgets without keys don't create separate state entries
- Widget `value` parameters ensure UI reflects dataclass state
- Dataclass updates happen in the same script run, before navigation

## Related Files Modified
- `buddy_matching/gui/app.py` - Main application file with all widget fixes

## No Changes Needed To
- `buddy_matching/gui/state.py` - State management classes remain unchanged
- `buddy_matching/gui/components.py` - Helper components remain unchanged
- Pipeline and business logic - No changes to matching algorithm

## Future Considerations
If you need to add new configuration options:
1. Add the field to `ConfigState` dataclass in `state.py`
2. In the Configure screen, use `value=config_state.your_field`
3. Immediately update: `config_state.your_field = widget_return_value`
4. Avoid using `key` parameters unless absolutely necessary
