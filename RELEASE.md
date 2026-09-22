# Release Checklist

## Pre-release

1. All tests passing: `python test.py`
2. Version bump in README badges
3. Git clean: `git status`
4. Tag version: `git tag v1.0.0 && git push --tags`

## Build Binaries

### Windows .exe
- Run on Windows machine: `pyinstaller build_windows.spec`
- Test: `dist/SAP_Simulator.exe`
- Size: ~50MB

### Linux AppImage
- Run: `./build_appimage.sh`
- Test: `./SAP_Simulator-x86_64.AppImage`
- Size: ~80MB

## GitHub Release

1. Go to: https://github.com/Manusi4hiu/Module_SAP/releases/new
2. Tag: `v1.0.0`
3. Title: `SAP Module Simulator v1.0.0`
4. Upload:
   - `SAP_Simulator.exe` (Windows)
   - `SAP_Simulator-x86_64.AppImage` (Linux)
   - `Source code (zip)` (auto-generated)
5. Release notes:
   ```
   ## Features
   - 14 T-codes across 8 SAP modules
   - MM, HCM, SD, FI, CO, PP, PM, EWM
   - SAP-style validation & error codes
   - Cross-platform: Windows 10/11, Linux

   ## Downloads
   - **Windows**: SAP_Simulator.exe (50MB, no install)
   - **Linux**: SAP_Simulator-x86_64.AppImage (80MB, portable)
   - **Any OS**: Clone repo & run ./run.sh or run.bat
   ```

## Post-release

Update README badge:
```markdown
![Release](https://img.shields.io/github/v/release/Manusi4hiu/Module_SAP)
```
