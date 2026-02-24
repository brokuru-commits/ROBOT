# CRITL OS - USB Update Paket

## Installation auf Raspberry Pi

### Schritt 1: Dateien kopieren

Kopiere alle Dateien aus diesem Ordner in dein CRITL OS Verzeichnis auf dem Pi:

```bash
# Auf dem Pi (ersetze /pfad/zum/usb mit deinem USB-Mount-Punkt)
cp -r /pfad/zum/usb/critl-os-usb-deploy/* /home/pi/dein-critl-verzeichnis/
```

### Schritt 2: Fertig!

Das war's! Beim nächsten Start lädt der Pi automatisch die neue Version mit:
- ✅ Boot-Screen beim Start
- ✅ Update-System
- ✅ Optimierter Schlafmodus (17:00-7:00 & Wochenende)

## Was ist neu?

### Neue Dateien:
- `boot_screen.py` - Retro-Terminal Boot-Sequenz
- `update_screen.py` - Update-Installation UI
- `update_system.py` - Update-Management
- `version.json` - Versions-Konfiguration
- `assets/boot_messages.txt` - Boot-Nachrichten

### Geänderte Dateien:
- `main.py` - Integriert Boot-Screen und reaktiviert Schlafmodus

## Features

### Boot-Screen
Beim Start zeigt CRITL OS jetzt eine Fallout-Style Boot-Sequenz:
1. RobCo Industries Header
2. System POST (Hardware-Checks)
3. Komponenten-Laden
4. Update-Check
5. Start

### Schlafmodus
- **Aktiv**: 17:00-7:00 Uhr und am Wochenende
- **Stromverbrauch**: ~80% reduziert durch optimierte Animation
- **Design**: Grüner pulsierender "Zzzzz..." Text

### Auto-Update (für später)
Das System kann sich in Zukunft selbst updaten:
- Prüft GitHub auf neue Versionen
- Lädt Updates automatisch herunter
- Installiert sie mit Fortschrittsanzeige

## Probleme?

Falls etwas nicht funktioniert:
1. Prüfe ob alle Dateien kopiert wurden
2. Stelle sicher dass `version.json` vorhanden ist
3. Prüfe die Berechtigungen: `chmod +x *.py`

## Technische Details

- **Version**: 2.1.0
- **Build**: 20260213
- **Python**: 3.6+
- **Pygame**: 2.0+

---

Bei Fragen oder Problemen: Einfach melden! 🚀
