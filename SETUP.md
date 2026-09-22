# SAP Module Simulator - Setup Complete

## Project Structure
```
Module_SAP/
├── main.py              # Main application entry point
├── database.py          # SQLite database layer
├── excel_parser.py      # Import master data from Excel
├── run.sh               # Launch script (Linux)
├── sap_style.qss        # SAP GUI stylesheet
├── requirements.txt     # Python dependencies
├── screens/
│   ├── po_create.py     # ME21N Purchase Order creation
│   └── master_data.py   # MM01 Material Master CRUD
└── sap_simulator.db     # SQLite database (auto-generated)
```

## Setup & Run

### First Time Setup
```bash
cd ~/Program/Module_SAP
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python excel_parser.py  # Import master data
```

### Run Application
```bash
./run.sh
# or
.venv/bin/python main.py
```

## Implemented Features

### ✅ MM - Materials Management
- [x] **MM01** - Material Master CRUD
- [x] **ME21N** - Create Purchase Order
- [ ] MM03 - Display Material
- [ ] ME23N - Display Purchase Order
- [ ] MIGO - Goods Receipt

### ⬜ HCM - Human Capital Management  
- [ ] PA30 - Maintain HR Master
- [ ] PA20 - Display HR Master

### ⬜ FI - Finance
- [ ] FB01 - Post Document

### ⬜ SD - Sales & Distribution
- [ ] VA01 - Create Sales Order

### ⬜ CO - Controlling
### ⬜ PP - Production Planning
### ⬜ PM - Plant Maintenance
### ⬜ EWM - Extended Warehouse

## Master Data Imported
- Materials: 28 records (from MM Excel)
- Vendors: 10 records (from SD Excel)
- Employees: 10 records (from HCM Excel)

## Usage Guide

1. **Launch app** → SAP GUI-style window appears
2. **Enter T-code** in toolbar (e.g., `MM01` or `ME21N`)
3. **Or use menu** → MM - Materials Management → select transaction
4. **MM01**: Create/edit material master data
5. **ME21N**: Create purchase orders with items
6. **F3** to go back to home screen
7. **Ctrl+S** to save (in transaction screens)

## Next Steps
- Implement MM03 (Display Material)
- Add ME23N (Display PO)
- Build HCM PA30 screen
- Add validation & error messages
- Implement remaining modules

## GitHub Repository
```bash
git remote add origin https://github.com/YOUR_USERNAME/Module_SAP.git
git push -u origin master
```

## Technical Notes
- PyQt5 for native desktop UI
- SQLite for local data storage
- SAP GUI-inspired styling (QSS)
- Excel files as data source (one-time import)
- Modular screen architecture (screens/ directory)

## Development
```bash
# Add new transaction screen
# 1. Create screens/new_screen.py
# 2. Import in main.py
# 3. Add to execute_tcode() switch
# 4. Mark implemented=1 in database.py tcodes list
```
