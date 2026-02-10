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
VERSION = "V 3.5 BULLETPROOF"

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

# --- SICHERE EMOJIS ---
EMOJIS = [
    "( ^_^ )", "( o_o )", "( O_O )",
    "( -_- )", "( ^.^ )", "[ 0_0 ]",
    "( >_< )", "( $_$ )"
]

DEFAULT_QUOTES = ["SYSTEMS OPTIMAL.", "LERNEN...", "WARTE AUF EINGABE", "RAD-LEVEL NORMAL."]

SCALE_GYM = [95, 80, 65, 50, 25, 0]
SCALE_RS  = [90, 75, 60, 45, 20, 0]

# --- VERTIKALER STUNDENPLAN (Kopiersicher!) ---
PLAN = [
    (7, 30, 8, 0, "PAUSE"),
    (8, 0, 8, 45, "1. STUNDE"),
    (8, 45, 8, 50, "PAUSE"),
    (8, 50, 9, 35, "2. STUNDE"),
    (9, 35, 9, 55, "HOFPAUSE"),
    (9, 55, 10, 40, "3. STUNDE"),
    (10, 40, 10, 45, "PAUSE"),
    (10, 45, 11, 30, "4. STUNDE"),
    (11, 30, 11, 50, "ESSEN"),
    (11, 50, 12, 35, "5. STUNDE"),
    (12, 35, 12, 40, "PAUSE"),
    (12, 40, 13, 25, "6. STUNDE"),
    (13, 25, 13, 35, "PAUSE"),
    (13, 35, 14, 20, "7. STUNDE"),
    (14, 20, 14, 25, "PAUSE"),
    (14, 25, 15, 10, "8. STUNDE"),
    (15, 10, 15, 15, "PAUSE"),
    (15, 15, 16, 0, "9. STUNDE"),
    (16, 0, 17, 0, "ENDE")
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
            # Hier war der Fehler oft: Jetzt sicher formatiert
            time_str = f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d}"
            return label, time_str, (cur-start)/total, end-cur
    return "FREIZEIT", "", 0.0, 0

def calc_grade(p_ist, p_max, school_type):
    if p_max <= 0: return "-"
    perc = (p_ist / p_max) * 100
    scale = SCALE_GYM if school_type == "GYM" else SCALE_RS
    for i, threshold in enumerate(scale):
        if perc >= threshold: return str(i + 1)
    return "6"

def safe_update():
    # ----------------------------------------------------
    # HIER DEINE GITHUB URL EINTRAGEN !!!
    url = "https://raw.githubusercontent.com/DEIN_NAME/DEIN_REPO/main/main.py"
    # ----------------------------------------------------
    try:
        req = urllib.request.urlopen(url, timeout=10)
        with open(__file__ + ".new", 'wb') as f: f.write(req.read())
        py_compile.compile(__file__ + ".new", doraise=True)
        os.replace(__file__ + ".new", os.path.abspath(__file__))
        return True
    except Exception as e:
        print(f"Update Fehler: {e}")
        return False

def draw_text_safe(screen, font, text, color, pos, align="center"):
    try:
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if align == "center": rect.center = pos
        elif align == "topleft": rect.topleft = pos
        screen.blit(surf, rect)
    except:
        # Fallback bei Fehler
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

    # Numpad Setup
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
        idx = (int(time.time()) // 600) % 4
        MAIN_COL = COLOR_MODES[idx]
        DIM_COL = (max(20, MAIN_COL[0]-150), max(20, MAIN_COL[1]-150), max(20, MAIN_COL[2]-150))

        click_pos = None
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN: click_pos = e.pos
            if e.type == pygame.FINGERDOWN: click_pos = (int(e.x * W), int(e.y * H))

        if time.time() - timer_emoji > 4.0:
            curr_emoji = random.choice(EMOJIS); timer_emoji = time.time()
        if time.time() - timer_quote > 8.0:
            curr_quote = random.choice(quotes_list); timer_quote = time.time()

        scan_line_x = (scan_line_x + 3) % W

        screen.fill(BLACK)
        if bg_img:
            screen.blit(bg_img, (0,0))
            over = pygame.Surface((W,H), pygame.SRCALPHA)
            over.fill((*DIM_COL, 140))
            screen.blit(over, (0,0))

        if state == "HOME":
            now = datetime.now()
            draw_text_safe(screen, f_xl, now.strftime("%H:%M:%S"), MAIN_COL, (20, 10), "topleft")

            for i, ico in enumerate(["☢", "⚡", "📶"]):
                col = MAIN_COL if int(time.time())%2==0 else DIM_COL
                draw_text_safe(screen, f_m, ico, col, (430-i*35, 15), "topleft")

            draw_text_safe(screen, f_xs, curr_quote, WHITE, (W//2, 95), "center")
            draw_text_safe(screen, f_l, curr_emoji, MAIN_COL, (W//2, 115), "center")

            label, timespan, prog, remain = get_status_data()
            pygame.draw.rect(screen, DIM_COL, (30, 175, 420, 55))
            pygame.draw.rect(screen, MAIN_COL, (30, 175, int(420 * prog), 55))

            draw_text_safe(screen, f_s, label, BLACK, (40, 188), "topleft")
            m, s = divmod(int(remain), 60)
            draw_text_safe(screen, f_s, f"{m:02d}:{s:02d}", BLACK, (370, 188), "topleft")

            pygame.draw.line(screen, MAIN_COL, (scan_line_x, 315), (scan_line_x+40, 315), 2)

            pygame.draw.rect(screen, DIM_COL, btn_calc); pygame.draw.rect(screen, MAIN_COL, btn_calc, 2)
            draw_text_safe(screen, f_s, "RECHNER", MAIN_COL, (btn_calc.x+40, btn_calc.y+15), "topleft")

            pygame.draw.rect(screen, DIM_COL, btn_upd); pygame.draw.rect(screen, (255,50,50), btn_upd, 2)
            draw_text_safe(screen, f_s, "UPDATE", (255,50,50), (btn_upd.x+45, btn_upd.y+15), "topleft")

            if click_pos:
                if btn_calc.collidepoint(click_pos): state = "CALC"
                if btn_upd.collidepoint(click_pos): state = "DO_UPDATE"

        elif state == "CALC":
            draw_text_safe(screen, f_l, "NOTEN RECHNER", MAIN_COL, (20, 15), "topleft")
            pygame.draw.rect(screen, DIM_COL, btn_home, 1)
            draw_text_safe(screen, f_s, "HOME", MAIN_COL, (395, 20), "topleft")

            col_i = MAIN_COL if input_focus=="IST" else DIM_COL
            col_m = MAIN_COL if input_focus=="MAX" else DIM_COL

            r_i = pygame.Rect(20, 70, 230, 50); pygame.draw.rect(screen, col_i, r_i, 2)
            r_m = pygame.Rect(20, 150, 230, 50); pygame.draw.rect(screen, col_m, r_m, 2)

            draw_text_safe(screen, f_xs, "DEINE PUNKTE:", WHITE, (25, 52), "topleft")
            draw_text_safe(screen, f_l, val_ist, WHITE, (35, 75), "topleft")
            draw_text_safe(screen, f_xs, "MAX. PUNKTE:", WHITE, (25, 132), "topleft")
            draw_text_safe(screen, f_l, val_max, WHITE, (35, 155), "topleft")

            try:
                note = calc_grade(float(val_ist or 0), float(val_max or 0), school_mode)
                c_res = MAIN_COL if note in "123" else (255,50,50)
                draw_text_safe(screen, f_xl, note, c_res, (100, 160), "topleft")
            except: pass

            for rect, val in num_btns:
                pygame.draw.rect(screen, DIM_COL, rect); pygame.draw.rect(screen, MAIN_COL, rect, 1)
                draw_text_safe(screen, f_m, val, WHITE, rect.center, "center")

            pygame.draw.rect(screen, (200,50,50), btn_del)
            draw_text_safe(screen, f_m, "DEL", WHITE, btn_del.center, "center")

            pygame.draw.rect(screen, MAIN_COL, btn_switch, 2)
            draw_text_safe(screen, f_m, f"MODUS: {school_mode}", MAIN_COL, btn_switch.center, "center")

            if click_pos:
                if btn_home.collidepoint(click_pos): state = "HOME"
                if r_i.collidepoint(click_pos): input_focus = "IST"
                if r_m.collidepoint(click_pos): input_focus = "MAX"
                if btn_switch.collidepoint(click_pos): school_mode = "RS" if school_mode=="GYM" else "GYM"
                if btn_del.collidepoint(click_pos):
                    if input_focus=="IST": val_ist=val_ist[:-1]
                    else: val_max=val_max[:-1]
                for r, v in num_btns:
                    if r.collidepoint(click_pos):
                        if input_focus=="IST" and len(val_ist)<5: val_ist+=v
                        elif input_focus=="MAX" and len(val_max)<5: val_max+=v

        elif state == "DO_UPDATE":
            screen.fill(BLACK)
            draw_text_safe(screen, f_m, "LADE UPDATE...", MAIN_COL, (W//2, H//2), "center")
            pygame.display.flip()
            if safe_update():
                pygame.quit(); sys.exit()
            else: state = "HOME"

        pygame.display.flip()

if __name__ == "__main__":
    main()
