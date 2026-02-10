#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, socket, urllib.request
from datetime import datetime, date
import pygame

# --- CONFIG ---
os.environ["SDL_VIDEODRIVER"] = "x11"
# Falls Touch zickt:
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

# --- STUNDENPLAN (BITTE ANPASSEN!) ---
# (Stunde_Start, Minute_Start, Stunde_Ende, Minute_Ende)
STUNDEN = [
    (7, 30, 8, 15),  # 1. Stunde
    (8, 20, 9, 5),   # 2. Stunde
    (9, 25, 10, 10), # 3. Stunde
    (10, 15, 11, 0), # 4. Stunde
    (11, 20, 12, 5), # 5. Stunde
    (12, 10, 12, 55) # 6. Stunde
]

# --- FUNKTIONEN ---
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

def get_school_status():
    """Gibt Text, Restzeit in Min und Fortschritt (0.0-1.0) zurück"""
    now = datetime.now()
    cur_min = now.hour * 60 + now.minute
    
    # 1. Ist Unterricht?
    for i, (sh, sm, eh, em) in enumerate(STUNDEN):
        start = sh * 60 + sm
        end = eh * 60 + em
        if start <= cur_min <= end:
            return f"STUNDE {i+1}", end - cur_min, (cur_min-start)/(end-start)
    
    # 2. Ist Pause?
    for i in range(len(STUNDEN)-1):
        _, _, eh, em = STUNDEN[i]
        sh, sm, _, _ = STUNDEN[i+1]
        start = eh * 60 + em
        end = sh * 60 + sm
        if start <= cur_min <= end:
            return "PAUSE", end - cur_min, (cur_min-start)/(end-start)

    return "FREIZEIT", 0, 0.0

# --- UI LOGIK ---
def main():
    pygame.init()
    pygame.mouse.set_visible(False) # <--- MAUSZEIGER WEG!
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    # Assets laden
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

    # State Variables
    state = "BOOT" # BOOT, HOME, TODO, CALC, UPDATE
    boot_start = time.time()
    
    # Daten
    todos = []
    ascii_art = ["(o.o)", "/|_|\\", " | |"]
    
    # Buttons definieren
    # Hauptmenü (Unten)
    btn_home = pygame.Rect(400, 10, 70, 40) # Oben rechts immer Home
    
    # Menü Buttons (Home Screen)
    btn_nav_todo = pygame.Rect(20, 240, 130, 60)
    btn_nav_calc = pygame.Rect(170, 240, 130, 60)
    btn_nav_upd  = pygame.Rect(320, 240, 130, 60)

    # ToDo Buttons
    btn_refresh = pygame.Rect(300, 10, 90, 40)
    
    # Calc Variablen
    calc_inp = ""
    calc_res = ""
    calc_face = "( -_-)"
    
    # Animation
    emoji_color = FALLOUT_GREEN
    last_col_change = time.time()

    while True:
        # --- HINTERGRUND ---
        if state != "BOOT" and bg_img: screen.blit(bg_img, (0,0))
        elif state != "BOOT": screen.fill(BLACK)

        # --- INPUT ---
        click_pos = None
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN: click_pos = e.pos
            elif e.type == pygame.FINGERDOWN: click_pos = (int(e.x*W), int(e.y*H))

        # --- LOGIK & UPDATE ---
        
        # 1. BOOT SCREEN (Bunt & Laut)
        if state == "BOOT":
            screen.fill(BLACK)
            elapsed = time.time() - boot_start
            
            # Disco Text
            rnd_col = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
            txt = f_xl.render("HEUM-TEC OS", True, rnd_col)
            screen.blit(txt, (W//2 - txt.get_width()//2, H//2 - 50))
            
            # Ladebalken Bunt
            bar_w = int((elapsed / 6.0) * 400)
            pygame.draw.rect(screen, rnd_col, (40, H//2 + 20, bar_w, 30))
            
            if elapsed > 6.0:
                state = "HOME"
                # Daten einmalig laden
                raw_art = fetch_data(ART_URL)
                if raw_art: 
                     # Splitte art.txt bei "---" und nimm zufälliges
                     parts = "\n".join(raw_art).split("---")
                     ascii_art = random.choice(parts).strip().split("\n")

        # 2. HOME SCREEN
        elif state == "HOME":
            # Status Icons oben links
            pygame.draw.circle(screen, FALLOUT_GREEN, (20, 20), 5) # Power
            temp = get_temp()
            col_temp = FALLOUT_GREEN if temp < 60 else ALERT_RED
            screen.blit(f_s.render(f"{temp:.0f}C", True, col_temp), (35, 12))
            
            # ASCII Art (Mitte) - Farbe wechselt
            if time.time() - last_col_change > 0.5:
                emoji_color = (random.randint(50,255), random.randint(100,255), random.randint(50,255))
                last_col_change = time.time()
                
            y_art = 80
            for line in ascii_art:
                surf = f_mono.render(line, True, emoji_color)
                screen.blit(surf, (W//2 - surf.get_width()//2, y_art))
                y_art += 25

            # Schul-Fortschrittsbalken
            label, rest_min, prog = get_school_status()
            if label != "FREIZEIT":
                # Balken Hintergrund
                pygame.draw.rect(screen, FALLOUT_DIM, (40, 180, 400, 30))
                # Füllung (Grün für Stunde, Blau für Pause)
                bar_col = FALLOUT_GREEN if "STUNDE" in label else BLUE_NEON
                pygame.draw.rect(screen, bar_col, (40, 180, int(400*prog), 30))
                
                info = f"{label}: noch {rest_min} min"
                screen.blit(f_m.render(info, True, WHITE), (50, 185))
            else:
                screen.blit(f_l.render("FREIZEIT!", True, BLUE_NEON), (W//2-60, 180))

            # Navigation Buttons zeichnen
            pygame.draw.rect(screen, FALLOUT_DIM, btn_nav_todo); pygame.draw.rect(screen, FALLOUT_GREEN, btn_nav_todo, 2)
            screen.blit(f_m.render("TO-DO", True, FALLOUT_GREEN), (btn_nav_todo.centerx-30, btn_nav_todo.centery-10))
            
            pygame.draw.rect(screen, FALLOUT_DIM, btn_nav_calc); pygame.draw.rect(screen, FALLOUT_GREEN, btn_nav_calc, 2)
            screen.blit(f_m.render("NOTEN", True, FALLOUT_GREEN), (btn_nav_calc.centerx-30, btn_nav_calc.centery-10))
            
            pygame.draw.rect(screen, FALLOUT_DIM, btn_nav_upd); pygame.draw.rect(screen, ALERT_RED, btn_nav_upd, 2)
            screen.blit(f_m.render("UPDATE", True, ALERT_RED), (btn_nav_upd.centerx-35, btn_nav_upd.centery-10))

            # Klick Check
            if click_pos:
                if btn_nav_todo.collidepoint(click_pos): 
                    state = "TODO"
                    todos = fetch_data(TODO_URL) # Frisch laden beim Öffnen
                if btn_nav_calc.collidepoint(click_pos): state = "CALC"
                if btn_nav_upd.collidepoint(click_pos): state = "UPDATE"

        # 3. TO-DO SCREEN
        elif state == "TODO":
            screen.blit(f_l.render("AUFGABEN", True, FALLOUT_GREEN), (20, 20))
            
            # Liste
            y_off = 70
            for i, item in enumerate(todos[:6]): # Max 6 Items
                # Box zum Abhaken
                box = pygame.Rect(20, y_off, 440, 35)
                pygame.draw.rect(screen, FALLOUT_DIM, box, 1)
                screen.blit(f_m.render(item, True, WHITE), (30, y_off+5))
                
                if click_pos and box.collidepoint(click_pos):
                    del todos[i] # Lokal löschen
                    click_pos = None # Klick verbraucht
                y_off += 40
            
            # Home Button
            pygame.draw.rect(screen, FALLOUT_DIM, btn_home, 1)
            screen.blit(f_m.render("HOME", True, FALLOUT_GREEN), (btn_home.x+10, btn_home.y+10))
            
            if click_pos and btn_home.collidepoint(click_pos): state = "HOME"

        # 4. UPDATE SCREEN (Sicherheitsabfrage)
        elif state == "UPDATE":
            screen.fill((50, 0, 0)) # Roter Alarm Hintergrund
            
            msg = f_l.render("SYSTEM UPDATE?", True, WHITE)
            screen.blit(msg, (W//2 - msg.get_width()//2, 80))
            
            btn_yes = pygame.Rect(60, 180, 160, 80)
            btn_no  = pygame.Rect(260, 180, 160, 80)
            
            pygame.draw.rect(screen, FALLOUT_GREEN, btn_yes)
            screen.blit(f_l.render("JA!", True, BLACK), (btn_yes.centerx-20, btn_yes.centery-15))
            
            pygame.draw.rect(screen, ALERT_RED, btn_no)
            screen.blit(f_l.render("NEIN", True, BLACK), (btn_no.centerx-30, btn_no.centery-15))
            
            if click_pos:
                if btn_no.collidepoint(click_pos): state = "HOME"
                if btn_yes.collidepoint(click_pos):
                    # Download Animation
                    screen.fill(BLACK)
                    screen.blit(f_l.render("DOWNLOADING...", True, FALLOUT_GREEN), (100, 150))
                    pygame.display.flip()
                    try:
                        urllib.request.urlretrieve(UPDATE_URL, "/home/bot/robot/ui/main.py")
                        sys.exit() # Neustart durch start_bot.sh
                    except:
                        state = "HOME" # Falls Internet fehlt

        # 5. NOTEN RECHNER
        elif state == "CALC":
            screen.blit(f_l.render("NOTEN-RECHNER", True, FALLOUT_GREEN), (20, 20))
            
            # Anzeige Feld
            pygame.draw.rect(screen, FALLOUT_DIM, (20, 70, 200, 50))
            screen.blit(f_l.render(calc_inp, True, WHITE), (30, 80))
            
            # Ergebnis / Gesicht
            screen.blit(f_xl.render(calc_res, True, FALLOUT_GREEN), (250, 80))
            screen.blit(f_l.render(calc_face, True, FALLOUT_GREEN), (360, 90))
            
            # Nummernblock Buttons
            keys = [
                ('7', 20, 140), ('8', 90, 140), ('9', 160, 140),
                ('4', 20, 200), ('5', 90, 200), ('6', 160, 200),
                ('1', 20, 260), ('2', 90, 260), ('3', 160, 260),
                ('0', 90, 320), ('C', 20, 320), ('=', 160, 320)
            ]
            # Home Button
            pygame.draw.rect(screen, FALLOUT_DIM, btn_home, 1)
            screen.blit(f_m.render("HOME", True, FALLOUT_GREEN), (btn_home.x+10, btn_home.y+10))
            if click_pos and btn_home.collidepoint(click_pos): state = "HOME"
            
            # Rechner Logik
            for k, kx, ky in keys:
                r = pygame.Rect(kx, ky, 60, 50)
                # Zeichnen (einfach gehalten)
                pygame.draw.rect(screen, FALLOUT_DIM, r, 1)
                screen.blit(f_m.render(k, True, WHITE), (kx+20, ky+15))
                
                if click_pos and r.collidepoint(click_pos):
                    if k == 'C': 
                        calc_inp = ""; calc_res = ""; calc_face = "( -_-)"
                    elif k == '=':
                        # Simple Logik: Prozent von 100
                        try:
                            p = float(calc_inp)
                            note = 6 - (5 * p / 100)
                            calc_res = f"{note:.1f}"
                            if note < 2: calc_face = "(^o^)"
                            elif note > 4: calc_face = "(>_<)"
                            else: calc_face = "( -_-)"
                        except: calc_res = "ERR"
                    else:
                        if len(calc_inp) < 3: calc_inp += k

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
