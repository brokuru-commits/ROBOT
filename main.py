#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, urllib.request, py_compile
from datetime import datetime
import pygame

# =========================
# CONFIG (TOUCH & DISPLAY)
# =========================
os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"

W, H = 480, 320
FPS = 30
VERSION = "V 3.1"

# --- FARB-MODI (ROTATION ALLE 10 MIN) ---
COLOR_MODES = [
    (50, 255, 50),   # Classic Green
    (255, 180, 0),   # Amber (New Vegas)
    (0, 200, 255),   # Vault-Tec Blue
    (255, 50, 50)    # Alert Red
]

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Pfade
BASE_DIR = os.path.expanduser("~/robot/ui/assets")
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
BG_PATH   = os.path.join(BASE_DIR, "bg.png")

# --- QUOTES & EMOJIS ---
QUOTES = ["SYSTEMS OPTIMAL.", "LERNEN LÄUFT...", "WARTE AUF EINGABE", "RAD-LEVEL NORMAL.", "WAS GIBT'S NEUES?"]
EMOJIS = ["( ^_^)","( o_o)","( O_O)","( -_-)","( ^.^)", "(⌐■_■)"]

# --- STUNDENPLAN ---
PLAN = [(7,30,8,0,"PAUSE"),(8,0,8,45,"1. STUNDE"),(8,45,8,50,"PAUSE"),(8,50,9,35,"2. STUNDE"),(9,35,9,55,"HOFPAUSE"),(9,55,10,40,"3. STUNDE"),(10,40,10,45,"PAUSE"),(10,45,11,30,"4. STUNDE"),(11,30,11,50,"ESSEN"),(11,50,12,35,"5. STUNDE"),(12,35,12,40,"PAUSE"),(12,40,13,25,"6. STUNDE"),(13,25,13,35,"PAUSE"),(13,35,14,20,"7. STUNDE"),(14,20,14,25,"PAUSE"),(14,25,15,10,"8. STUNDE"),(15,10,15,15,"PAUSE"),(15,15,16,0,"9. STUNDE"),(16,0,17,0,"ENDE")]

def get_status_data():
    now = datetime.now()
    cur = now.hour * 3600 + now.minute * 60 + now.second
    for (sh, sm, eh, em, label) in PLAN:
        start, end = sh * 3600 + sm * 60, eh * 3600 + em * 60
        if start <= cur < end:
            return label, f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d}", (cur-start)/(end-start), end-cur
    return "FREIZEIT", "", 0.0, 0

def safe_update():
    """Lädt den neuen Code und beendet das Programm für den Auto-Reload."""
    this_file = os.path.abspath(__file__)
    new_file = this_file + ".new"
    url = "https://raw.githubusercontent.com/dein-nutzername/dein-repo/main/main.py" # DEINE URL EINTRAGEN
    try:
        req = urllib.request.urlopen(url, timeout=5)
        with open(new_file, 'wb') as f:
            f.write(req.read())
        # Syntax-Check
        py_compile.compile(new_file, doraise=True)
        os.replace(new_file, this_file)
        return True
    except Exception as e:
        print(f"Update Error: {e}")
        return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    def get_f(s): 
        try: return pygame.font.Font(FONT_PATH, s)
        except: return pygame.font.SysFont("monospace", s, bold=True)

    f_xl = get_f(80); f_l = get_f(40); f_m = get_f(28); f_s = get_f(24); f_xs = get_f(14)
    
    bg_img = None
    if os.path.exists(BG_PATH):
        try:
            bg_img = pygame.image.load(BG_PATH).convert()
            bg_img = pygame.transform.scale(bg_img, (W, H))
        except: pass

    state = "HOME"
    scan_x = 0
    emoji_timer = quote_timer = 0
    curr_emoji = EMOJIS[0]; curr_quote = QUOTES[0]

    while True:
        clock.tick(FPS)
        # Farbwechsel alle 10 Min (600 Sek)
        color_idx = (int(time.time()) // 600) % len(COLOR_MODES)
        MAIN_COL = COLOR_MODES[color_idx]
        DIM_COL = (MAIN_COL[0]//5, MAIN_COL[1]//5, MAIN_COL[2]//5)

        click_pos = None
        for e in pygame.event.get():
            if e.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                click_pos = getattr(e, 'pos', None) or (int(e.x * W), int(e.y * H))

        screen.fill(BLACK)
        if bg_img:
            screen.blit(bg_img, (0,0))
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((DIM_COL[0], DIM_COL[1], DIM_COL[2], 140))
            screen.blit(overlay, (0,0))

        if state == "HOME":
            now = datetime.now()
            # Uhrzeit
            screen.blit(f_xl.render(now.strftime("%H:%M:%S"), True, MAIN_COL), (20, 10))
            
            # Icons (ruhig)
            for i, icon in enumerate(["☢", "⚡", "📶"]):
                screen.blit(f_m.render(icon, True, MAIN_COL), (430 - i*35, 15))

            # Bot & Zitat
            if time.time() - emoji_timer > 4.0:
                curr_emoji = random.choice(EMOJIS); emoji_timer = time.time()
            if time.time() - quote_timer > 8.0:
                curr_quote = random.choice(QUOTES); quote_timer = time.time()
            
            screen.blit(f_xs.render(curr_quote, True, WHITE), (W//2 - 60, 90))
            screen.blit(f_l.render(curr_emoji, True, MAIN_COL), (W//2 - 60, 110))

            # --- STUNDENPLAN BALKEN ---
            label, timespan, prog, remain = get_status_data()
            bar_rect = pygame.Rect(30, 175, 420, 55)
            pygame.draw.rect(screen, DIM_COL, bar_rect)
            pygame.draw.rect(screen, MAIN_COL, (30, 175, int(420 * prog), 55))
            
            # Schrift im Balken (Schwarz, Groß)
            screen.blit(f_s.render(label, True, BLACK), (40, 187))
            m, s = divmod(int(remain), 60)
            screen.blit(f_s.render(f"{m:02d}:{s:02d}", True, BLACK), (375, 187))

            # Scanline
            scan_x = (scan_x + 2) % W 
            pygame.draw.line(screen, MAIN_COL, (scan_x, 312), (scan_x + 40, 312), 2)

            # Buttons
            btn_calc = pygame.Rect(40, 245, 180, 55)
            btn_upd = pygame.Rect(260, 245, 180, 55)
            for b, t, c in [(btn_calc, "RECHNER", MAIN_COL), (btn_upd, "UPDATE", ALERT_RED)]:
                pygame.draw.rect(screen, DIM_COL, b)
                pygame.draw.rect(screen, c, b, 2)
                screen.blit(f_s.render(t, True, c), (b.x+35, b.y+12))

            if click_pos:
                if btn_calc.collidepoint(click_pos): state = "CALC"
                if btn_upd.collidepoint(click_pos): state = "DO_UPDATE"

        elif state == "DO_UPDATE":
            screen.fill(BLACK)
            screen.blit(f_m.render("PRÜFE AUF UPDATES...", True, WHITE), (80, 140))
            pygame.display.flip()
            if safe_update():
                pygame.quit()
                sys.exit() # Bash-Skript startet es neu
            else:
                state = "HOME"

        elif state == "CALC":
            # Platzhalter für deinen Calc-Modus
            screen.fill(BLACK)
            screen.blit(f_m.render("RECHNER (BACK MIT KLICK)", True, MAIN_COL), (50, 140))
            if click_pos: state = "HOME"

        pygame.display.flip()

if __name__ == "__main__":
    main()
