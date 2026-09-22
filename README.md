# SAP Module Simulator

![Status](https://img.shields.io/badge/status-Complete-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

Desktop application untuk simulasi SAP GUI dengan 8 modul lengkap (14 T-codes). Dibangun untuk learning & practice SAP workflows.

## 📦 Features

- **SAP GUI Shell**: T-code navigation, menu bar, status bar, F3 back
- **14 T-codes**: MM (5), HCM (2), SD (2), FI (1), CO (1), PP (1), PM (1), EWM (1)
- **Master Data**: 36 materials, 10 vendors, 10 employees (imported dari Excel)
- **SAP-style Validation**: Error codes (ME 022, F5 001, etc.), balance checks
- **CRUD Operations**: Create, display, edit across all modules
- **Cross-platform**: Linux + Windows 10/11

## 🚀 Quick Start

**Linux/macOS**:
```bash
git clone https://github.com/Manusi4hiu/Module_SAP.git
cd Module_SAP
./run.sh
```

**Windows 10/11**:
```cmd
git clone https://github.com/Manusi4hiu/Module_SAP.git
cd Module_SAP
run.bat
```

**Manual setup** (semua OS):
```bash
python -m venv .venv
# Linux/Mac: .venv/bin/pip install -r requirements.txt
# Windows: .venv\Scripts\pip install -r requirements.txt
python excel_parser.py
python main.py
```

## 📖 Usage

1. **Launch app** → SAP GUI window
2. **Enter T-code** (MM01, ME21N) di toolbar
3. **Or navigate menu** → MM - Materials Management → pilih transaction
4. **Keyboard shortcuts**:
   - `F3` = Back
   - `F8` = Check/Execute
   - `Ctrl+S` = Save

## 🏗️ Architecture

```
Module_SAP/
├── main.py              # PyQt5 main window & T-code router
├── database.py          # SQLite ORM layer
├── excel_parser.py      # Import Excel → SQLite
├── sap_style.qss        # SAP GUI CSS theme
├── screens/
│   ├── po_create.py     # ME21N screen
│   └── master_data.py   # MM01 screen
└── sap_simulator.db     # SQLite database
```

**Tech Stack**:
- **PyQt5**: Native desktop UI
- **SQLite**: Local data persistence
- **openpyxl**: Excel data import
- **Python 3.12**

## 📊 Database Schema

```sql
-- Master data
materials (material_id, description, material_group, uom, plant, ...)
vendors (vendor_id, name, city, payment_terms, credit_limit)
employees (personnel_no, name, department, position, basic_salary)

-- Transactional
purchase_orders (po_number, vendor_id, status, total_value)
po_items (po_number, item_no, material_id, quantity, unit_price)

-- System
tcodes (code, module, name, implemented)
user_progress (module, tcode, completed, score)
```

## 🎯 Module Progress

| Module | Code | Status | T-codes |
|--------|------|--------|---------|
| Materials Management | MM | ✅ Complete | MM01, MM03, ME21N, ME23N, MIGO |
| Human Capital | HCM | ✅ Complete | PA30, PA20 |
| Sales & Distribution | SD | ✅ Complete | VA01, VA03 |
| Finance | FI | ✅ Complete | FB01 |
| Controlling | CO | ✅ Complete | KS01 |
| Production Planning | PP | ✅ Complete | MD61 |
| Plant Maintenance | PM | ✅ Complete | IW31 |
| Extended Warehouse | EWM | ✅ Complete | LT01 |

## 🧪 Testing

```bash
python test.py  # Health check: DB, data counts, T-codes
```

## 📝 Data Source

Master data imported dari Excel workbooks:
- `~/Downloads/SAP MODUL/SAP_MM_WORK_SIMULATOR.xlsx`
- `~/Downloads/SAP MODUL/SAP_SD_WORK_SIMULATOR.xlsx`
- `~/Downloads/SAP MODUL/SAP_HCM_WORK_SIMULATOR.xlsx`

Credit: Excel simulators by [@amouralulla](https://twitter.com/amouralulla)

## 🤝 Contributing

1. Fork repo
2. Create feature branch (`git checkout -b feature/new-tcode`)
3. Implement screen di `screens/`
4. Update `main.py` router & `database.py` tcode list
5. Commit & PR

## 📄 License

MIT License - free for learning & personal use

## 🙏 Acknowledgments

- Excel SAP simulators by @amouralulla
- PyQt5 documentation
- SAP GUI design reference

---

**Author**: Dimas Rifky Pratama  
**Purpose**: Learning SAP workflows untuk IT Support role preparation  
**Status**: Complete - 14 T-codes, 8 modules (100%)
