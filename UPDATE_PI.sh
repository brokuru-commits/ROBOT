#!/bin/bash
# ============================================================
# CRITL OS - INITIAL UPDATE SCRIPT
# This script performs the one-time manual update on the Pi.
# ============================================================

# Navigate to the project directory
PROJECT_DIR="/home/martin/Dokumente/prog/HEUM-tec"

echo "------------------------------------------"
echo "CRITL OS: Starte manuelles Update..."
echo "------------------------------------------"

if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    
    # Perform git pull
    echo "Lade neue Dateien von GitHub..."
    git pull origin main
    
    if [ $? -eq 0 ]; then
        echo "------------------------------------------"
        echo "ERFOLG: System wurde aktualisiert!"
        echo "Das automatische Update ist jetzt aktiv."
        echo "Du kannst das System nun neu starten."
        echo "------------------------------------------"
    else
        echo "FEHLER: Git Pull ist fehlgeschlagen."
        echo "Prüfe deine Internetverbindung."
    fi
else
    echo "FEHLER: Projektordner nicht gefunden!"
    echo "Pfad: $PROJECT_DIR"
fi

# Keep window open for feedback
echo ""
echo "Drücke Enter zum Schließen..."
read
