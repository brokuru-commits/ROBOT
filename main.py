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
VERSION = "V 3.0"

# --- FARB-MODI (FALLOUT STYLE) ---
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

# --- QUOTES ---
QUOTES = ["LERNEN IST ZWECKLOS...", "WAS GIBT'S ZU ESSEN?", "SYSTEMS OPTIMAL.", "SCANNRE UMGEBUNG...", "RAD-LEVEL NORMAL."]
EMOJIS = ["( ^_^)","( o_o)","( O_O)","( -_-)","( ^.^)", "(⌐■_■)"]

# --- STUNDENPLAN (Identisch) ---
PLAN = [(7,30,8,0,"PAUSE"),(8,0,8,45,"1. STUNDE"),(8,45,8,50,"PAUSE"),(8,50,9,35,"2. STUNDE"),(9,35,9,55,"HOFPAUSE"),(9,55,10,40,"3. STUNDE"),(10,40,10,45,"PAUSE"),(10,45,11,30,"4. STUNDE"),(11,30,11,50,"ESSEN"),(11,50,12,35,"5. STUNDE"),(12,35,12,40,"PAUSE"),(12,40,13,25,"6. STUNDE"),(13,25,13,35,"PAUSE"),(13,35,14,20,"7. STUNDE"),(14,20,14,25,"PAUSE"),(14,25,15,10,"8. STUNDE"),(15,10,15,15,"PAUSE"),(15,15,16,0,"9. STUNDE"),(16,0,17,0,"ENDE")]

def get_status_data():
    now = datetime.now()
    cur = now.hour * 3600 + now.minute * 60 + now.second
    for (sh, sm, eh, em, label) in PLAN:
        start, end = sh * 3600 + sm * 60, eh * 3600 + em * 60
        if start <= cur < end:
            return label, f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d}", (cur-start)/(end-start), end-cur
    return "FREIZEIT", "", 0.0, 0

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    def get_f(s): 
        try: return pygame.font.Font(FONT_PATH, s)
        except: return pygame.font.SysFont("monospace", s, bold=True)

    f_xl = get_f(80); f_l = get_f(40); f_m = get_f(28); f_s = get_f(22); f_xs = get_f(14)
    
    # Hintergrund laden
    bg_img = None
    if os.path.exists(BG_PATH):
        bg_img = pygame.image.load(BG_PATH).convert()
        bg_img = pygame.transform.scale(bg_img, (W, H))

    state = "HOME"
    scan_x = 0
    emoji_timer = quote_timer = 0
    curr_emoji = EMOJIS[0]; curr_quote = QUOTES[0]

    while True:
        clock.tick(FPS)
        # --- FARB ROTATION (Alle 10 Minuten) ---
        color_idx = (int(time.time()) // 600) % len(COLOR_MODES)
        MAIN_COL = COLOR_MODES[color_idx]
        DIM_COL = (MAIN_COL[0]//5, MAIN_COL[1]//5, MAIN_COL[2]//5)

        click_pos = None
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN: click_pos = e.pos
            if e.type == pygame.FINGERDOWN: click_pos = (int(e.x * W), int(e.y * H))

        # --- RENDERING ---
        screen.fill(BLACK)
        if bg_img:
            screen.blit(bg_img, (0,0))
            # Color-Overlay für den Background-Look
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((DIM_COL[0], DIM_COL[1], DIM_COL[2], 120))
            screen.blit(overlay, (0,0))

        if state == "HOME":
            now = datetime.now()
            screen.blit(f_xl.render(now.strftime("%H:%M:%S"), True, MAIN_COL), (20, 10))
            
            # Ruhige Icons oben rechts
            icons = ["☢", "⚡", "📶"]
            for i, icon in enumerate(icons):
                alpha = 255 if (int(time.time()) + i) % 3 != 0 else 100 # Langsames Pulsieren
                txt = f_m.render(icon, True, MAIN_COL)
                txt.set_alpha(alpha)
                screen.blit(txt, (430 - i*35, 15))

            # Bot & Quote
            if time.time() - emoji_timer > 4.0:
                curr_emoji = random.choice(EMOJIS); emoji_timer = time.time()
            if time.time() - quote_timer > 8.0:
                curr_quote = random.choice(QUOTES); quote_timer = time.time()
            
            screen.blit(f_xs.render(curr_quote, True, WHITE), (W//2 - 60, 95))
            screen.blit(f_l.render(curr_emoji, True, MAIN_COL), (W//2 - 60, 115))

            # Stundenplan (GROSS & LESBAR)
            label, timespan, prog, remain = get_status_data()
            bar_rect = pygame.Rect(30, 175, 420, 55)
            pygame.draw.rect(screen, DIM_COL, bar_rect)
            pygame.draw.rect(screen, MAIN_COL, (30, 175, int(420 * prog), 55))
            
            # Schrift im Balken (Groß)
            txt_label = f_s.render(f"{label}", True, BLACK)
            screen.blit(txt_label, (40, 188))
            min, sec = divmod(int(remain), 60)
            screen.blit(f_s.render(f"{min:02d}:{sec:02d}", True, BLACK), (370, 188))

            # Langsame Scanline
            scan_x = (scan_x + 2) % W 
            pygame.draw.line(screen, MAIN_COL, (scan_x, 310), (scan_x + 30, 310), 2)

            # Buttons
            btn_calc = pygame.Rect(40, 245, 180, 55)
            btn_upd = pygame.Rect(260, 245, 180, 55)
            pygame.draw.rect(screen, DIM_COL, btn_calc); pygame.draw.rect(screen, MAIN_COL, btn_calc, 2)
            pygame.draw.rect(screen, DIM_COL, btn_upd); pygame.draw.rect(screen, MAIN_COL, btn_upd, 2)
            screen.blit(f_s.render("RECHNER", True, MAIN_COL), (75, 258))
            screen.blit(f_s.render("UPDATE", True, MAIN_COL), (300, 258))

            if click_pos:
                if btn_calc.collidepoint(click_pos): state = "CALC"
                if btn_upd.collidepoint(click_pos): pass # Update-Logik

        elif state == "CALC":
            screen.fill(BLACK)
            screen.blit(f_l.render("CALC MODE", True, MAIN_COL), (100, 100))
            if click_pos: state = "HOME"

        pygame.display.flip()

if __name__ == "__main__":
    main()
