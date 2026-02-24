╔════════════════════════════════════════════════════════════╗
║  CRITL OS - USB Installation für Raspberry Pi             ║
║  HEUM-TEC CRITL OS VERSION 2.1.0                          ║
╚════════════════════════════════════════════════════════════╝

INSTALLATION - NUR 2 SCHRITTE:
═══════════════════════════════════════════════════════════

1. USB-Stick in den Raspberry Pi stecken

2. Terminal öffnen und ausführen:
   
   cd /media/pi/USB-NAME/critl-os-usb-deploy
   bash INSTALL_PI.sh

   (Ersetze USB-NAME mit dem Namen deines USB-Sticks)

3. Fertig! Pi neu starten:
   
   sudo reboot


ALTERNATIVE (falls USB anders gemountet):
═══════════════════════════════════════════════════════════

1. USB-Stick finden:
   ls /media/pi/
   
2. Zum USB-Ordner wechseln:
   cd /media/pi/DEIN-USB/critl-os-usb-deploy
   
3. Script ausführen:
   bash INSTALL_PI.sh


WAS PASSIERT BEIM INSTALL:
═══════════════════════════════════════════════════════════

✓ Alle Python-Dateien werden kopiert
✓ Alle Assets (Grafiken, Sounds, Fonts) werden kopiert
✓ version.json wird kopiert
✓ Berechtigungen werden gesetzt

Das Script fragt dich nach dem Zielverzeichnis
(Standard: /home/pi/critl-os)


NEUE FEATURES:
═══════════════════════════════════════════════════════════

✓ HEUM-TEC Boot-Screen beim Start
✓ Automatisches Update-System
✓ Optimierter Schlafmodus (17:00-7:00 & Wochenende)


PROBLEME?
═══════════════════════════════════════════════════════════

Falls das Script nicht läuft:
1. Berechtigungen prüfen: chmod +x INSTALL_PI.sh
2. Manuell kopieren: cp -r * /home/pi/critl-os/

Bei Fragen: Einfach melden!
