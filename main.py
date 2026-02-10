#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
from datetime import datetime
import pygame

# --- DISPLAY FIX ---
# Dies zwingt Pygame, den ersten Monitor zu nutzen, 
# auch wenn das Script per Autostart oder Script kommt.
os.environ["DISPLAY"] = ":0"

# --- KONFIGURATION ---
WIDTH, HEIGHT = 640, 480
COLOR_BG       = (0, 10, 0)
COLOR_TOXIC    = (0, 255, 60)
COLOR_TEXT     = (200, 255, 200)
COLOR_SCANLINE = (0, 20, 0)

# Pfade absolut setzen, damit es von überall startet
BASE_DIR   = "/home/bot/robot/ui"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
EMOTES_DIR = os.path.join(ASSETS_DIR, "emotes")
TXT_FILE   = os.path.join(ASSETS_DIR, "emotions.txt")

def load_quotes():
    quotes_map = {}
    if os.path.exists(TXT_FILE):
        try:
            with open(TXT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line:
                        idx, text = line.split("|", 1)
                        quotes_map.setdefault(idx.strip(), []).append(text.strip())
            print(f"✅ {sum(len(v) for v in quotes_map.values())} Sprüche geladen.")
        except Exception as e:
            print(f"❌ Fehler beim Lesen der emotions.txt: {e}")
    else:
        print("⚠️ emotions.txt nicht gefunden! Nutze Standard-Texte.")
    return quotes_map

def main():
    print("--- HEUM-TEC SYSTEM START ---")
    
    # Pygame Initialisierung
    try:
        pygame.init()
        # Versuche Vollbild ohne Rahmen
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        pygame.mouse.set_visible(False)
        print("✅ Grafiksystem initialisiert.")
    except Exception as e:
        print(f"❌ KRITISCHER GRAFIKFEHLER: {e}")
        sys.exit()

    clock = pygame.time.Clock()
    
    # Schriften laden
    font_big = pygame.font.SysFont("monospace", 80, bold=True)
    font_date = pygame.font.SysFont("monospace", 40, bold=True)
    font_msg = pygame.font.SysFont("monospace", 22, bold=True)

    quotes_data = load_quotes()
    last_logic_update = 0
    current_id = "1"
    current_quote = "BOOTING..."
    
    scan_y = 0
    weekdays = ["MONTAG", "DIENSTAG", "MITTWOCH", "DONNERSTAG", "FREITAG", "SAMSTAG", "SONNTAG"]

    print("--- STARTE RENDERING ---")
    
    try:
        while True:
            # Event-Check (Esc zum Beenden im Testmodus)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            # Zeitsteuerung & Logik
            if time.time() - last_logic_update > 10:
                now_hour = datetime.now().hour
                # Deine Logik: 1=Happy, 2=Bored, 3=Panic, 4=Profit
                if now_hour >= 20: current_id = "4"
                elif 8 <= now_hour < 14: current_id = "2"
                elif random.random() < 0.05: current_id = "3" # 5% Chance auf Panik
                else: current_id = "1"
                
                possible_quotes = quotes_data.get(current_id, ["SYSTEM ONLINE"])
                current_quote = random.choice(possible_quotes)
                last_logic_update = time.time()

            # --- ZEICHNEN ---
            screen.fill(COLOR_BG)
            dt = datetime.now()

            # 1. Uhrzeit
            time_surf = font_big.render(dt.strftime("%H:%M"), True, COLOR_TOXIC)
            screen.blit(time_surf, (WIDTH//2 - time_surf.get_width()//2, 10))

            # 2. Datum
            date_str = f"{weekdays[dt.weekday()]} {dt.strftime('%d.%m.')}"
            date_surf = font_date.render(date_str, True, COLOR_TOXIC)
            screen.blit(date_surf, (WIDTH//2 - date_surf.get_width()//2, 90))

            # 3. Käfer-Bild
            img_path = os.path.join(EMOTES_DIR, f"{current_id}.png")
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert()
                    img = pygame.transform.scale(img, (200, 200))
                    screen.blit(img, (WIDTH//2 - 100, 130))
                except:
                    pygame.draw.rect(screen, COLOR_TOXIC, (WIDTH//2-50, 150, 100, 100), 1) # Platzhalter
            else:
                # Wenn Bild fehlt, zeichne einen Kasten als Warnung
                pygame.draw.rect(screen, (255,0,0), (WIDTH//2-50, 150, 100, 100), 2)

            # 4. Spruch
            msg_surf = font_msg.render(current_quote.upper(), True, COLOR_TEXT)
            screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT - 35))

            # 5. Scanline & Effekt
            scan_y = (scan_y + 2) % HEIGHT
            pygame.draw.line(screen, (0, 255, 60, 50), (0, scan_y), (WIDTH, scan_y), 1)
            for y in range(0, HEIGHT, 4):
                pygame.draw.line(screen, COLOR_SCANLINE, (0, y), (WIDTH, y))

            pygame.display.flip()
            clock.tick(30)

    except KeyboardInterrupt:
        print("\n--- SYSTEM SHUTDOWN ---")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
