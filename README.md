# SAP Module Simulator

![Status](https://img.shields.io/badge/status-MVP-green)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

Desktop application untuk simulasi SAP GUI dengan modul lengkap. Dibangun untuk learning & practice SAP workflows.

## 📦 Features

### ✅ Implemented
- **SAP GUI Shell**: T-code navigation, menu bar, status bar
- **MM01**: Material Master CRUD dengan validasi
- **ME21N**: Purchase Order creation dengan items
- **Master Data**: 36 materials, 10 vendors, 10 employees (imported dari Excel)

### 🚧 Roadmap
- [ ] MM03 - Display Material
- [ ] ME23N - Display Purchase Order
- [ ] MIGO - Goods Receipt
- [ ] PA30 - HR Master Data maintenance
- [ ] PA20 - Display HR Master
- [ ] FB01 - FI Document posting
- [ ] VA01 - Sales Order creation
- [ ] CO, PP, PM, EWM modules

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/dimasrifkypratama/Module_SAP.git
cd Module_SAP

# Run (auto-setup venv & dependencies)
./run.sh

# Or manual setup
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python excel_parser.py  # Import master data
.venv/bin/python main.py
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
| Materials Management | MM | 🟢 Active | MM01 ✅, ME21N ✅ |
| Human Capital | HCM | 🟡 Planned | PA30, PA20 |
| Finance | FI | 🟡 Planned | FB01 |
| Sales & Distribution | SD | 🟡 Planned | VA01 |
| Controlling | CO | ⚪ Future | - |
| Production Planning | PP | ⚪ Future | - |
| Plant Maintenance | PM | ⚪ Future | - |
| Extended Warehouse | EWM | ⚪ Future | - |

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
**Status**: MVP - 2 working T-codes, 8 modules planned
