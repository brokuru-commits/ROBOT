#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, socket, urllib.request
from datetime import datetime, date
import pygame

# --- TOUCH & DISPLAY CONFIG ---
os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["SDL_MOUSEDRV"] = "TSLIB"

W, H = 480, 320
FPS = 30
BLACK = (0, 0, 0)
VERSION = "V 1.9 - ULTIMATE" 

# Pfade & Links
BASE_DIR = os.path.expanduser("~/robot/ui/assets")
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
UPDATE_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/main.py"
TODO_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/todo.txt"
QUOTES_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/quotes.txt"
ART_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/art.txt"

PALETTES = [
    ((0, 80, 0), (100, 255, 100)),   # Klassik Grün
    ((0, 40, 80), (100, 200, 255)),  # Sci-Fi Blau
    ((80, 40, 0), (255, 180, 50)),   # Fallout Amber
    ((60, 0, 80), (200, 100, 255)),  # Cyberpunk Lila
]

# --- DATEN-ABRUF ---
def fetch_data(url, default=["DATEN-ERROR"]):
    try:
        response = urllib.request.urlopen(url, timeout=3)
        return [line.strip() for line in response.read().decode('utf-8').splitlines() if line.strip()]
    except: return default

def get_random_art():
    lines = fetch_data(ART_URL, ["(o.o)", "---", "[0_0]"])
    full_text = "\n".join(lines)
    arts = full_text.split("---")
    return random.choice(arts).strip().split("\n")

def get_sys():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read())/1000
    except: return 0.0

# --- BOOT ANIMATION ---
def run_boot_screen(screen, f_b, f_m, f_s):
    start_t = time.time()
    boot_quotes = fetch_data(QUOTES_URL, ["LADE SYSTEM...", "HEUM-TEC ONLINE."])
    random_art = get_random_art()
    col = PALETTES[0][1] # Startfarbe Grün
    
    while time.time() - start_t < 4:
        screen.fill(BLACK)
        prog = int(((time.time()-start_t)/4)*100)
        
        # ASCII Art
        for i, line in enumerate(random_art):
            art_surf = f_s.render(line, True, col)
            screen.blit(art_surf, (W//2 - art_surf.get_width()//2, 170 + (i*15)))

        # Header & Ladebalken
        txt = f_b.render("HEUM-TEC SYSTEMS", True, col)
        screen.blit(txt, (W//2-txt.get_width()//2, 30))
        pygame.draw.rect(screen, col, (90, 100, 300, 20), 1)
        pygame.draw.rect(screen, col, (93, 103, int(294*(min(prog,100)/100)), 14))
        
        # Spruch
        q_idx = min(int((prog/101)*len(boot_quotes)), len(boot_quotes)-1)
        screen.blit(f_m.render(boot_quotes[q_idx], True, col), (W//2-50, 130))
        
        pygame.display.flip()
        time.sleep(0.01)

# --- MAIN LOOP ---
def main():
    pygame.init()
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

    # Initiales Booten
    run_boot_screen(screen, f_b, f_m, f_s)
    
    raw_todos = fetch_data(TODO_URL, ["KEIN SYNC"])
    done_todos = []
    
    btn_start = pygame.Rect(270, 225, 190, 65)
    btn_update = pygame.Rect(445, 5, 30, 30)
    
    scan_text = "<<>><<>><<>><<>><<>><<>><<>><<>><<>><<>>"
    scan_pos = 0; scan_dir = 1
    current_palette = PALETTES[0]
    last_color_change = time.time()

    while True:
        screen.fill(BLACK)
        now = datetime.now()
        
        if time.time() - last_color_change > 120:
            current_palette = random.choice(PALETTES)
            last_color_change = time.time()

        active_todos = [t for t in raw_todos if t not in done_todos][:5]
        col_dim, col_bright = current_palette

        for e in pygame.event.get():
            pos = None
            if e.type == pygame.MOUSEBUTTONDOWN: pos = e.pos
            elif e.type == pygame.FINGERDOWN: pos = (int(e.x * W), int(e.y * H))
            
            if pos:
                if btn_update.collidepoint(pos):
                    try: urllib.request.urlretrieve(UPDATE_URL, "/home/bot/robot/ui/main.py")
                    except: pass
                    sys.exit()
                if btn_start.collidepoint(pos):
                    raw_todos = fetch_data(TODO_URL, ["KEIN SYNC"])
                    done_todos = []
                for i, item in enumerate(active_todos):
                    item_rect = pygame.Rect(25, 155 + (i*28), 220, 25)
                    if item_rect.collidepoint(pos):
                        done_todos.append(item)

        # UI
        screen.blit(f_h.render(now.strftime("%H:%M"), True, col_bright), (20, 10))
        screen.blit(f_b.render(now.strftime("%d.%m.%Y"), True, col_dim), (25, 80))
        screen.blit(f_m.render("TO-DO (TAP TO DONE):", True, col_bright), (25, 130))
        
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

        screen.blit(f_s.render(f"TEMP: {get_sys():.1f}C", True, (50,50,50)), (300, 140))
        screen.blit(f_s.render(VERSION, True, (40,40,40)), (5, 305))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
