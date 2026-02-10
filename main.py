#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, socket, urllib.request
from datetime import datetime, date
import pygame

# --- TOUCH-FIX ---
# Wir versuchen, die gängigsten Treiber für kleine Displays zu laden
os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["SDL_MOUSEDRV"] = "TSLIB"

W, H = 480, 320
FPS = 30
BLACK = (0, 0, 0)
VERSION = "V 1.8 - FINAL DEBUG" 

# Pfade & Links
BASE_DIR = os.path.expanduser("~/robot/ui/assets")
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
UPDATE_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/main.py"
TODO_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/todo.txt"

# Farbpaletten (Grundfarbe, Hellere Nuance)
PALETTES = [
    ((0, 80, 0), (100, 255, 100)),   # Klassik Grün
    ((0, 40, 80), (100, 200, 255)),  # Sci-Fi Blau
    ((80, 40, 0), (255, 180, 50)),   # Fallout Amber
    ((60, 0, 80), (200, 100, 255)),  # Cyberpunk Lila
]

def fetch_todo():
    try:
        response = urllib.request.urlopen(TODO_URL, timeout=3)
        return [line.strip() for line in response.read().decode('utf-8').splitlines() if line.strip()]
    except: return ["KEIN SYNC - PRÜFE WLAN"]

def main():
    pygame.init()
    # Mauszeiger sichtbar lassen, um Kalibrierung zu prüfen
    pygame.mouse.set_visible(True)
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    
    try:
        f_h = pygame.font.Font(FONT_PATH, 70); f_b = pygame.font.Font(FONT_PATH, 28)
        f_m = pygame.font.Font(FONT_PATH, 18); f_s = pygame.font.Font(FONT_PATH, 16)
        f_l = pygame.font.SysFont("Courier", 18, bold=True)
    except:
        f_h = pygame.font.SysFont(None, 70); f_b = pygame.font.SysFont(None, 30)
        f_m = f_s = f_l = pygame.font.SysFont(None, 20)

    # Daten laden
    raw_todos = fetch_todo()
    done_todos = []
    
    # UI Elemente
    btn_start = pygame.Rect(270, 225, 190, 65)
    btn_update = pygame.Rect(445, 5, 30, 30)
    
    # Scanner Setup
    scan_text = "<<>><<>><<>><<>><<>><<>><<>><<>><<>><<>>"
    scan_pos = 0; scan_dir = 1
    current_palette = PALETTES[0]
    last_color_change = time.time()
    
    debug_msg = "Warte auf Input..."

    while True:
        screen.fill(BLACK)
        now = datetime.now()
        
        # Farbwechsel alle 120 Sekunden
        if time.time() - last_color_change > 120:
            current_palette = random.choice(PALETTES)
            last_color_change = time.time()

        active_todos = [t for t in raw_todos if t not in done_todos][:5]

        # EVENT LOOP
        for e in pygame.event.get():
            pos = None
            if e.type == pygame.MOUSEBUTTONDOWN:
                pos = e.pos
                debug_msg = f"Touch bei: {pos}"
            elif e.type == pygame.FINGERDOWN:
                pos = (int(e.x * W), int(e.y * H))
                debug_msg = f"Finger bei: {pos}"
            
            if pos:
                print(debug_msg) # Ausgabe im Terminal
                
                # Update Button
                if btn_update.collidepoint(pos):
                    debug_msg = "Update gestartet..."
                    try: urllib.request.urlretrieve(UPDATE_URL, "/home/bot/robot/ui/main.py")
                    except: pass
                    sys.exit()
                
                # Refresh/Start
                if btn_start.collidepoint(pos):
                    raw_todos = fetch_todo()
                    done_todos = []
                
                # To-Do Items antippen
                for i, item in enumerate(active_todos):
                    item_rect = pygame.Rect(25, 155 + (i*28), 220, 25)
                    if item_rect.collidepoint(pos):
                        done_todos.append(item)

        # --- ZEICHNEN ---
        col_dim, col_bright = current_palette
        
        # Uhr & Datum
        screen.blit(f_h.render(now.strftime("%H:%M"), True, col_bright), (20, 10))
        screen.blit(f_b.render(now.strftime("%d.%m.%Y"), True, col_dim), (25, 80))
        
        # To-Do Liste
        screen.blit(f_m.render("TO-DO (TAB TO DONE):", True, col_bright), (25, 130))
        for i, item in enumerate(active_todos):
            pygame.draw.rect(screen, col_dim, (30, 160 + (i*28), 15, 15), 1)
            screen.blit(f_s.render(item, True, col_dim), (55, 158 + (i*28)))

        # Refresh Button
        pygame.draw.rect(screen, col_dim, btn_start, 1)
        screen.blit(f_b.render("REFRESH", True, col_bright), (btn_start.centerx-50, btn_start.centery-10))
        
        # Scanner Leiste
        scan_pos += 0.4 * scan_dir
        if scan_pos >= len(scan_text)-4 or scan_pos <= 0: scan_dir *= -1
        
        for i, char in enumerate(scan_text):
            char_col = col_bright if abs(i - scan_pos) < 3 else col_dim
            screen.blit(f_l.render(char, True, char_col), (25 + (i * 11), 305))

        # Status & Debug (ganz klein)
        screen.blit(f_s.render(debug_msg, True, (40,40,40)), (280, 10))
        screen.blit(f_s.render(VERSION, True, (40,40,40)), (5, 305))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
