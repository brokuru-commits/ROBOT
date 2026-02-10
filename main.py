#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, urllib.request, py_compile
from datetime import datetime
import pygame

# =========================
# TOUCH & DISPLAY FIX
# =========================
os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"

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
BG_PATH   = os.path.join(BASE_DIR, "bg.png")

# --- STUNDENPLAN ---
PLAN = [
    (7, 30, 8, 0,  "ANKUNFT/PAUSE"), (8, 0, 8, 45, "1. STUNDE"),
    (8, 45, 8, 50, "PAUSE"), (8, 50, 9, 35, "2. STUNDE"),
    (9, 35, 9, 55, "HOFPAUSE"), (9, 55, 10, 40, "3. STUNDE"),
    (10, 40, 10, 45, "PAUSE"), (10, 45, 11, 30, "4. STUNDE"),
    (11, 30, 11, 50, "ESSENSPAUSE"), (11, 50, 12, 35, "5. STUNDE"),
    (12, 35, 12, 40, "PAUSE"), (12, 40, 13, 25, "6. STUNDE"),
    (13, 25, 13, 35, "PAUSE"), (13, 35, 14, 20, "7. STUNDE"),
    (14, 20, 14, 25, "PAUSE"), (14, 25, 15, 10, "8. STUNDE"),
    (15, 10, 15, 15, "PAUSE"), (15, 15, 16, 0,  "9. STUNDE"),
    (16, 0, 17, 0, "FEIERABEND")
]

def get_temp_c():
    try:
        # Wir lesen nur, wenn die Datei existiert, ohne zu blockieren
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
            total = max(1, end - start)
            passed = cur - start
            return label, f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d}", passed/total, end-cur
    return "FREIZEIT", "", 0.0, 0

def fmt_time(sec):
    m, s = divmod(int(sec), 60)
    return f"{m:02d}:{s:02d}"

def safe_update():
    # Update mit hartem Timeout, damit nichts einfriert
    this_file = os.path.abspath(__file__)
    new_file = this_file + ".new"
    url = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/main.py"
    try:
        req = urllib.request.urlopen(url, timeout=1.5)
        with open(new_file, 'wb') as f:
            f.write(req.read())
        py_compile.compile(new_file, doraise=True)
        os.replace(new_file, this_file)
        return True
    except:
        return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
    pygame.mouse.set_visible(False) 
    clock = pygame.time.Clock()

    def get_f(s): 
        try: return pygame.font.Font(FONT_PATH, s)
        except: return pygame.font.SysFont(None, s)

    f_xl = get_f(80); f_l = get_f(35); f_m = get_f(24); f_s = get_f(18)
    
    bg_img = None
    if os.path.exists(BG_PATH):
        try: bg_img = pygame.transform.scale(pygame.image.load(BG_PATH).convert(), (W, H))
        except: pass

    state = "BOOT"
    boot_start = time.time()
    
    btn_calc = pygame.Rect(40, 240, 180, 60)
    btn_upd  = pygame.Rect(260, 240, 180, 60)
    btn_home = pygame.Rect(380, 10, 90, 40)

    while True:
        # WICHTIG: Die Uhr darf nicht hängen bleiben
        dt = clock.tick(FPS) 
        click_pos = None
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                click_pos = e.pos
            if e.type == pygame.FINGERDOWN:
                click_pos = (int(e.x * W), int(e.y * H))

        # --- RENDERING ---
        if state == "BOOT":
            screen.fill(BLACK)
            elapsed = time.time() - boot_start
            txt = f_xl.render("HEUM-TEC", True, FALLOUT_GREEN)
            screen.blit(txt, (W//2 - txt.get_width()//2, H//2 - 60))
            pygame.draw.rect(screen, FALLOUT_GREEN, (40, H//2 + 20, int(min(1.0, elapsed/4.0)*400), 20))
            if elapsed > 4.0: state = "HOME"

        elif state == "HOME":
            if bg_img: screen.blit(bg_img, (0,0))
            else: screen.fill(BLACK)

            now = datetime.now()
            screen.blit(f_xl.render(now.strftime("%H:%M:%S"), True, FALLOUT_GREEN), (20, 10))
            screen.blit(f_m.render(now.strftime("%d.%m.%Y"), True, FALLOUT_GREEN), (25, 90))
            
            label, timespan, prog, remain = get_status_data()
            if label != "FREIZEIT":
                col = BLUE_NEON if "PAUSE" in label else FALLOUT_GREEN
                pygame.draw.rect(screen, FALLOUT_DIM, (30, 140, 420, 45))
                pygame.draw.rect(screen, col, (30, 140, int(420 * prog), 45))
                screen.blit(f_m.render(f"{label} ({timespan})", True, WHITE), (40, 148))
                screen.blit(f_m.render(f"- {fmt_time(remain)}", True, WHITE), (350, 148))
            else:
                screen.blit(f_l.render("FREIZEIT", True, BLUE_NEON), (30, 140))

            # Buttons
            pygame.draw.rect(screen, FALLOUT_DIM, btn_calc); pygame.draw.rect(screen, FALLOUT_GREEN, btn_calc, 2)
            screen.blit(f_m.render("BEWERTUNG", True, FALLOUT_GREEN), (65, 258))
            
            pygame.draw.rect(screen, FALLOUT_DIM, btn_upd); pygame.draw.rect(screen, ALERT_RED, btn_upd, 2)
            screen.blit(f_m.render("UPDATE", True, ALERT_RED), (310, 258))

            if click_pos:
                if btn_calc.collidepoint(click_pos): state = "CALC"
                elif btn_upd.collidepoint(click_pos): state = "UPDATE"

        elif state == "UPDATE":
            screen.fill((40, 0, 0))
            txt = f_l.render("JETZT UPDATEN?", True, WHITE)
            screen.blit(txt, (W//2 - txt.get_width()//2, 80))
            
            btn_yes = pygame.Rect(60, 180, 160, 70); btn_no = pygame.Rect(260, 180, 160, 70)
            pygame.draw.rect(screen, FALLOUT_GREEN, btn_yes); screen.blit(f_m.render("JA", True, BLACK), (125, 202))
            pygame.draw.rect(screen, ALERT_RED, btn_no); screen.blit(f_m.render("NEIN", True, BLACK), (310, 202))
            
            if click_pos:
                if btn_no.collidepoint(click_pos): state = "HOME"
                elif btn_yes.collidepoint(click_pos):
                    screen.fill(BLACK)
                    screen.blit(f_m.render("LADE...", True, FALLOUT_GREEN), (200, 150))
                    pygame.display.flip()
                    if safe_update(): sys.exit()
                    else: state = "HOME"

        elif state == "CALC":
            screen.fill(BLACK)
            pygame.draw.rect(screen, FALLOUT_DIM, btn_home, 1)
            screen.blit(f_s.render("HOME", True, FALLOUT_GREEN), (395, 22))
            screen.blit(f_l.render("NOTEN RECHNER", True, FALLOUT_GREEN), (20, 20))
            if click_pos and btn_home.collidepoint(click_pos): state = "HOME"

        pygame.display.flip()

if __name__ == "__main__":
    main()
