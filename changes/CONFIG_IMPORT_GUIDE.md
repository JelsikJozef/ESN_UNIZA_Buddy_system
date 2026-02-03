# Quick Guide: Loading config.yml in the GUI

**For ESN Coordinators**

---

## What is Config Import?

Config import allows you to load previously saved configuration files into the GUI, automatically setting up all your preferences without manual configuration.

---

## How to Use

### Step 1: Export Your Configuration (First Time)

1. Go to the **Configure** screen
2. Set up your configuration:
   - Select filters
   - Choose question columns
   - Set matching parameters
3. Scroll to **Config Export / Import**
4. Click **"Export Config to YAML"**
5. Click **"Download config.yml"**
6. Save the file (e.g., `my_config.yml`)

### Step 2: Import Configuration (Next Time)

1. Go to the **Configure** screen
2. Scroll to **Config Export / Import**
3. In the right column, find **"Import YAML config"**
4. Click **"Browse files"**
5. Select your saved config file (e.g., `my_config.yml`)
6. Wait for success message: **"✓ Config imported successfully!"**
7. Review the settings above to verify

### Step 3: Verify and Run

1. **Check the imported settings**:
   - Scroll up to verify filters
   - Check question columns
   - Confirm matching parameters
2. **Adjust if needed** (optional)
3. Go to **Run** screen and execute pipeline

---

## What Gets Imported?

The config import loads:
- ✅ **Buddy filter** settings (enabled/disabled, column, value)
- ✅ **Timestamp filter** settings (enabled/disabled, column, min value, format)
- ✅ **Required columns**
- ✅ **Identifier column**
- ✅ **Question columns** (all selected questions)
- ✅ **Top K** value
- ✅ **Output settings** (per-ESN sheets, extra fields, prefix)

---

## Common Workflows

### Workflow 1: Save Time on Repeated Tasks

**Scenario**: You run matching every semester with the same settings

1. **First semester**: Configure manually → Export config
2. **Next semester**: Load data → Import config → Run
3. **Result**: 5 minutes saved per run

### Workflow 2: Share Configuration

**Scenario**: Multiple coordinators need the same settings

1. **Coordinator A**: Set up config → Export → Share file
2. **Coordinator B**: Load data → Import shared config → Run
3. **Result**: Consistent configurations across team

### Workflow 3: Version Control

**Scenario**: Track configuration changes over time

1. Save configs with dates: `config_2026_spring.yml`
2. Store in folder or Git repository
3. Load specific version when needed
4. **Result**: Easy rollback and comparison

---

## Important Notes

### ✅ What Works
- Import any config.yml file (GUI or CLI format)
- Partial configurations (only some sections)
- Multiple imports (overwrites previous values)
- Works with already-loaded data

### ⚠️ What to Check
- **Column names must match your data**
  - If imported config references "Question 1" but your data has "Q1", you'll need to adjust
  - The importer doesn't validate column names

- **Data must be loaded first**
  - Import config AFTER loading data
  - This helps you verify column names exist

### 🚫 Limitations
- **Doesn't load data files** - only configuration
- **Doesn't validate columns** - you must verify they exist
- **Overwrites current settings** - previous configuration is replaced

---

## Troubleshooting

### "Failed to import config" Error

**Possible causes**:
1. Invalid YAML syntax in file
2. File is corrupted
3. Wrong file format (not .yml or .yaml)

**Solution**:
- Check file is valid YAML
- Try re-exporting from a working session
- Open file in text editor to verify syntax

### Settings Don't Appear After Import

**Cause**: Config file might be empty or have different structure

**Solution**:
- Check the config file content
- Verify it has the expected structure
- Re-export a config from working session

### Columns Not Found Error When Running

**Cause**: Imported column names don't exist in loaded data

**Solution**:
- After importing, review question columns
- Remove non-existent columns
- Add correct column names
- Re-export config for future use

---

## Example Config File

Here's what a typical config.yml looks like:

```yaml
filters:
  buddy_interest:
    enabled: true
    column: "Buddy"
    value: "Yes"
  timestamp_min:
    enabled: true
    column: "Timestamp"
    min_value: "1/22/2026 14:10:12"
    format: "%m/%d/%Y %H:%M:%S"

schema:
  required_columns:
    - Name
    - Surname
    - Timestamp
  identifier_column: "Timestamp"
  question_columns:
    - Are you an introvert or extrovert
    - Do you like to party
    - What is your favorite music genre

matching:
  metric: hamming
  top_k: 10

output:
  per_esner_sheets: true
  include_extra_fields: true
  out_prefix: "matching_"
```

You can edit this file in any text editor if needed!

---

## Tips & Best Practices

### 1. Name Your Configs Clearly
```
✅ Good: config_spring_2026.yml
✅ Good: config_engineering_students.yml
❌ Bad: config.yml
❌ Bad: my_config_v2_final_FINAL.yml
```

### 2. Keep a Config Library
Create a folder with common configurations:
```
configs/
├── standard_matching.yml
├── engineering_only.yml
├── business_only.yml
└── high_matching_threshold.yml
```

### 3. Document Your Configs
Add comments in YAML files:
```yaml
# Configuration for Spring 2026 intake
# Uses strict buddy filter: Yes only
# Top 10 matches per ESN member
filters:
  buddy_interest:
    enabled: true
    # ...
```

### 4. Test Before Sharing
Before sharing a config:
1. Import it yourself
2. Run a test pipeline
3. Verify results
4. Then share with team

### 5. Version Your Configs
Use Git or file versioning:
```bash
git add config_spring_2026.yml
git commit -m "Add Spring 2026 configuration"
```

---

## Summary

**Config import saves time by**:
- ⏱️ Eliminating manual configuration
- 🔄 Enabling configuration reuse
- 🤝 Facilitating team collaboration
- 📊 Supporting consistent processes

**Remember**:
1. Load data first
2. Import config second
3. Verify settings third
4. Run pipeline fourth

---

**Status**: ✅ Feature is ready to use!

**Location**: Configure screen → Config Export / Import section → Right column
