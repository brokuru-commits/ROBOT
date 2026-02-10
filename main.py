#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
from datetime import datetime
import pygame

# --- DISPLAY FIX ---
os.environ["DISPLAY"] = ":0"

# --- KONFIGURATION (Auf 640x480 angepasst) ---
WIDTH, HEIGHT = 640, 480
COLOR_BG       = (0, 10, 0)
COLOR_TOXIC    = (0, 255, 60)
COLOR_TEXT     = (200, 255, 200)
COLOR_SCANLINE = (0, 20, 0)

# Pfade absolut setzen
BASE_DIR   = "/home/bot/robot/ui"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
EMOTES_DIR = os.path.join(ASSETS_DIR, "emotes")
TXT_FILE   = os.path.join(ASSETS_DIR, "emotions.txt")

def load_quotes():
    """Laedt Sprueche ohne Sonderzeichen-Fehler."""
    quotes_map = {}
    if os.path.exists(TXT_FILE):
        try:
            with open(TXT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line:
                        idx, text = line.split("|", 1)
                        quotes_map.setdefault(idx.strip(), []).append(text.strip())
            print("INFO: Sprueche erfolgreich geladen.")
        except Exception as e:
            print("ERROR: Fehler beim Lesen der emotions.txt")
    else:
        print("WARNUNG: emotions.txt nicht gefunden.")
    return quotes_map

def main():
    print("--- HEUM-TEC SYSTEM START (640x480) ---")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        pygame.mouse.set_visible(False)
        print("OK: Grafiksystem initialisiert.")
    except Exception as e:
        print("ERROR: Kritischer Grafikfehler.")
        sys.exit()

    clock = pygame.time.Clock()
    
    # Schriftgrößen für 640x480 leicht erhöht
    font_big = pygame.font.SysFont("monospace", 110, bold=True)
    font_date = pygame.font.SysFont("monospace", 55, bold=True)
    font_msg = pygame.font.SysFont("monospace", 28, bold=True)

    quotes_data = load_quotes()
    last_logic_update = 0
    current_id = "1"
    current_quote = "BOOTING..."
    
    scan_y = 0
    glitch_offset = 0
    glitch_timer = 0
    weekdays = ["MONTAG", "DIENSTAG", "MITTWOCH", "DONNERSTAG", "FREITAG", "SAMSTAG", "SONNTAG"]

    print("--- STARTE RENDERING ---")
    
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            # Logik & Zeit (1=Happy, 2=Bored, 3=Panic, 4=Profit)
            if time.time() - last_logic_update > 12:
                now_hour = datetime.now().hour
                if now_hour >= 20: current_id = "4"
                elif 8 <= now_hour < 14: current_id = "2"
                elif random.random() < 0.08: current_id = "3" 
                else: current_id = "1"
                
                possible_quotes = quotes_data.get(current_id, ["SYSTEM ONLINE"])
                current_quote = random.choice(possible_quotes)
                last_logic_update = time.time()

            # Glitch-Logik
            if glitch_timer > 0:
                glitch_timer -= 1
                glitch_offset = random.randint(-4, 4)
            else:
                if random.random() < 0.01: glitch_timer = 4
                glitch_offset = 0

            # --- ZEICHNEN ---
            screen.fill(COLOR_BG)
            dt = datetime.now()

            # 1. Uhrzeit (Zentral)
            time_surf = font_big.render(dt.strftime("%H:%M"), True, COLOR_TOXIC)
            screen.blit(time_surf, (WIDTH//2 - time_surf.get_width()//2 + glitch_offset, 20))

            # 2. Datum & Wochentag
            date_str = f"{weekdays[dt.weekday()]} {dt.strftime('%d.%m.')}"
            date_surf = font_date.render(date_str, True, COLOR_TOXIC)
            screen.blit(date_surf, (WIDTH//2 - date_surf.get_width()//2, 130))

            # 3. Kafer-Bild (Groesser für 640x480)
            img_path = os.path.join(EMOTES_DIR, f"{current_id}.png")
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert()
                    img = pygame.transform.scale(img, (280, 280))
                    screen.blit(img, (WIDTH//2 - 140 + glitch_offset, 190))
                except:
                    pygame.draw.rect(screen, COLOR_TOXIC, (WIDTH//2-70, 200, 140, 140), 1)
            else:
                pygame.draw.rect(screen, (100,0,0), (WIDTH//2-70, 200, 140, 140), 1)

            # 4. Spruch
            msg_surf = font_msg.render(current_quote.upper(), True, COLOR_TEXT)
            screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT - 45))

            # 5. Scanlines & Radar-Effekt
            scan_y = (scan_y + 3) % HEIGHT
            pygame.draw.line(screen, (0, 255, 60, 60), (0, scan_y), (WIDTH, scan_y), 2)
            for y in range(0, HEIGHT, 4):
                pygame.draw.line(screen, COLOR_SCANLINE, (0, y), (WIDTH, y))

            pygame.display.flip()
            clock.tick(30)

    except KeyboardInterrupt:
        print("Shutdown")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
