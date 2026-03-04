# ROBOT OS - Update Guide

Dieses Dokument erklärt, wie du das neue **ROBOT OS** (ehemals HEUM-TEC) auf deinen Raspberry Pi bringst.

## Option 1: Der einfache Weg (Empfohlen) ✅

Verwende das mitgelieferte Script. Es kopiert alle Dateien an den richtigen Ort und **repariert automatisch deinen Autostart**, damit das neue System beim Booten lädt.

1. Stecke den USB-Stick in den Pi.
2. Öffne ein Terminal.
3. Gehe zum USB-Ordner:
   ```bash
   cd /media/pi/DEIN-USB-NAME/robot-usb-deploy
   ```
4. Starte die Installation:
   ```bash
   bash INSTALL_PI.sh
   ```
5. Starte den Pi neu: `sudo reboot`

---

## Option 2: Manuelles Kopieren (Drag & Drop) 📂

Du kannst die Dateien auch einfach rüberziehen, aber dann musst du den Autostart von Hand anpassen.

1. Kopiere alle Dateien vom USB-Stick nach `/home/bot/robot/`.
2. Öffne die Autostart-Datei im Editor:
   ```bash
   nano ~/.config/lxsession/LXDE-pi/autostart
   ```
3. Suche die Zeile, die die alte Version startet (z.B. `@python3 /home/pi/critl-os/main.py`).
4. Ändere sie auf den neuen Pfad:
   ```text
   @python3 /home/bot/robot/main.py
   ```
5. Speichere mit `Strg+O`, `Enter` und beende mit `Strg+X`.

---

## Warum das Script besser ist:
- Es erkennt alte Pfade (`critl-os`, `HEUM-tec`, etc.) automatisch.
- Es setzt die richtigen Dateiberechtigungen.
- Es stellt sicher, dass alle Assets im richtigen Unterordner landen.

## Fehlerbehebung
Falls der Autostart gar nicht geht, prüfe ob `python3 /home/bot/robot/main.py` im Terminal ohne Fehler startet.
