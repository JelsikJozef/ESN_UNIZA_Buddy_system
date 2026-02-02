# ⚡ Quick Test Guide - Timestamp Filter

## 🎯 5-Minute Test / 5-Minútový Test

### 1. Spusti GUI / Start GUI
```bash
streamlit run buddy_matching/gui/app.py
```

### 2. Load Data / Nahraj dáta
- Go to **Input** screen
- Upload your XLSX or CSV files
- Click "Load Data"
- Wait for ✓ success message

### 3. Configure Timestamp Filter / Nastav Timestamp Filter
- Go to **Configure** screen
- Expand **"Timestamp Filter (optional)"**
- ✅ **Check** "Enable timestamp filter"
- **Select** timestamp column (e.g., "Timestamp")
- **Enter** minimum date: `1/22/2026 14:10:12`
- **Enter** format: `%m/%d/%Y %H:%M:%S`

### 4. Check Live Preview / Skontroluj Preview
Look for message like:
```
ℹ️ Erasmus: 60 / 100 rows after timestamp filter (>= 1/22/2026 14:10:12)
```

✅ If you see this → **Filter is configured correctly!**
❌ If you see warning → Check date format

### 5. Run Matching / Spusti Matching
- Go to **Run** screen
- Click **"Run Matching"** button
- Watch the logs

### 6. Verify in Logs / Over v Logoch
Look for message:
```
ℹ️ Applied timestamp filter: 60/100 Erasmus students (>= 1/22/2026 14:10:12)
```

✅ If you see this → **Filter was applied!**

### 7. Check Results / Skontroluj Výsledky
- Go to **Results** screen
- Check "Erasmus loaded total" count
- It should match the filtered count (e.g., 60)

---

## 🔥 Quick Troubleshooting / Rýchle Riešenie Problémov

### Problem: No live preview appears
**Solution**: Make sure all 3 fields are filled:
1. ✅ Checkbox enabled
2. ✅ Column selected
3. ✅ Minimum date entered

### Problem: "Cannot preview timestamp filter: ..."
**Solution**: Date format mismatch
- Try without format field first
- Or adjust format to match your date string

### Problem: 0 rows after filter
**Solution**: Your minimum date is too late
- Check the actual dates in your data
- Lower the minimum date

### Problem: Filter not applied in Run
**Solution**: 
1. Go back to Configure
2. Check all settings are still there
3. Click somewhere to trigger save
4. Try running again

---

## ✅ Success Indicators / Indikátory Úspechu

You'll know it's working when you see ALL of these:

1. ✅ Live preview in Configure shows filtered count
2. ✅ Log message during Run: "Applied timestamp filter: X/Y..."
3. ✅ Results screen shows reduced Erasmus count
4. ✅ Only recent students appear in matches

---

## 📊 Example Test Case / Príklad Test Case

**Your data:**
- 100 Erasmus students
- Dates range: 1/20/2026 to 1/25/2026

**Filter settings:**
- Minimum: `1/22/2026 14:10:12`
- Format: `%m/%d/%Y %H:%M:%S`

**Expected results:**
- Live preview: ~60-70 students remaining
- Log: "Applied timestamp filter: XX/100 Erasmus students"
- Matching uses only filtered students

**If you see these numbers → ✅ SUCCESS!**

---

## 🚀 Ready to Use!

After this test, you can confidently use timestamp filter in production.

**Pro tip**: Combine with buddy filter for even better results:
1. First: Timestamp filter (removes old applications)
2. Second: Buddy filter (removes students not wanting a buddy)
3. Result: Clean, current dataset for matching!
