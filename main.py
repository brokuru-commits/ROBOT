#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, urllib.request, py_compile
from datetime import datetime
import pygame

# =========================
# SYSTEM CONFIG
# =========================
os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"

W, H = 480, 320
FPS = 30
VERSION = "V 3.4 SAFE"

# =========================
# PFADE (Sicherer Fix für Autostart)
# =========================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

FONT_PATH = os.path.join(ASSETS_DIR, "font.ttf")
BG_PATH   = os.path.join(ASSETS_DIR, "bg.png")
QUOTES_PATH = os.path.join(ASSETS_DIR, "quotes.txt")

# =========================
# DATEN
# =========================
COLOR_MODES = [
    (50, 255, 50),   # Green
    (255, 180, 0),   # Amber
    (0, 200, 255),   # Blue
    (255, 50, 50)    # Red
]

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --- SICHERE EMOJIS (Keine Sonderzeichen!) ---
# Wir nutzen nur Zeichen, die JEDE Schriftart kann.
EMOJIS = [
    "( ^_^ )", 
    "( o_o )", 
    "( O_O )", 
    "( -_- )", 
    "( ^.^ )", 
    "[ 0_0 ]", 
    "( >_< )",
    "( $_$ )"
]

DEFAULT_QUOTES = ["SYSTEMS OPTIMAL.", "LERNEN...", "WARTE AUF EINGABE", "RAD-LEVEL NORMAL."]

SCALE_GYM = [95, 80, 65, 50, 25, 0]
SCALE_RS  = [90, 75, 60, 45, 20, 0]

PLAN = [
    (7,30,8,0,"PAUSE"),(8,0,8,45,"1. STUNDE"),(8,45,8,50,"PAUSE"),
    (8,50,9,35,"2. STUNDE"),(9,35,9,55,"HOFPAUSE"),(9,55,10,40,"3. STUNDE"),
    (10,40,10,45,"PAUSE"),(10,45,11,30,"4. STUNDE"),(11,30,11,50,"ESSEN"),
    (11,50,12,35,"5. STUNDE"),(12,35,12,40,"PAUSE"),(12,40,13,25,"6. STUNDE"),
    (13,25,13,35,"PAUSE"),(13,35,14,20,"7. STUNDE"),(14,20,14,25,"PAUSE"),
    (14,25,15,10,"8. STUNDE"),(15,10,15,15,"PAUSE"),(15,15,16,0,"9. STUNDE"),
    (16,0,17,0,"ENDE")
]

# =========================
# HILFSFUNKTIONEN
# =========================

def load_quotes():
    q = []
    if os.path.exists(QUOTES_PATH):
        try:
            with open(QUOTES_PATH, "r", encoding="utf-8") as f:
                q = [line.strip() for line in f if line.strip()]
        except: pass
    return q if q else DEFAULT_QUOTES

def get_status_data():
    now = datetime.now()
    cur = now.hour * 3600 + now.minute * 60 + now.second
    for (sh, sm, eh, em, label) in PLAN:
        start = sh * 3600 + sm * 60
        end   = eh * 3600 + em * 60
        if start <= cur < end:
            total = max(1, end - start)
            return label, f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d}", (cur-start)/total, end-cur
    return "FREIZEIT", "", 0.0, 0

def calc_grade(p_ist, p_max, school_type):
    if p_max <= 0: return "-"
    perc = (p_ist / p_max) * 100
    scale = SCALE_GYM if school_type == "GYM" else SCALE_RS
    for i, threshold in enumerate(scale):
        if perc >= threshold: return str(i + 1)
    return "6"

def safe_update():
    # URL HIER EINTRAGEN!
    url = "https://raw.githubusercontent.com/DEIN_NAME/DEIN_REPO/main/main.py"
    try:
        req = urllib.request.urlopen(url, timeout=10)
        with open(__file__ + ".new", 'wb') as f: f.write(req.read())
        py_compile.compile(__file__ + ".new", doraise=True)
        os.replace(__file__ + ".new", os.path.abspath(__file__))
        return True
    except Exception as e:
        print(f"Update Fehler: {e}")
        return False

# --- NEUE FUNKTION: ABSTURZSICHERES TEXT-RENDERN ---
def draw_text_safe(screen, font, text, color, pos, align="center"):
    try:
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if align == "center":
            rect.center = pos
        elif align == "topleft":
            rect.topleft = pos
        screen.blit(surf, rect)
    except Exception as e:
        # Falls das Zeichen fehlt, malen wir einfach "..." statt abzustürzen
        print(f"Font Error: {e}")
        try:
            surf = font.render("...", True, color)
            screen.blit(surf, pos)
        except: pass

# =========================
# MAIN LOOP
# =========================
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    def get_f(s): 
        try: return pygame.font.Font(FONT_PATH, s)
        except: return pygame.font.SysFont("monospace", s, bold=True)

    f_xl = get_f(80); f_l = get_f(40); f_m = get_f(28); f_s = get_f(22); f_xs = get_f(14)
    
    bg_img = None
    if os.path.exists(BG_PATH):
        try: bg_img = pygame.transform.scale(pygame.image.load(BG_PATH).convert(), (W, H))
        except: pass

    state = "HOME"
    
    scan_line_x = 0
    quotes_list = load_quotes()
    curr_quote = random.choice(quotes_list)
    curr_emoji = random.choice(EMOJIS)
    timer_quote = time.time()
    timer_emoji = time.time()
    
    # Calc Variablen
    school_mode = "GYM"
    input_focus = "IST"
    val_ist = ""
    val_max = ""

    # Numpad
    num_btns = []
    for i in range(1, 10):
        x, y = 280 + ((i-1)%3)*60, 80 + ((i-1)//3)*50
        num_btns.append((pygame.Rect(x, y, 55, 45), str(i)))
    num_btns.append((pygame.Rect(280, 230, 55, 45), "0"))
    
    btn_del = pygame.Rect(340, 230, 115, 45)
    btn_switch = pygame.Rect(20, 230, 230, 45)
    
    btn_calc = pygame.Rect(40, 245, 180, 55)
    btn_upd  = pygame.Rect(260, 245, 180, 55)
    btn_home = pygame.Rect(380, 10, 90, 40)

    while True:
        dt = clock.tick(FPS)
        
        # Farbwechsel
        idx = (int(time.time()) // 600) % 4
        MAIN_COL = COLOR_MODES[idx]
        DIM_COL = (max(20, MAIN_COL[0]-150), max(
