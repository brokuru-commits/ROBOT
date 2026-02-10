#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, urllib.request, py_compile
from datetime import datetime
import pygame

# =========================
# CONFIG
# =========================
os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"

W, H = 480, 320
FPS = 30
VERSION = "V 3.2"

# --- NOTENTABELLEN ---
SCALE_GYM = [95, 80, 65, 50, 25, 0]
SCALE_RS  = [90, 75, 60, 45, 20, 0]

# --- FARB-MODI (ROTATION ALLE 10 MIN) ---
COLOR_MODES = [
    (50, 255, 50),   # Classic Green
    (255, 180, 0),   # Amber
    (0, 200, 255),   # Vault Blue
    (255, 50, 50)    # Alert Red
]

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Pfade
BASE_DIR = os.path.expanduser("~/robot/ui/assets")
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
BG_PATH   = os.path.join(BASE_DIR, "bg.png")

# --- STUNDENPLAN ---
PLAN = [(7,30,8,0,"PAUSE"),(8,0,8,45,"1. STUNDE"),(8,45,8,50,"PAUSE"),(8,50,9,35,"2. STUNDE"),(9,35,9,55,"HOFPAUSE"),(9,55,10,40,"3. STUNDE"),(10,40,10,45,"PAUSE"),(10,45,11,30,"4. STUNDE"),(11,30,11,50,"ESSEN"),(11,50,12,35,"5. STUNDE"),(12,35,12,40,"PAUSE"),(12,40,13,25,"6. STUNDE"),(13,25,13,35,"PAUSE"),(13,35,14,20,"7. STUNDE"),(14,20,14,25,"PAUSE"),(14,25,15,10,"8. STUNDE"),(15,10,15,15,"PAUSE"),(15,15,16,0,"9. STUNDE"),(16,0,17,0,"ENDE")]

QUOTES = ["SYSTEMS OPTIMAL.", "LERNEN LÄUFT...", "WARTE AUF EINGABE", "RAD-LEVEL NORMAL.", "WAS GIBT'S NEUES?"]
EMOJIS = ["( ^_^)","( o_o)","( O_O)","( -_-)","( ^.^)", "(⌐■_■)"]

def get_status_data():
    now = datetime.now()
    cur = now.hour * 3600 + now.minute * 60 + now.second
    for (sh, sm, eh, em, label) in PLAN:
        start, end = sh * 3600 + sm * 60, eh * 3600 + em * 60
        if start <= cur < end:
            return label, f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d}", (cur-start)/(end-start), end-cur
    return "FREIZEIT", "", 0.0, 0

def calc_grade(p_ist, p_max, school_type):
    if p_max <= 0: return "-"
    perc = (p_ist / p_max) * 100
    scale = SCALE_GYM if school_type == "GYM" else SCALE_RS
    for i, threshold in enumerate(scale):
        if perc >= threshold: return str(i + 1)
    return "6"

def safe_update():
    # --- HIER DEINE GITHUB URL REINMACHEN ---
    url = "https://raw.githubusercontent.com/DEIN_GITHUB_NAME/DEIN_REPO/main/main.py" 
    try:
        req = urllib.request.urlopen(url, timeout=5)
        with open(__file__ + ".new", 'wb') as f:
            f.write(req.read())
        py_compile.compile(__file__ + ".new", doraise=True)
        os.replace(__file__ + ".new", os.path.abspath(__file__))
        return True
    except Exception as e:
        print(e)
        return False

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
    
    # Animations-Variablen
    scan_x = 0
    emoji_timer = quote_timer = 0
    curr_emoji = EMOJIS[0]; curr_quote = QUOTES[0]

    # Rechner Variablen
    school_mode = "GYM"
    input_focus = "IST"
    val_ist = ""
    val_max = ""

    # Numpad Positionen
    num_btns = []
    for i in range(1, 10):
        num_btns.append((pygame.Rect(280 + ((i-1)%3)*60, 80 + ((i-1)//3)*50, 55, 45), str(i)))
    num_btns.append((pygame.Rect(280, 230, 55, 45), "0"))
    btn_del = pygame.Rect(340, 230, 115, 45)
    btn_switch = pygame.Rect(20, 230, 230, 45)

    while True:
        clock.tick(FPS)
        
        # Farb-Rotation
        color_idx = (int(time.time()) // 600) % len(COLOR_MODES)
        MAIN_COL = COLOR_MODES[color_idx]
        DIM_COL = (MAIN_COL[0]//5, MAIN_COL[1]//5, MAIN_COL[2]//5)

        # Event Loop (Button Fix)
        click_pos = None
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN: click_pos = e.pos
            if e.type == pygame.FINGERDOWN: click_pos = (int(e.x * W), int(e.y * H))

        screen.fill(BLACK)
        if bg_img:
            screen.blit(bg_img, (0,0))
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((DIM_COL[0], DIM_COL[1], DIM_COL[2], 120))
            screen.blit(overlay, (0,0))

        if state == "HOME":
            now = datetime.now()
            screen.blit(f_xl.render(now.strftime("%H:%M:%S"), True, MAIN_COL), (20, 10))
            
            # Icons
            for i, icon in enumerate(["☢", "⚡", "📶"]):
                screen.blit(f_m.render(icon, True, MAIN_COL), (430 - i*35, 15))

            # Bot Face
            if time.time() - emoji_timer > 4.0: curr_emoji = random.choice(EMOJIS); emoji_timer = time.time()
            if time.time() - quote_timer > 8.0: curr_quote = random.choice(QUOTES); quote_timer = time.time()
            screen.blit(f_xs.render(curr_quote, True, WHITE), (W//2 - 60, 95))
            screen.blit(f_l.render(curr_emoji, True, MAIN_COL), (W//2 - 60, 115))

            # Stundenplan
            label, timespan, prog, remain = get_status_data()
            pygame.draw.rect(screen, DIM_COL, (30, 175, 420, 55))
            pygame.draw.rect(screen, MAIN_COL, (30, 175, int(420 * prog), 55))
            screen.blit(f_s.render(label, True, BLACK), (40, 188))
            m, s = divmod(int(remain), 60)
            screen.blit(f_s.render(f"{m:02d}:{s:02d}", True, BLACK), (370, 188))

            # Scanline
            scan_x = (scan_x + 3) % W 
            pygame.draw.line(screen, MAIN_COL, (scan_x, 312), (scan_x + 40, 312), 2)

            # Buttons
            btn_calc = pygame.Rect(40, 245, 180, 55)
            btn_upd = pygame.Rect(260, 245, 180, 55)
            
            # Rechner Button
            pygame.draw.rect(screen, DIM_COL, btn_calc); pygame.draw.rect(screen, MAIN_COL, btn_calc, 2)
            screen.blit(f_s.render("RECHNER", True, MAIN_COL), (75, 258))
            
            # Update Button
            pygame.draw.rect(screen, DIM_COL, btn_upd); pygame.draw.rect(screen, (255,50,50), btn_upd, 2)
            screen.blit(f_s.render("UPDATE", True, (255,50,50)), (300, 258))

            if click_pos:
                if btn_calc.collidepoint(click_pos): state = "CALC"
                if btn_upd.collidepoint(click_pos): state = "DO_UPDATE"

        elif state == "CALC":
            # Header
            screen.blit(f_l.render("NOTEN RECHNER", True, MAIN_COL), (20, 15))
            btn_home = pygame.Rect(380, 10, 90, 40)
            pygame.draw.rect(screen, DIM_COL, btn_home, 1)
            screen.blit(f_s.render("HOME", True, MAIN_COL), (395, 20))

            # Eingabefelder
            rect_ist = pygame.Rect(20, 70, 230, 50)
            rect_max = pygame.Rect(20, 150, 230, 50)
            
            # Aktives Feld Highlight
            col_ist = MAIN_COL if input_focus == "IST" else DIM_COL
            col_max = MAIN_COL if input_focus == "MAX" else DIM_COL
            
            pygame.draw.rect(screen, col_ist, rect_ist, 2)
            pygame.draw.rect(screen, col_max, rect_max, 2)
            
            screen.blit(f_xs.render("DEINE PUNKTE:", True, WHITE), (25, 52))
            screen.blit(f_l.render(val_ist, True, WHITE), (35, 75))
            
            screen.blit(f_xs.render("MAX. PUNKTE:", True, WHITE), (25, 132))
            screen.blit(f_l.render(val_max, True, WHITE), (35, 155))

            # Ergebnis Note
            try:
                note = calc_grade(float(val_ist or 0), float(val_max or 0), school_mode)
                res_col = MAIN_COL if note in "123" else (255, 50, 50)
                screen.blit(f_xl.render(note, True, res_col), (100, 160)) # Note Groß in der Mitte
            except: pass

            # Buttons zeichnen
            for rect, val in num_btns:
                pygame.draw.rect(screen, DIM_COL, rect)
                pygame.draw.rect(screen, MAIN_COL, rect, 1)
                screen.blit(f_m.render(val, True, WHITE), (rect.x+20, rect.y+10))
            
            pygame.draw.rect(screen, (255,50,50), btn_del)
            screen.blit(f_m.render("DEL", True, WHITE), (btn_del.x+35, btn_del.y+10))

            pygame.draw.rect(screen, MAIN_COL, btn_switch, 2)
            screen.blit(f_m.render(f"MODUS: {school_mode}", True, MAIN_COL), (btn_switch.x+40, btn_switch.y+10))

            # Logik
            if click_pos:
                if btn_home.collidepoint(click_pos): state = "HOME"
                if rect_ist.collidepoint(click_pos): input_focus = "IST"
                if rect_max.collidepoint(click_pos): input_focus = "MAX"
                if btn_switch.collidepoint(click_pos): 
                    school_mode = "RS" if school_mode == "GYM" else "GYM"
                if btn_del.collidepoint(click_pos):
                    if input_focus == "IST": val_ist = val_ist[:-1]
                    else: val_max = val_max[:-1]
                for rect, val in num_btns:
                    if rect.collidepoint(click_pos):
                        if input_focus == "IST": val_ist += val
                        else: val_max += val

        elif state == "DO_UPDATE":
            screen.fill(BLACK)
            screen.blit(f_m.render("LADE UPDATE VOM SERVER...", True, MAIN_COL), (40, 140))
            pygame.display.flip()
            if safe_update():
                pygame.quit()
                sys.exit() # Neustart via Skript
            else:
                state = "HOME"

        pygame.display.flip()

if __name__ == "__main__":
    main()
