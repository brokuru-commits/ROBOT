# HEUM-tec CRITL OS

CRITL OS ist ein interaktives System für den Raspberry Pi, entwickelt von HEUM-TEC. Es bietet eine einzigartige Mischung aus KI-Persönlichkeit, Storytelling und Mini-Spielen.

## Features
- **Interaktive KI**: CRITL reagiert auf deine Eingaben und Bedürfnisse.
- **Story-System**: Schalte Geschichten und Meme-Events frei.
- **Hacking-Simulator**: Spiele Mini-Games im Terminal-Look.
- **Boot-Screen**: Authentisches HEUM-TEC Boot-Erlebnis.
- **Update-System**: Automatische Aktualisierungen über GitHub.

## Installation auf dem Raspberry Pi
Um CRITL OS auf deinem Pi zu installieren:

1. Lade dieses Repository herunter oder klone es.
2. Kopiere den Inhalt auf einen USB-Stick oder direkt auf den Pi.
3. Führe das Installations-Skript aus:
   ```bash
   bash INSTALL_PI.sh
   ```
4. Folge den Anweisungen auf dem Bildschirm. Standardmäßig wird alles nach `/home/pi/critl-os` installiert.

Weitere Informationen zur Installation findest du in der `README_PI.txt`.

## Struktur
- `main.py`: Die Hauptanwendung.
- `assets/`: Alle Grafiken, Sounds und Story-Inhalte.
- `update_system.py`: Verwaltet die automatischen Updates.
- `INSTALL_PI.sh`: Installations-Skript für den Pi.
