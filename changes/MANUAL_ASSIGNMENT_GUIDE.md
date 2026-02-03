# Manual Assignment Quick Reference Guide

**For ESN Coordinators**

---

## What is Manual Assignment?

Manual assignment allows you to manually pair an Erasmus student with an ESN buddy member, overriding the automatic ranking system. Once assigned, a student cannot be assigned to another ESN member (preventing double assignments).

---

## How to Assign a Buddy

### Step 1: Run the Matching Pipeline
1. Load your data in the **Input** screen
2. Configure filters in the **Configure** screen
3. Click **Run Matching** in the **Run** screen
4. Wait for completion

### Step 2: Browse and Assign
1. Go to the **Results** screen
2. Select an ESN member from the dropdown
3. View their ranked matches
4. In the **Manual Assignment** section:
   - Select an available student (not marked "ASSIGNED")
   - Click **"Assign to this ESN member"**
5. See success message
6. Student is now marked as "ASSIGNED"

### Step 3: View All Assignments
1. On the **Results** screen, expand **"Current Assignments"**
2. View table of all assignments with timestamps
3. See total assignment count

### Step 4: Export Assignments
1. Go to the **Export** screen
2. Scroll to **"Export Assigned Buddies"**
3. Click **"Download Assignments as CSV"** for quick export
4. Or click **"Generate Assignments XLSX"** then **"Download"** for Excel

---

## Key Features

✅ **Duplicate Prevention**: Each student can only be assigned once  
✅ **Visual Status**: Assigned students clearly marked in ranking table  
✅ **Remove Assignments**: Unassign students if needed  
✅ **Timestamp Tracking**: All assignments timestamped automatically  
✅ **Multiple Formats**: Export as CSV or Excel  

---

## Important Notes

⚠️ **Assignments are session-based**: They exist only during your current browser session. Make sure to export before closing the browser.

⚠️ **Assignments don't affect ranking**: The ranking algorithm is not modified. Rankings remain the same for reference.

⚠️ **One student, one buddy**: A student can only be assigned to one ESN member at a time.

---

## Troubleshooting

### "Student is already assigned" error
**Solution**: The student has already been assigned to another ESN member. Check the "Current Assignments" section to see who they're assigned to.

### No students available to assign
**Reason**: All students in the ranking are already assigned.  
**Solution**: Either unassign a student or select a different ESN member.

### Assignments disappeared after refresh
**Reason**: Assignments are session-based and not saved automatically.  
**Solution**: Always export your assignments before closing the browser.

---

## Example Workflow

**Scenario**: You have 10 ESN members and 50 Erasmus students

1. Run the pipeline (10 ESN × top 10 matches = 100 ranking entries)
2. Review rankings for "Alice Brown"
3. Assign "Bob Green" (ranked #1) to Alice
4. Bob now shows as "ASSIGNED" everywhere
5. Bob cannot be assigned to any other ESN member
6. Review rankings for "Carol White"
7. Bob is still in Carol's ranking but marked "ASSIGNED"
8. Assign "Dave Black" to Carol instead
9. Export all assignments at the end

**Result**: 
- 2 manual assignments made
- CSV file with Alice→Bob and Carol→Dave
- Clear audit trail with timestamps

---

## Export File Format

### CSV Format
```
ESN_Name,ESN_Surname,Erasmus_Name,Erasmus_Surname,Assignment_Timestamp
Alice,Brown,Bob,Green,2026-02-03T10:30:00
Carol,White,Dave,Black,2026-02-03T10:35:00
```

### Excel Format
- Sheet name: "Assignments"
- Same columns as CSV
- Professionally formatted

---

## Best Practices

1. **Export frequently**: Don't wait until the end to export
2. **Review before assigning**: Check the student's profile in the ranking
3. **Use rankings as guidance**: The ranking system provides good recommendations
4. **Document special cases**: Add notes externally for non-standard assignments
5. **Verify before closing**: Always check "Current Assignments" before closing browser

---

## Support

For technical issues or questions, refer to:
- Full documentation: `changes/MANUAL_ASSIGNMENT_FEATURE.md`
- Architecture guide: `architecture.md`
- Test files: `tests/test_assignments.py`, `tests/test_export_assignments.py`

---

**Version**: 1.0  
**Last Updated**: 2026-02-03
