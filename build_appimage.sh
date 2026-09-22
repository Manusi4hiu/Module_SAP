#!/bin/bash
# Build AppImage for Linux distribution
set -e

echo "Building SAP Simulator AppImage..."

# Create AppDir structure
mkdir -p AppDir/usr/{bin,lib,share/applications,share/icons}

# Copy application
cp -r *.py screens/ sap_style.qss AppDir/usr/bin/
cp sap_simulator.db AppDir/usr/bin/ 2>/dev/null || python3 excel_parser.py && cp sap_simulator.db AppDir/usr/bin/

# Install Python deps into AppDir
python3 -m venv AppDir/usr
AppDir/usr/bin/pip install PyQt5 openpyxl

# Create launcher
cat > AppDir/usr/bin/sap_simulator << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./python main.py
EOF
chmod +x AppDir/usr/bin/sap_simulator

# Desktop entry
cat > AppDir/usr/share/applications/sap_simulator.desktop << EOF
[Desktop Entry]
Name=SAP Simulator
Exec=sap_simulator
Type=Application
Categories=Education;
EOF

# AppRun
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/sap_simulator" "$@"
EOF
chmod +x AppDir/AppRun

# Download appimagetool if missing
if [ ! -f appimagetool-x86_64.AppImage ]; then
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
./appimagetool-x86_64.AppImage AppDir SAP_Simulator-x86_64.AppImage

echo "✓ Built: SAP_Simulator-x86_64.AppImage"
