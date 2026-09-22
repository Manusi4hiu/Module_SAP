# Testing Guide

## Automated Tests

### Unit Test
```bash
.venv/bin/python test.py
```
Checks: database, master data counts, T-code count

### Integration Test
```bash
.venv/bin/python test_integration.py
```
**Note**: Requires X display (GUI environment)
Checks: All T-codes load without errors

---

## Manual Testing Checklist

### MM - Materials Management ✓
- [ ] **MM01** - Create material (MAT9999, "Test Material")
  - Fill all fields → Save → Check success message
- [ ] **MM03** - Display material (MAT1001)
  - Load existing → Verify readonly, no edit buttons
- [ ] **ME21N** - Create PO
  - Vendor C1001 → Add 2 items → F8 check → Ctrl+S save
- [ ] **ME23N** - Display PO
  - Enter saved PO number → Verify shows header + items
- [ ] **MIGO** - Goods Receipt
  - Load PO → Enter GR qty → F8 → Post → Check success

### HCM - Human Capital ✓
- [ ] **PA30** - Create employee (999999, "Test Employee")
  - Fill all fields → Save → Success message
- [ ] **PA20** - Display employee (100001)
  - Load existing → Verify readonly

### SD - Sales & Distribution ✓
- [ ] **VA01** - Create SO
  - Customer C1001 → Add items → F8 → Ctrl+S
- [ ] **VA03** - Display SO
  - Load saved SO → Verify header + items

### FI - Finance ✓
- [ ] **FB01** - Post document
  - Add 2 lines: Debit 1000, Credit 1000
  - F8 → Balance green → Ctrl+S → Success
  - Test error: Unbalanced (should fail with F5 001)

### CO - Controlling ✓
- [ ] **KS01** - Cost Center
  - Create CC1001 "IT Department" → Save
  - Edit existing → Modify budget → Save

---

## Error Validation Tests

### Required Fields
- [ ] ME21N: Save without vendor → Error ME 022
- [ ] ME21N: Save without items → Error ME 023
- [ ] VA01: Save without customer → Error VA 020
- [ ] MIGO: Post without GR qty → Error MB 045
- [ ] FB01: Post unbalanced → Error F5 001
- [ ] FB01: Post empty → Error F5 002
- [ ] FB01: Post 1 line → Error F5 003
- [ ] KS01: Save without ID → Error CO 001

### Navigation
- [ ] F3 from any screen → Returns to home
- [ ] Invalid T-code (XXX) → Error message
- [ ] Menu navigation → Loads correct screen

---

## Workflow Tests

### Procurement Flow (MM)
1. MM01 → Create material MAT9999
2. ME21N → Create PO with MAT9999 (qty 10)
3. ME23N → Display saved PO → Verify
4. MIGO → Load PO → Receive qty 5
5. MIGO → Load same PO → Pending shows 5

### Sales Flow (SD)
1. VA01 → Create SO with 3 items
2. VA03 → Display saved SO → Verify all items

### Finance Flow (FI)
1. FB01 → Post journal entry
2. Verify document number generated
3. Check database: fi_documents table has entry

---

## Database Integrity

After testing, check:
```bash
sqlite3 sap_simulator.db "
  SELECT COUNT(*) FROM purchase_orders;
  SELECT COUNT(*) FROM goods_receipts;
  SELECT COUNT(*) FROM sales_orders;
  SELECT COUNT(*) FROM fi_documents;
  SELECT COUNT(*) FROM cost_centers;
"
```

Expected: Non-zero counts after testing

---

## Performance

- [ ] App launch < 3 seconds
- [ ] T-code switch < 1 second
- [ ] Save operations < 500ms
- [ ] Display screens load < 500ms

---

## Cross-Platform

### Linux
```bash
./run.sh
```

### Windows
```cmd
run.bat
```

Verify: Same functionality both platforms

---

**Test Status**: Ready for manual QA  
**Automated**: Unit tests passing  
**Integration**: Requires GUI environment
