#!/bin/bash
# CRITL OS - Automatisches Install/Update Script für Raspberry Pi
# Dieses Script kopiert alle Dateien und richtet Auto-Update beim Start ein

set -e  # Bei Fehler abbrechen

echo "================================================"
echo "  CRITL OS - Installation & Auto-Update Setup"
echo "================================================"
echo ""

# Zielverzeichnis (anpassen falls nötig)
TARGET_DIR="/home/pi/critl-os"
AUTOSTART_DIR="/home/pi/.config/autostart"

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[1/5]${NC} Erstelle Zielverzeichnis..."
mkdir -p "$TARGET_DIR"
mkdir -p "$TARGET_DIR/assets"
mkdir -p "$AUTOSTART_DIR"

echo -e "${YELLOW}[2/5]${NC} Kopiere Python-Dateien..."
cp -v *.py "$TARGET_DIR/" 2>/dev/null || echo "Einige .py Dateien nicht gefunden (OK)"

echo -e "${YELLOW}[3/5]${NC} Kopiere Assets..."
cp -v assets/*.txt "$TARGET_DIR/assets/" 2>/dev/null || echo "Einige .txt Dateien nicht gefunden (OK)"
cp -v assets/*.png "$TARGET_DIR/assets/" 2>/dev/null || echo "Einige .png Dateien nicht gefunden (OK)"
cp -v assets/*.ttf "$TARGET_DIR/assets/" 2>/dev/null || echo "Einige .ttf Dateien nicht gefunden (OK)"

echo -e "${YELLOW}[4/5]${NC} Kopiere Konfigurationsdateien..."
cp -v version.json "$TARGET_DIR/" 2>/dev/null || echo "version.json nicht gefunden (OK)"
cp -v .gitignore "$TARGET_DIR/" 2>/dev/null || true

echo -e "${YELLOW}[5/5]${NC} Richte Auto-Update beim Start ein..."

# Erstelle Autostart Desktop-Datei
cat > "$AUTOSTART_DIR/critl-os.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=CRITL OS
Comment=CRITL OS mit Auto-Update
Exec=/home/pi/critl-os/start_critl.sh
Terminal=false
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

# Erstelle Start-Script mit Auto-Update
cat > "$TARGET_DIR/start_critl.sh" << 'EOF'
#!/bin/bash
# CRITL OS Start-Script mit Auto-Update

cd /home/pi/critl-os

# Prüfe ob venv existiert, wenn nicht erstelle es
if [ ! -d ".venv" ]; then
    echo "Erstelle virtuelle Umgebung..."
    python3 -m venv .venv
    .venv/bin/pip install pygame
fi

# Aktiviere venv
source .venv/bin/activate

# Optional: Git Pull für Auto-Update (wenn Git-Repo vorhanden)
if [ -d ".git" ]; then
    echo "Prüfe auf Updates..."
    git pull origin main 2>/dev/null || echo "Kein Git-Update verfügbar"
fi

# Starte CRITL OS
python3 main.py

# Bei Fehler: Warte 5 Sekunden bevor Fenster schließt
if [ $? -ne 0 ]; then
    echo "Fehler beim Start. Warte 5 Sekunden..."
    sleep 5
fi
EOF

chmod +x "$TARGET_DIR/start_critl.sh"

echo ""
echo -e "${GREEN}✓ Installation abgeschlossen!${NC}"
echo ""
echo "CRITL OS wurde installiert nach: $TARGET_DIR"
echo "Auto-Start wurde eingerichtet."
echo ""
echo "Nächste Schritte:"
echo "1. Starte den Pi neu: sudo reboot"
echo "2. CRITL OS startet automatisch beim Booten"
echo ""
echo "Manueller Start: cd $TARGET_DIR && ./start_critl.sh"
echo ""
