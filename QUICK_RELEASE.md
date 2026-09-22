# Quick Release Guide

## Create v1.0.0 Release on GitHub

1. **Go to**: https://github.com/Manusi4hiu/Module_SAP/releases/new

2. **Fill form**:
   - Tag: `v1.0.0` (already pushed)
   - Title: `SAP Module Simulator v1.0.0`
   - Description:
     ```
     ## SAP Module Simulator - Complete Release
     
     Desktop training app dengan 14 T-codes across 8 SAP modules.
     
     ### Features
     - ✅ MM (Materials Management) - 5 T-codes
     - ✅ HCM (Human Capital) - 2 T-codes  
     - ✅ SD (Sales & Distribution) - 2 T-codes
     - ✅ FI (Finance) - 1 T-code
     - ✅ CO (Controlling) - 1 T-code
     - ✅ PP (Production Planning) - 1 T-code
     - ✅ PM (Plant Maintenance) - 1 T-code
     - ✅ EWM (Extended Warehouse) - 1 T-code
     
     ### Downloads
     
     **Windows 10/11** (build saat GitHub Actions jalan):
     - Download `SAP_Simulator.exe` (akan muncul di artifacts)
     - Double-click to run
     
     **Linux** (build saat GitHub Actions jalan):  
     - Download `SAP_Simulator-x86_64.AppImage`
     - `chmod +x` and run
     
     **Any OS** (manual):
     ```bash
     git clone https://github.com/Manusi4hiu/Module_SAP.git
     cd Module_SAP
     ./run.sh  # or run.bat on Windows
     ```
     
     ### What's Included
     - Cross-platform PyQt5 desktop app
     - SQLite database (36 materials, 10 vendors, 10 employees)
     - SAP-style error validation
     - Complete documentation
     ```

3. **Publish release** → GitHub Actions akan otomatis build binaries

## Manual Build (Optional)

### Windows
```cmd
pip install pyinstaller
python excel_parser.py
pyinstaller build_windows.spec
```
Output: `dist/SAP_Simulator.exe`

### Linux  
```bash
./build_appimage.sh
```
Output: `SAP_Simulator-x86_64.AppImage`

---

**Note**: Setelah release pertama, tag berikutnya (v1.0.1, v1.1.0, dst) otomatis trigger builds via GitHub Actions.
