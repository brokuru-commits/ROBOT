#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, socket, urllib.request
from datetime import datetime
import pygame

# --- CONFIG ---
os.environ["SDL_VIDEODRIVER"] = "x11"
# Falls Touch nicht geht:
# os.environ["SDL_MOUSEDRV"] = "TSLIB"
# os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"

W, H = 480, 320
FPS = 30

# Farben
FALLOUT_GREEN = (50, 255, 50)
FALLOUT_DIM   = (10, 80, 10)
BLACK         = (0, 0, 0)
WHITE         = (255, 255, 255)
ALERT_RED     = (255, 50, 50)
BLUE_NEON     = (0, 200, 255)

# Pfade
BASE_DIR = os.path.expanduser("~/robot/ui/assets")
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
BG_PATH = os.path.join(BASE_DIR, "bg.png")

# GitHub Links
REPO_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/"
UPDATE_URL = REPO_URL + "main.py"
TODO_URL   = REPO_URL + "todo.txt"
ART_URL    = REPO_URL + "art.txt"
QUOTES_URL = REPO_URL + "quotes.txt"

# --- DEIN STUNDENPLAN ---
PLAN = [
    (7, 30, 8, 0, "ANKUNFT/PAUSE"),
    (8, 0, 8, 45, "UNTERRICHT 1"),
    (8, 45, 8, 50, "PAUSE (5min)"),
    (8, 50, 9, 35, "UNTERRICHT 2"),
    (9, 35, 9, 55, "PAUSE (20min)"),
    (9, 55, 10, 40, "UNTERRICHT 3"),
    (10, 40, 10, 45, "PAUSE (5min)"),
    (10, 45, 11, 30, "UNTERRICHT 4"),
    (11, 30, 11, 50, "PAUSE (20min)"),
    (11, 50, 12, 35, "UNTERRICHT 5"),
    (12, 35, 12, 40, "PAUSE (5min)"),
    (12, 40, 13, 25, "UNTERRICHT 6"),
    (13, 25, 13, 35, "PAUSE (10min)"),
    (13, 35, 14, 20, "UNTERRICHT 7"),
    (14, 20, 14, 25, "PAUSE (5min)"),
    (14, 25, 15, 10, "UNTERRICHT 8"),
    (15, 10, 15, 15, "PAUSE (5min)"),
    (15, 15, 16, 0, "UNTERRICHT 9"),
    (16, 0, 17, 0, "FEIERABEND")
]

# --- HELFER ---
def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read())/1000
    except: return 0.0

def fetch_data(url):
    try:
        r = urllib.request.urlopen(url, timeout=2)
        return [l.strip() for l in r.read().decode('utf-8').splitlines() if l.strip()]
    except: return []

def get_status():
    now = datetime.now()
    cur_min = now.hour * 60 + now.minute
    for (sh, sm, eh, em, label) in PLAN:
        start = sh * 60 + sm
        end = eh * 60 + em
        if start <= cur_min < end:
            total = end - start
            passed = cur_min - start
            return label, end - cur_min, passed / total if total > 0 else 0
    return "FREIZEIT", 0, 0.0

# --- HAUPTPROGRAMM ---
def main():
    pygame.init()
    pygame.mouse.set_visible(False) 
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    # Assets
    try: bg_img = pygame.transform.scale(pygame.image.load(BG_PATH), (W, H))
    except: bg_img = None

    try:
        f_xl = pygame.font.Font(FONT_PATH, 55)
        f_l = pygame.font.Font(FONT_PATH, 30)
        f_m = pygame.font.Font(FONT_PATH, 22)
        f_s = pygame.font.Font(FONT_PATH, 16)
        f_mono = pygame.font.SysFont("Courier", 20, bold=True)
    except:
        f_xl = f_l = f_m = f_s = f_mono = pygame.font.SysFont(None, 30)

    # Boot Daten laden (Quotes zuerst)
    boot_quotes = fetch_data(QUOTES_URL)
    if not boot_quotes: boot_quotes = ["SYSTEM START...", "LADE KERNEL...", "CHECK WIFI...", "HEUM-TEC ONLINE"]

    state = "BOOT" 
    boot_start = time.time()
    
    todos = []
    ascii_art = ["(o.o)", "/|_|\\", " | |"]
    
    # Buttons
    btn_home = pygame.Rect(400, 10, 70, 40) 
    btn_nav_todo = pygame.Rect(20, 240, 130, 60)
    btn_nav_calc = pygame.Rect(170, 240, 130, 60)
    btn_nav_upd  = pygame.Rect(320, 240, 130, 60)

    # Animation Vars
    emoji_color = FALLOUT_GREEN
    last_col_change = time.time()
    calc_inp = ""; calc_res = ""; calc_face = "( -_-)"

    while True:
        # HINTERGRUND
        if state != "BOOT" and bg_img: screen.blit(bg_img, (0,0))
        elif state != "BOOT": screen.fill(BLACK)

        # INPUT
        click_pos = None
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN: click_pos = e.pos
            elif e.type == pygame.FINGERDOWN: click_pos = (int(e.x*W), int(e.y*H))

        # --- STATE MACHINE ---

        # 1. BOOT SCREEN
        if state == "BOOT":
            screen.fill(BLACK)
            elapsed = time.time() - boot_start
            
            # Disco Title
            rnd_col = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
            txt = f_xl.render("HEUM-TEC V2.2", True, rnd_col)
            screen.blit(txt, (W//2 - txt.get_width()//2, H//2 - 60))
            
            # Ladebalken
            bar_w = int((elapsed / 6.0) * 400)
            pygame.draw.rect(screen, rnd_col, (40, H//2, bar_w, 20))
            
            # --- HIER SIND DIE QUOTES ---
            # Wir berechnen, welcher Spruch dran ist
            q_idx = int((elapsed / 6.0) * len(boot_quotes))
            if q_idx < len(boot_quotes):
                q_surf = f_m.render(boot_quotes[q_idx], True, WHITE)
                screen.blit(q_surf, (W//2 - q_surf.get_width()//2, H//2 + 30))
            
            if elapsed > 6.0:
                state = "HOME"
                # Restliche Daten laden
                raw_art = fetch_data(ART_URL)
                if raw_art: 
                     parts = "\n".join(raw_art).split("---")
                     ascii_art = random.choice(parts).strip().split("\n")

        # 2. HOME SCREEN
        elif state == "HOME":
            # Header
            pygame.draw.circle(screen, FALLOUT_GREEN, (20, 20), 5)
            temp = get_temp()
            col_temp = FALLOUT_GREEN if temp < 60 else ALERT_RED
            screen.blit(f_s.render(f"{temp:.0f}C", True, col_temp), (35, 12))
            
            # ASCII Art (Mitte)
            if time.time() - last_col_change > 0.5:
                emoji_color = (random.randint(50,255), random.randint(100,255), random.randint(50,255))
                last_col_change = time.time()
            y_art = 60
            for line in ascii_art:
                surf = f_mono.render(line, True, emoji_color)
                screen.blit(surf, (W//2 - surf.get_width()//2, y_art))
                y_art += 25

            # STUNDENPLAN
            label, rest, prog = get_status()
            if label != "FREIZEIT":
                if "PAUSE" in label: bar_col = BLUE_NEON
                elif "FEIER" in label: bar_col = (100, 0, 100)
                else: bar_col = FALLOUT_GREEN
                
                pygame.draw.rect(screen, FALLOUT_DIM, (40, 170, 400, 40))
                pygame.draw.rect(screen, bar_col, (40, 170, int(400*prog), 40))
                
                screen.blit(f_m.render(label, True, WHITE), (50, 180))
                screen.blit(f_m.render(f"NOCH {rest} MIN", True, WHITE), (280, 180))
            else:
                msg = f_l.render("FREIZEIT!", True, BLUE_NEON)
                screen.blit(msg, (W//2 - msg.get_width()//2, 175))

            # Navigation
            for btn, txt, col in [(btn_nav_todo, "TO-DO", FALLOUT_GREEN), (btn_nav_calc, "NOTEN", FALLOUT_GREEN), (btn_nav_upd, "UPDATE", ALERT_RED)]:
                pygame.draw.rect(screen, FALLOUT_DIM, btn)
                pygame.draw.rect(screen, col, btn, 2)
                t_surf = f_m.render(txt, True, col)
                screen.blit(t_surf, (btn.centerx - t_surf.get_width()//2, btn.centery - t_surf.get_height()//2))

            if click_pos:
                if btn_nav_todo.collidepoint(click_pos): 
                    state = "TODO"; todos = fetch_data(TODO_URL)
                if btn_nav_calc.collidepoint(click_pos): state = "CALC"
                if btn_nav_upd.collidepoint(click_pos): state = "UPDATE"

        # 3. TO-DO
        elif state == "TODO":
            screen.blit(f_l.render("AUFGABEN", True, FALLOUT_GREEN), (20, 20))
            y_off = 70
            for i, item in enumerate(todos[:6]):
                box = pygame.Rect(20, y_off, 440, 35)
                pygame.draw.rect(screen, FALLOUT_DIM, box, 1)
                screen.blit(f_m.render(item, True, WHITE), (30, y_off+5))
                if click_pos and box.collidepoint(click_pos):
                    del todos[i]; click_pos = None
                y_off += 40
            
            pygame.draw.rect(screen, FALLOUT_DIM, btn_home, 1)
            screen.blit(f_m.render("HOME", True, FALLOUT_GREEN), (btn_home.x+10, btn_home.y+10))
            if click_pos and btn_home.collidepoint(click_pos): state = "HOME"

        # 4. UPDATE
        elif state == "UPDATE":
            screen.fill((50, 0, 0))
            msg = f_l.render("GITHUB UPDATE STARTEN?", True, WHITE)
            screen.blit(msg, (W//2 - msg.get_width()//2, 80))
            btn_yes = pygame.Rect(60, 180, 160, 80); btn_no = pygame.Rect(260, 180, 160, 80)
            
            pygame.draw.rect(screen, FALLOUT_GREEN, btn_yes); screen.blit(f_l.render("JA", True, BLACK), (120, 205))
            pygame.draw.rect(screen, ALERT_RED, btn_no); screen.blit(f_l.render("NEIN", True, BLACK), (310, 205))
            
            if click_pos:
                if btn_no.collidepoint(click_pos): state = "HOME"
                if btn_yes.collidepoint(click_pos):
                    screen.fill(BLACK); pygame.display.flip()
                    try: urllib.request.urlretrieve(UPDATE_URL, "/home/bot/robot/ui/main.py"); sys.exit()
                    except: state = "HOME"

        # 5. RECHNER
        elif state == "CALC":
            screen.blit(f_l.render("NOTEN RECHNER", True, FALLOUT_GREEN), (20, 20))
            pygame.draw.rect(screen, FALLOUT_DIM, (20, 70, 200, 50))
            screen.blit(f_l.render(calc_inp, True, WHITE), (30, 80))
            screen.blit(f_xl.render(calc_res, True, FALLOUT_GREEN), (250, 80))
            screen.blit(f_l.render(calc_face, True, FALLOUT_GREEN), (360, 90))
            
            pygame.draw.rect(screen, FALLOUT_DIM, btn_home, 1)
            screen.blit(f_m.render("HOME", True, FALLOUT_GREEN), (btn_home.x+10, btn_home.y+10))
            if click_pos and btn_home.collidepoint(click_pos): state = "HOME"

            keys = [('7', 20, 140), ('8', 90, 140), ('9', 160, 140), ('4', 20, 200), ('5', 90, 200), ('6', 160, 200),
                    ('1', 20, 260), ('2', 90, 260), ('3', 160, 260), ('0', 90, 320), ('C', 20, 320), ('=', 160, 320)]
            for k, kx, ky in keys:
                r = pygame.Rect(kx, ky, 60, 50)
                pygame.draw.rect(screen, FALLOUT_DIM, r, 1); screen.blit(f_m.render(k, True, WHITE), (kx+20, ky+15))
                if click_pos and r.collidepoint(click_pos):
                    if k == 'C': calc_inp = ""; calc_res = ""; calc_face = "( -_-)"
                    elif k == '=':
                        try:
                            note = 6 - (5 * float(calc_inp) / 100)
                            calc_res = f"{note:.1f}"
                            calc_face = "(^o^)" if note < 2 else "(>_<)" if note > 4 else "( -_-)"
                        except: calc_res = "ERR"
                    else: 
                        if len(calc_inp) < 3: calc_inp += k

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
