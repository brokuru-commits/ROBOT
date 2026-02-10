#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, urllib.request, py_compile
from datetime import datetime
import pygame

# =========================
# CONFIG (TOUCH FIX)
# =========================
os.environ["SDL_VIDEODRIVER"] = "x11"

W, H = 480, 320
FPS = 25

# Farben
FALLOUT_GREEN = (50, 255, 50)
FALLOUT_DIM   = (10, 80, 10)
BLACK         = (0, 0, 0)
WHITE         = (255, 255, 255)
ALERT_RED     = (255, 50, 50)
BLUE_NEON     = (0, 200, 255)
PURPLE        = (140, 60, 180)

# Pfade
BASE_DIR = os.path.expanduser("~/robot/ui/assets")
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
BG_PATH   = os.path.join(BASE_DIR, "bg.png")

# GitHub Update
REPO_URL   = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/"
UPDATE_URL = REPO_URL + "main.py"

# --- DEIN STUNDENPLAN ---
PLAN = [
    (7, 30, 8, 0,  "ANKUNFT/PAUSE"),
    (8, 0,  8, 45, "1. STUNDE"),
    (8, 45, 8, 50, "PAUSE"),
    (8, 50, 9, 35, "2. STUNDE"),
    (9, 35, 9, 55, "HOFPAUSE"),
    (9, 55, 10, 40, "3. STUNDE"),
    (10, 40, 10, 45, "PAUSE"),
    (10, 45, 11, 30, "4. STUNDE"),
    (11, 30, 11, 50, "ESSENSPAUSE"),
    (11, 50, 12, 35, "5. STUNDE"),
    (12, 35, 12, 40, "PAUSE"),
    (12, 40, 13, 25, "6. STUNDE"),
    (13, 25, 13, 35, "PAUSE"),
    (13, 35, 14, 20, "7. STUNDE"),
    (14, 20, 14, 25, "PAUSE"),
    (14, 25, 15, 10, "8. STUNDE"),
    (15, 10, 15, 15, "PAUSE"),
    (15, 15, 16, 0,  "9. STUNDE"),
    (16, 0,  17, 0,  "FEIERABEND")
]

# --- HELFER ---
def get_temp_c():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read()) / 1000.0
    except: return 0.0

def get_status_data():
    now = datetime.now()
    cur = now.hour * 3600 + now.minute * 60 + now.second
    for (sh, sm, eh, em, label) in PLAN:
        start = sh * 3600 + sm * 60
        end   = eh * 3600 + em * 60
        if start <= cur < end:
            total = end - start
            passed = cur - start
            return label, f"{sh:02d}:{sm:02d} - {eh:02d}:{em:02d}", passed/total, end-cur
    return "FREIZEIT", "", 0.0, 0

def fmt_time(sec):
    m, s = divmod(int(sec), 60)
    return f"{m:02d}:{s:02d}"

def safe_update_self():
    this_file = os.path.abspath(__file__)
    new_file = this_file + ".new"
    try:
        urllib.request.urlretrieve(UPDATE_URL, new_file)
        py_compile.compile(new_file, doraise=True)
        os.replace(new_file, this_file)
        return True
    except:
        if os.path.exists(new_file): os.remove(new_file)
        return False

# --- MAIN ---
def main():
    pygame.init()
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    # Fonts
    def get_f(s): 
        try: return pygame.font.Font(FONT_PATH, s)
        except: return pygame.font.SysFont(None, s)

    f_xl = get_f(80); f_l = get_f(35); f_m = get_f(24); f_s = get_f(18)
    
    bg_img = None
    if os.path.exists(BG_PATH):
        bg_img = pygame.transform.scale(pygame.image.load(BG_PATH).convert(), (W, H))

    state = "BOOT"
    boot_start = time.time()
    
    # UI Buttons
    btn_calc = pygame.Rect(40, 240, 180, 60)
    btn_upd  = pygame.Rect(260, 240, 180, 60)
    btn_home = pygame.Rect(380, 10, 90, 40)

    while True:
        clock.tick(FPS)
        click_pos = None
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN: click_pos = e.pos
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        # Render Logic
        if state == "BOOT":
            screen.fill(BLACK)
            elapsed = time.time() - boot_start
            rnd_col = (random.randint(50, 255), 255, 50)
            txt = f_xl.render("HEUM-TEC", True, rnd_col)
            screen.blit(txt, (W//2 - txt.get_width()//2, H//2 - 60))
            pygame.draw.rect(screen, rnd_col, (40, H//2 + 20, int(min(1.0, elapsed/4.0)*400), 20))
            if elapsed > 4.0: state = "HOME"

        elif state == "HOME":
            if bg_img: screen.blit(bg_img, (0,0))
            else: screen.fill(BLACK)

            now = datetime.now()
            # Uhrzeit & Datum
            screen.blit(f_xl.render(now.strftime("%H:%M:%S"), True, FALLOUT_GREEN), (20, 10))
            screen.blit(f_m.render(now.strftime("%d.%m.%Y"), True, FALLOUT_GREEN), (25, 90))
            
            # Temp
            temp = get_temp_c()
            pygame.draw.circle(screen, FALLOUT_GREEN if temp < 60 else ALERT_RED, (440, 25), 6)

            # Stundenplan
            label, timespan, prog, remain = get_status_data()
            if label != "FREIZEIT":
                col = BLUE_NEON if "PAUSE" in label else FALLOUT_GREEN
                # Balken
                pygame.draw.rect(screen, FALLOUT_DIM, (30, 140, 420, 45))
                pygame.draw.rect(screen, col, (30, 140, int(420 * prog), 45))
                # Label & Zeitspanne
                screen.blit(f_m.render(f"{label} ({timespan})", True, WHITE), (40, 148))
                screen.blit(f_m.render(f"- {fmt_time(remain)}", True, WHITE), (360, 148))
            else:
                screen.blit(f_l.render("FREIZEIT", True, BLUE_NEON), (30, 140))

            # Buttons
            pygame.draw.rect(screen, FALLOUT_DIM, btn_calc); pygame.draw.rect(screen, FALLOUT_GREEN, btn_calc, 2)
            screen.blit(f_m.render("BEWERTUNG", True, FALLOUT_GREEN), (65, 258))
            
            pygame.draw.rect(screen, FALLOUT_DIM, btn_upd); pygame.draw.rect(screen, ALERT_RED, btn_upd, 2)
            screen.blit(f_m.render("UPDATE", True, ALERT_RED), (310, 258))

            if click_pos:
                if btn_calc.collidepoint(click_pos): state = "CALC"
                if btn_upd.collidepoint(click_pos): state = "UPDATE"

        elif state == "UPDATE":
            screen.fill((40, 0, 0))
            txt = f_l.render("JETZT UPDATEN?", True, WHITE)
            screen.blit(txt, (W//2 - txt.get_width()//2, 80))
            
            btn_yes = pygame.Rect(60, 180, 160, 70)
            btn_no  = pygame.Rect(260, 180, 160, 70)
            
            pygame.draw.rect(screen, FALLOUT_GREEN, btn_yes); screen.blit(f_m.render("JA", True, BLACK), (125, 202))
            pygame.draw.rect(screen, ALERT_RED, btn_no); screen.blit(f_m.render("NEIN", True, BLACK), (310, 202))
            
            if click_pos:
                if btn_no.collidepoint(click_pos): state = "HOME"
                if btn_yes.collidepoint(click_pos):
                    screen.fill(BLACK)
                    screen.blit(f_m.render("LADE GITHUB VERSION...", True, FALLOUT_GREEN), (100, 150))
                    pygame.display.flip()
                    if safe_update_self(): sys.exit()
                    else: state = "HOME"

        elif state == "CALC":
            if bg_img: screen.blit(bg_img, (0,0))
            else: screen.fill(BLACK)
            
            pygame.draw.rect(screen, FALLOUT_DIM, btn_home, 1)
            screen.blit(f_s.render("HOME", True, FALLOUT_GREEN), (395, 22))
            
            # Hier kannst du dein bestehendes Calc-Numpad einfügen oder einfach
            # den Platzhalter lassen. Zurück kommt man immer über HOME.
            screen.blit(f_l.render("NOTEN RECHNER", True, FALLOUT_GREEN), (20, 20))
            if click_pos and btn_home.collidepoint(click_pos): state = "HOME"

        pygame.display.flip()

if __name__ == "__main__":
    main()
