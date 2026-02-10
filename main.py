#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, urllib.request, py_compile
from datetime import datetime, date
import pygame

# =========================
# SYSTEM CONFIG
# =========================
os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"

W, H = 480, 320
FPS = 30
VERSION = "V 3.7 DECIMAL"

# =========================
# PFADE
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

EMOJIS = [
    "( ^_^ )", "( o_o )", "( O_O )", 
    "( -_- )", "( ^.^ )", "[ 0_0 ]", 
    "( >_< )", "( $_$ )"
]

DEFAULT_QUOTES = ["SYSTEMS OPTIMAL.", "LERNEN...", "WARTE AUF EINGABE", "RAD-LEVEL NORMAL."]

# --- FERIEN (anpassen, falls sich Termine ändern) ---
HOLIDAYS = [
    ("Winterferien", date(2026, 2, 2), date(2026, 2, 6)),
    ("Osterferien", date(2026, 3, 30), date(2026, 4, 10)),
    ("Sommerferien", date(2026, 7, 2), date(2026, 8, 12)),
    ("Herbstferien", date(2026, 10, 19), date(2026, 10, 30)),
    ("Weihnachtsferien", date(2026, 12, 23), date(2027, 1, 1)),
]

# --- STUNDENPLAN ---
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
            time_str = f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d}"
            return label, time_str, (cur-start)/total, end-cur
    return "FREIZEIT", "", 0.0, 0

def get_next_holiday_data(today=None):
    if today is None:
        today = date.today()

    # erst prüfen, ob gerade Ferien sind
    for name, start, end in HOLIDAYS:
        if start <= today <= end:
            left = (end - today).days + 1
            return f"{name}: Noch {left} Tag(e)"

    # dann nächste zukünftige Ferien finden
    upcoming = [(name, start) for name, start, end in HOLIDAYS if start > today]
    if not upcoming:
        return "Keine Ferientermine hinterlegt"

    name, start = min(upcoming, key=lambda item: item[1])
    days_left = (start - today).days
    return f"Bis {name}: {days_left} Tag(e)"

def calc_grade_decimal(p_ist, p_max, school_type):
    """Berechnet die Note als Dezimalzahl (z.B. 2,4)."""
    if p_max <= 0: return "-"
    
    percent = p_ist / p_max
    
    # --- GRENZWERTE ---
    # Wo liegt die Note 4.0?
    # GYM: bei 50% (0.50)
    # RS:  bei 45% (0.45)
    limit_4 = 0.50 if school_type == "GYM" else 0.45

    grade = 6.0
    
    if percent == 1.0:
        grade = 1.0
    elif percent > limit_4:
        # Bereich Note 1 bis 4 (Oberhalb der Grenze)
        # Formel: Linear von 1.0 bis 4.0
        grade = 1 + 3 * ((1 - percent) / (1 - limit_4))
    else:
        # Bereich Note 4 bis 6 (Unterhalb der Grenze)
        # Formel: Linear von 4.0 bis 6.0
        grade = 4 + 2 * ((limit_4 - percent) / limit_4)
        
    # Begrenzen auf 1.0 bis 6.0
    if grade < 1: grade = 1.0
    if grade > 6: grade = 6.0
    
    # Formatieren: Eine Nachkommastelle, Punkt zu Komma
    return f"{grade:.1f}".replace('.', ',')

def safe_update():
    # ----------------------------------------------------
    # HIER DEINE GITHUB URL EINTRAGEN !!!
    url = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/main.py"
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
        try:
            surf = font.render("...", True, color)
            screen.blit(surf, pos)
        except: pass

# =========================
# MAIN LOOP
# =========================
def main():
    pygame.init()
    # Vollbild Modus
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    def get_f(s): 
        try: return pygame.font.Font(FONT_PATH, s)
        except: return pygame.font.SysFont("monospace", s, bold=True)

    f_xl = get_f(80); f_l = get_f(35); f_m = get_f(24); f_s = get_f(20); f_xs = get_f(14)
    
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

    # Buttons Setup
    num_btns = []
    for i in range(1, 10):
        x = 300 + ((i-1)%3)*55
        y = 75 + ((i-1)//3)*45
        num_btns.append((pygame.Rect(x, y, 50, 40), str(i)))
    
    num_btns.append((pygame.Rect(300, 210, 50, 40), "0"))
    btn_del = pygame.Rect(355, 210, 105, 40)
    btn_switch = pygame.Rect(20, 210, 200, 40)
    
    btn_calc = pygame.Rect(50, 250, 160, 45)
    btn_upd  = pygame.Rect(270, 250, 160, 45)
    btn_home = pygame.Rect(390, 10, 80, 35)

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
            draw_text_safe(screen, f_s, now.strftime("%d.%m.%Y"), WHITE, (22, 88), "topleft")
            
            for i, ico in enumerate(["☢", "⚡", "📶"]):
                col = MAIN_COL if int(time.time())%2==0 else DIM_COL
                draw_text_safe(screen, f_m, ico, col, (430-i*35, 15), "topleft")

            draw_text_safe(screen, f_xs, curr_quote, WHITE, (W//2, 95), "center")
            draw_text_safe(screen, f_l, curr_emoji, MAIN_COL, (W//2, 115), "center")

            label, timespan, prog, remain = get_status_data()
            holiday_info = get_next_holiday_data(now.date())
            pygame.draw.rect(screen, DIM_COL, (30, 175, 420, 50))
            pygame.draw.rect(screen, MAIN_COL, (30, 175, int(420 * prog), 50))
            
            draw_text_safe(screen, f_s, label, BLACK, (40, 188), "topleft")
            m, s = divmod(int(remain), 60)
            draw_text_safe(screen, f_s, f"{m:02d}:{s:02d}", BLACK, (370, 188), "topleft")
            draw_text_safe(screen, f_xs, holiday_info, WHITE, (W//2, 235), "center")

            pygame.draw.line(screen, MAIN_COL, (scan_line_x, 315), (scan_line_x+40, 315), 2)

            pygame.draw.rect(screen, DIM_COL, btn_calc); pygame.draw.rect(screen, MAIN_COL, btn_calc, 2)
            draw_text_safe(screen, f_s, "RECHNER", MAIN_COL, btn_calc.center, "center")
            
            pygame.draw.rect(screen, DIM_COL, btn_upd); pygame.draw.rect(screen, (255,50,50), btn_upd, 2)
            draw_text_safe(screen, f_s, "UPDATE", (255,50,50), btn_upd.center, "center")

            if click_pos:
                if btn_calc.collidepoint(click_pos): state = "CALC"
                if btn_upd.collidepoint(click_pos): state = "DO_UPDATE"

        elif state == "CALC":
            draw_text_safe(screen, f_l, "NOTEN RECHNER", MAIN_COL, (20, 15), "topleft")
            pygame.draw.rect(screen, DIM_COL, btn_home, 1)
            draw_text_safe(screen, f_s, "HOME", MAIN_COL, btn_home.center, "center")

            col_i = MAIN_COL if input_focus=="IST" else DIM_COL
            col_m = MAIN_COL if input_focus=="MAX" else DIM_COL
            
            r_i = pygame.Rect(20, 65, 230, 40); pygame.draw.rect(screen, col_i, r_i, 2)
            r_m = pygame.Rect(20, 135, 230, 40); pygame.draw.rect(screen, col_m, r_m, 2)
            
            draw_text_safe(screen, f_xs, "DEINE PUNKTE:", WHITE, (25, 50), "topleft")
            draw_text_safe(screen, f_l, val_ist, WHITE, (30, 68), "topleft")
            draw_text_safe(screen, f_xs, "MAX. PUNKTE:", WHITE, (25, 120), "topleft")
            draw_text_safe(screen, f_l, val_max, WHITE, (30, 138), "topleft")

            try:
                # Hier rufen wir die NEUE Dezimal-Funktion auf
                note = calc_grade_decimal(float(val_ist or 0), float(val_max or 0), school_mode)
                
                # Farbe Rot, wenn Note schlechter als 4,0
                is_bad = False
                try: 
                    if float(note.replace(',', '.')) > 4.0: is_bad = True
                except: pass
                
                c_res = (255, 50, 50) if is_bad else MAIN_COL
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
