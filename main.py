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
VERSION = "V 2.9"

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

# --- QUOTES ---
QUOTES = [
    "LERNEN IST ZWECKLOS...", "WAS GIBT'S ZU ESSEN?", "BIN ICH EIN GUTER BOT?",
    "SYSTEMS OPTIMAL.", "SCANNRE UMGEBUNG...", "NOCH 5 MINUTEN?", 
    "AHA, INTERESSANT!", "LÄCHELN NICHT VERGESSEN!", "RAD-LEVEL NORMAL."
]

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

EMOJIS = ["( ^_^)","( o_o)","( O_O)","( -_-)","( ^.^)", "( >_<)", "(⌐■_■)"]

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

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    def get_f(s): 
        try: return pygame.font.Font(FONT_PATH, s)
        except: return pygame.font.SysFont("monospace", s, bold=True)

    f_xl = get_f(80); f_l = get_f(35); f_m = get_f(24); f_s = get_f(15); f_xs = get_f(12)
    f_emoji = pygame.font.SysFont("monospace", 45, bold=True)

    state = "HOME"
    
    # Animation Variablen
    scan_line_x = 0
    quote_timer = 0
    current_quote = random.choice(QUOTES)
    emoji_timer = 0
    current_emoji = random.choice(EMOJIS)
    
    # Buttons Home
    btn_calc_nav = pygame.Rect(40, 240, 180, 60)
    btn_upd_nav  = pygame.Rect(260, 240, 180, 60)

    while True:
        clock.tick(FPS)
        click_pos = None
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN: click_pos = e.pos
            if e.type == pygame.FINGERDOWN: click_pos = (int(e.x * W), int(e.y * H))

        screen.fill(BLACK)

        if state == "HOME":
            now = datetime.now()
            
            # --- HEADER ---
            screen.blit(f_xl.render(now.strftime("%H:%M:%S"), True, FALLOUT_GREEN), (20, 10))
            
            # Dynamische Icons oben rechts
            icon_y = 15
            for i in range(3):
                col = FALLOUT_GREEN if random.random() > 0.1 else FALLOUT_DIM
                pygame.draw.rect(screen, col, (420 - (i*25), icon_y, 15, 15), 2)
                if random.random() > 0.5: pygame.draw.rect(screen, col, (423 - (i*25), icon_y+3, 9, 9))
            screen.blit(f_xs.render("WIFI: OK  RAD: 0.02", True, FALLOUT_DIM), (325, 35))

            # --- BOT & QUOTE ---
            if time.time() - emoji_timer > 2.5:
                current_emoji = random.choice(EMOJIS)
                emoji_timer = time.time()
            if time.time() - quote_timer > 6.0:
                current_quote = random.choice(QUOTES)
                quote_timer = time.time()
            
            # Sprechblase (Andeutung)
            q_surf = f_xs.render(current_quote, True, WHITE)
            screen.blit(q_surf, (W//2 - q_surf.get_width()//2, 85))
            e_surf = f_emoji.render(current_emoji, True, FALLOUT_GREEN)
            screen.blit(e_surf, (W//2 - e_surf.get_width()//2, 105))

            # --- STUNDENPLAN ---
            label, timespan, prog, remain = get_status_data()
            bar_rect = pygame.Rect(30, 165, 420, 45)
            pygame.draw.rect(screen, FALLOUT_DIM, bar_rect)
            
            col = BLUE_NEON if "PAUSE" in label else FALLOUT_GREEN
            pygame.draw.rect(screen, col, (30, 165, int(420 * prog), 45))
            
            # Schrift im Balken: Schwarz für beste Lesbarkeit
            label_txt = f_s.render(f"{label} ({timespan})", True, BLACK)
            screen.blit(label_txt, (40, 178))
            
            # Countdown
            min, sec = divmod(int(remain), 60)
            count_txt = f_s.render(f"{min:02d}:{sec:02d}", True, BLACK)
            screen.blit(count_txt, (390, 178))

            # --- SCANLINE EFFEKT UNTEN ---
            scan_line_x = (scan_line_x + 8) % W
            pygame.draw.line(screen, (0, 100, 0), (scan_line_x, 310), (scan_line_x + 20, 310), 3)
            pygame.draw.rect(screen, FALLOUT_DIM, (0, 315, W, 5)) # Bodenlinie

            # --- NAV BUTTONS ---
            pygame.draw.rect(screen, FALLOUT_DIM, btn_calc_nav); pygame.draw.rect(screen, FALLOUT_GREEN, btn_calc_nav, 2)
            screen.blit(f_m.render("RECHNER", True, FALLOUT_GREEN), (75, 258))
            
            pygame.draw.rect(screen, FALLOUT_DIM, btn_upd_nav); pygame.draw.rect(screen, ALERT_RED, btn_upd_nav, 2)
            screen.blit(f_m.render("UPDATE", True, ALERT_RED), (310, 258))

            if click_pos:
                if btn_calc_nav.collidepoint(click_pos): state = "CALC"
                if btn_upd_nav.collidepoint(click_pos): # Update Logik hierher...
                    pass 

        elif state == "CALC":
            # (Hier kommt dein funktionierender Calc-Code aus V 2.8 rein)
            screen.blit(f_m.render("RECHNER AKTIV - BACK ZU HOME", True, WHITE), (50, 100))
            if click_pos: state = "HOME"

        pygame.display.flip()

if __name__ == "__main__":
    main()
