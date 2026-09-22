# Building Distributable Binaries

## Windows (.exe)

**Requirements**: Windows 10/11, Python 3.8+

```cmd
pip install pyinstaller
python excel_parser.py
pyinstaller build_windows.spec
```

Output: `dist/SAP_Simulator.exe` (~50MB, standalone)

---

## Linux (AppImage)

**Requirements**: Ubuntu/Debian, Python 3.8+

```bash
# Install dependencies
sudo apt install python3-pip python3-venv

# Build
./build_appimage.sh
```

Output: `SAP_Simulator-x86_64.AppImage` (~80MB, portable)

---

## Manual (Any OS)

Already works:
```bash
git clone https://github.com/Manusi4hiu/Module_SAP.git
cd Module_SAP
./run.sh  # Linux/Mac
run.bat   # Windows
```

Launchers auto-install dependencies.
