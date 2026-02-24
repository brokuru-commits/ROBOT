#!/bin/bash
# CRITL OS - Einfaches Install-Script für Raspberry Pi
# Einfach ausführen mit: bash INSTALL_PI.sh

set -e  # Bei Fehler abbrechen

echo "================================================"
echo "  CRITL OS - Installation auf Raspberry Pi"
echo "  HEUM-TEC CRITL OS VERSION 2.1.0"
echo "================================================"
echo ""

# Finde das Script-Verzeichnis (USB-Stick)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "USB-Stick gefunden: $SCRIPT_DIR"
echo ""

# Frage nach Zielverzeichnis
read -p "CRITL OS Verzeichnis auf dem Pi [/home/pi/critl-os]: " TARGET_DIR
TARGET_DIR=${TARGET_DIR:-/home/pi/critl-os}

echo ""
echo "Zielverzeichnis: $TARGET_DIR"
echo ""

# Bestätigung
read -p "Alle Dateien nach $TARGET_DIR kopieren? (j/n): " CONFIRM
if [ "$CONFIRM" != "j" ] && [ "$CONFIRM" != "J" ]; then
    echo "Abgebrochen."
    exit 0
fi

echo ""
echo "[1/3] Erstelle Zielverzeichnis..."
mkdir -p "$TARGET_DIR"
mkdir -p "$TARGET_DIR/assets"

echo "[2/3] Kopiere Dateien..."
# Kopiere alle Python-Dateien
cp -v "$SCRIPT_DIR"/*.py "$TARGET_DIR/" 2>/dev/null || true

# Kopiere version.json
cp -v "$SCRIPT_DIR"/version.json "$TARGET_DIR/" 2>/dev/null || true

# Kopiere Assets
if [ -d "$SCRIPT_DIR/assets" ]; then
    cp -rv "$SCRIPT_DIR/assets"/* "$TARGET_DIR/assets/" 2>/dev/null || true
fi

echo ""
echo "[3/3] Setze Berechtigungen..."
chmod +x "$TARGET_DIR"/*.py 2>/dev/null || true

echo ""
echo "================================================"
echo "  ✓ Installation abgeschlossen!"
echo "================================================"
echo ""
echo "CRITL OS wurde installiert nach: $TARGET_DIR"
echo ""
echo "Neue Features:"
echo "  ✓ HEUM-TEC Boot-Screen beim Start"
echo "  ✓ Automatisches Update-System"
echo "  ✓ Optimierter Schlafmodus (17:00-7:00 & Wochenende)"
echo ""
echo "Da main.py automatisch beim Start lädt:"
echo "  → Einfach Pi neu starten: sudo reboot"
echo ""
echo "Oder manuell testen:"
echo "  → cd $TARGET_DIR && python3 main.py"
echo ""
