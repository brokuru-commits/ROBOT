#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, math, random
from datetime import datetime
import pygame

# ============================================================
# FIXED SPECS (640x480 GOLD-STANDARD)
# ============================================================
W, H = 640, 480
FPS = 25

# FARBEN
GREEN      = (80, 255, 80)
GREEN_SOFT = (120, 255, 120)
DIM_GREEN  = (18, 55, 18)
BLUE       = (0, 190, 255)
DIM_BLUE   = (0, 50, 100)
RED        = (255, 50, 50)
WARN       = (255, 180, 60)
ORANGE     = (255, 150, 50)
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
GRAY       = (100, 100, 100)

# PFADE
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
BG_PATH   = os.path.join(ASSET_DIR, "bg.png")
FONT_PATH = os.path.join(ASSET_DIR, "Monofonto.ttf")
TXT_PATH  = os.path.join(ASSET_DIR, "emotions.txt")
ART_PATH  = os.path.join(ASSET_DIR, "art.txt") 

# DEBUG OUTPUT
print("--- STARTE CRITL OS V2.1 ---")
print(f"Checke Asset-Ordner: {ASSET_DIR}")

CRITL_PATHS = {
    1: os.path.join(ASSET_DIR, "1.png"), 
    2: os.path.join(ASSET_DIR, "2.png"),
    3: os.path.join(ASSET_DIR, "3.png"), 
    4: os.path.join(ASSET_DIR, "4.png")
}

# ============================================================
# STUNDENPLAN
# ============================================================
PLAN_RAW = [
    ("07:30","08:00","VORBEREITUNG"), ("08:00","08:45","UNTERRICHT"), ("08:45","08:50","PAUSE"),
    ("08:50","09:35","UNTERRICHT"), ("09:35","09:55","PAUSE"), ("09:55","10:40","UNTERRICHT"),
    ("10:40","10:45","PAUSE"), ("10:45","11:30","UNTERRICHT"), ("11:30","11:50","PAUSE"),
    ("11:50","12:35","UNTERRICHT"), ("12:35","12:40","PAUSE"), ("12:40","13:25","UNTERRICHT"),
    ("13:25","13:35","PAUSE"), ("13:35","14:20","UNTERRICHT"), ("14:20","14:25","PAUSE"),
    ("14:25","15:10","UNTERRICHT"), ("15:10","15:15","PAUSE"), ("15:15","16:00","UNTERRICHT")
]

def number_lessons(plan):
    n=1; out=[]
    for a,b,l in plan:
        if l=="UNTERRICHT": l=f"{n}. STUNDE"; n+=1
        out.append((a,b,l))
    return out
PLAN = number_lessons(PLAN_RAW)

def to_sec(t):
    h,m = map(int,t.split(":")); return h*3600+m*60

def get_status(now):
    cur = now.hour*3600+now.minute*60+now.second
    for a,b,l in PLAN:
        s,e = to_sec(a),to_sec(b)
        if s<=cur<e: return l, e-cur, (cur-s)/(e-s), a, b
    return "FEIERABEND", 0, 1.0, "--:--", "--:--"

def fmt(sec):
    m,s = divmod(int(sec),60); return f"{m:02d}:{s:02d}"

def clamp(x,a,b): return a if x<a else b if x>b else x

def blend(c1,c2,t): return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

# ============================================================
# SYSTEM STATS & DATEI LOADER
# ============================================================
def get_pi_stats():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read()) / 1000.0
    except: temp = 0.0
    try: load = os.getloadavg()[0]
    except: load = 0.5
    watts = 3.2 + (load * 1.5)
    return temp, watts

def load_quotes():
    data = {
        "neutral": ["System läuft.", "Alles stabil.", "Guck nicht so!"],
        "genervt": ["Nein Martin.", "Wartung? Später.", "Kein Wunderheiler."],
        "müde": ["Energie bei 2%.", "Pause? Jetzt?", "Simuliere Bereitschaft."],
        "arbeit": ["Scan läuft...", "Langeweile erkannt.", "Effizienz? Nö."]
    }
    if os.path.exists(TXT_PATH):
        try:
            file_data = {"neutral":[], "genervt":[], "müde":[], "arbeit":[]}
            with open(TXT_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        cat, txt = line.split(":", 1)
                        cat = cat.strip().lower()
                        txt = txt.strip()
                        if cat in file_data and txt:
                            file_data[cat].append(txt)
            for k in file_data:
                if file_data[k]:
                    data[k] = file_data[k]
        except: pass
    return data

def load_faces():
    faces = ["NO FILE", "CHECK", "ASSETS"]
    if os.path.exists(ART_PATH):
        try:
            with open(ART_PATH, "r", encoding="utf-8") as f:
                loaded = [line.strip() for line in f if line.strip()]
            if loaded:
                print(f"OK: {len(loaded)} ASCII-Arts geladen.")
                faces = loaded
            else:
                faces = ["FILE", "EMPTY"]
        except Exception as e:
            print(f"Error reading art.txt: {e}")
    else:
        print("WARNUNG: art.txt fehlt!")
    return faces

# ============================================================
# TEXTE & EVENTS CONFIG
# ============================================================
CRITL_QUOTES = load_quotes()
CRITL_FACES = load_faces() 

EVENTS = [
    {"type":"rads",     "min":25, "max":45},
    {"type":"critical", "min":30, "max":45},
    {"type":"vats",     "min":20, "max":40},
    {"type":"error",    "min":20, "max":35},
    {"type":"chem",     "min":20, "max":35},
    {"type":"vision",   "min":25, "max":45},
    {"type":"censored", "min":20, "max":45},
    {"type":"emote",    "min":10, "max":15},
    {"type":"glitch_blue", "min":3, "max":5},
    {"type":"glitch_green","min":3, "max":5},
    {"type":"glitch_blue", "min":3, "max":5}, 
    {"type":"glitch_green","min":3, "max":5}
]

# ============================================================
# INIT
# ============================================================
pygame.init()
screen = pygame.display.set_mode((W,H), pygame.FULLSCREEN | pygame.NOFRAME)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

def load_font(size):
    try: return pygame.font.Font(FONT_PATH,size)
    except: return pygame.font.SysFont("monospace",size)

font_time, font_body, font_small, font_v_small = load_font(75), load_font(32), load_font(24), load_font(18)

# ROBUSTER FONT LOADER
font_smilie = None
possible_fonts = ["dejavu sans", "noto sans", "arial", "segoe ui", "symbola", "freesans"]
for f_name in possible_fonts:
    try:
        f = pygame.font.SysFont(f_name, 32, bold=True)
        if f: 
            font_smilie = f
            break
    except: continue

if not font_smilie:
    font_smilie = pygame.font.SysFont(None, 35, bold=True)

try: bg = pygame.transform.scale(pygame.image.load(BG_PATH),(W,H))
except: bg = pygame.Surface((W,H)); bg.fill(BLACK)

critl_imgs={}
for k,p in CRITL_PATHS.items():
    try: critl_imgs[k]=pygame.transform.smoothscale(pygame.image.load(p).convert_alpha(),(350,350))
    except: critl_imgs[k]=None

# ============================================================
# ZEICHEN-HELFER
# ============================================================
def draw_text_wrapped(text, x, y, font, color, max_w=580):
    words = text.split(' '); lines = []; cur_l = ""
    for w_ in words:
        if font.size(cur_l + w_)[0] < max_w: cur_l += w_ + " "
        else: lines.append(cur_l); cur_l = w_ + " "
    lines.append(cur_l)
    for i, l in enumerate(lines):
        screen.blit(font.render(l.strip(), True, color), (x, y + i * (font.get_height() + 2)))

def draw_bar(x, y, w, h, prog, is_pause, remain, label, t_start, t_end):
    pygame.draw.rect(screen, DIM_GREEN, (x, y, w, h))
    pygame.draw.rect(screen, GREEN, (x, y, w, h), 3)
    col = BLUE if is_pause else (blend(GREEN, WARN, 1-remain/120) if remain <= 120 else GREEN)
    fill_w = int((w - 6) * prog)
    if fill_w > 0: pygame.draw.rect(screen, col, (x + 3, y + 3, fill_w, h - 6))
    full_text = f"{t_start}-{t_end} | {label}"
    if remain > 0: full_text += f" | NOCH {fmt(remain)}"
    s_light = font_small.render(full_text, True, GREEN_SOFT)
    s_dark  = font_small.render(full_text, True, BLACK)
    tx = x + (w - s_light.get_width()) // 2
    ty = y + (h - s_light.get_height()) // 2
    screen.set_clip(pygame.Rect(x+3, y+3, fill_w, h-6))
    screen.blit(s_dark, (tx, ty))
    screen.set_clip(pygame.Rect(x+3+fill_w, y+3, w-6-fill_w, h-6))
    screen.blit(s_light, (tx, ty))
    screen.set_clip(None)

def draw_edge_scan(t):
    lw, lx = 60, int((t * 100) % W)
    cv = int(math.sin(t * 2) * 127 + 128); col = (0, 255, cv)
    if lx + lw > W:
        pygame.draw.line(screen, col, (lx, H-12), (W, H-12), 3)
        pygame.draw.line(screen, col, (0, H-12), (lw - (W - lx), H-12), 3)
    else: pygame.draw.line(screen, col, (lx, H-12), (lx + lw, H-12), 3)

def tint(color, alpha):
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    s.fill((color[0], color[1], color[2], alpha))
    screen.blit(s, (0, 0))

def draw_status_icons(t):
    start_x, y, r, g, b = W - 110, 20, 80, 255, 80
    w_v = int(100 + 100 * math.sin(t * 0.8))
    s_w = pygame.Surface((34,34), pygame.SRCALPHA)
    for i in range(3): pygame.draw.arc(s_w, (r, g, b, w_v), (5+i*4, 8+i*4, 24-i*8, 24-i*8), math.pi/4, 3*math.pi/4, 2)
    screen.blit(s_w, (start_x, y))
    r_v = int(100 + 100 * math.sin(t * 0.5))
    s_r = pygame.Surface((34,34), pygame.SRCALPHA); c=(17,17)
    pygame.draw.circle(s_r, (r, g, b, r_v), c, 4)
    for i in range(3):
        ang = i * (2 * math.pi / 3) - (math.pi / 2)
        p1 = (c[0] + 14 * math.cos(ang - 0.5), c[1] + 14 * math.sin(ang - 0.5))
        p2 = (c[0] + 14 * math.cos(ang + 0.5), c[1] + 14 * math.sin(ang + 0.5))
        pygame.draw.polygon(s_r, (r, g, b, r_v), [c, p1, p2])
    screen.blit(s_r, (start_x + 35, y))
    bc = (200, 255, 200, 255) if random.random() > 0.98 else (r//2, g//2, b//2, 100)
    s_b = pygame.Surface((34,34), pygame.SRCALPHA)
    pts = [(17, 4), (24, 16), (17, 16), (20, 30), (10, 16), (17, 16)]
    pygame.draw.polygon(s_b, bc, pts)
    screen.blit(s_b, (start_x + 70, y))

# ============================================================
# MAIN LOOP
# ============================================================
active_event, ev_start, ev_dur = None, 0, 0
next_event = time.time() + 120 

active_quote, q_until, next_quote = "", 0, time.time()+20
active_face, last_face_change = "INIT", 0 

while True:
    t_now = time.time()
    
    # ----------------------------------------------------
    # SCHLAFMODUS
    # ----------------------------------------------------
    now = datetime.now()
    if now.hour >= 17 or now.hour < 7:
        screen.fill(BLACK)
        zzz_x, zzz_y = random.randint(50, W-150), random.randint(50, H-50)
        screen.blit(font_time.render("Zzzzz...", True, (0, 50, 0)), (zzz_x, zzz_y))
        screen.blit(font_v_small.render(f"SLEEP MODE | {now.strftime('%H:%M')}", True, (0, 30, 0)), (20, H-30))
        pygame.display.flip()
        time.sleep(2) 
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q): pygame.quit(); sys.exit()
        continue 

    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q): pygame.quit(); sys.exit()
        
        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if pygame.Rect(W - 360, 40, 350, 350).collidepoint(mx, my):
                active_event = random.choice(EVENTS)
                ev_start = t_now
                ev_dur = random.randint(active_event["min"], active_event["max"])
                next_event = t_now + random.randint(120, 300)

    label, remain, prog, t_s, t_e = get_status(now)
    is_p = "PAUSE" in label or "VORBEREITUNG" in label
    
    screen.blit(bg, (0, 0))

    if active_event:
        p_ev = clamp((t_now - ev_start) / ev_dur, 0, 1)
        et = active_event["type"]

        if et == "glitch_blue":
            tint((0, 50, 100), 40)
            sy = int(p_ev * H)
            pygame.draw.line(screen, (100, 200, 255), (0, sy), (W, sy), 3)
            pygame.draw.line(screen, (100, 200, 255), (0, sy-2), (W, sy-2), 1)
        
        elif et == "glitch_green":
            for _ in range(600):
                screen.set_at((random.randrange(W), random.randrange(H)), (100, 255, 100))

        elif et == "rads":
            tint((0, 255, 0), 50)
            for _ in range(1000): 
                screen.set_at((random.randrange(W), random.randrange(H)), GREEN)
            isotopes = ["U-235", "Pu-239", "Cs-137", "I-131", "Sr-90", "Co-60"]
            for i in range(5):
                iso = isotopes[(int(t_now) + i) % len(isotopes)]
                val = random.randint(400, 9999)
                txt_str = f"SENSOR_0{i+1}: {iso} ... {val} mSv"
                screen.blit(font_small.render(txt_str, True, GREEN_SOFT), (40, 80 + i * 35))
            if int(t_now * 2) % 2 == 0:
                warn_rect = pygame.Rect(40, H-160, 250, 30)
                pygame.draw.rect(screen, DIM_GREEN, warn_rect)
                pygame.draw.rect(screen, GREEN, warn_rect, 1)
                screen.blit(font_v_small.render("WARNING: HAZARDOUS ENVIRONMENT", True, GREEN), (50, H-155))

        elif et == "critical":
            tint((100, 0, 0), 80)
            shake = int(2 + 28 * p_ev)
            ox, oy = random.randint(-shake, shake), random.randint(-shake, shake)
            screen.blit(screen.copy(), (ox, oy))
            if math.sin(t_now * (5 + 25 * p_ev)) > 0: tint((255, 0, 0), int(50 + 70 * p_ev))
            if random.random() > 0.8:
                bx, by = random.randint(0, W), random.randint(0, H)
                pygame.draw.rect(screen, WHITE, (bx, by, random.randint(50,150), random.randint(10,50)))

        elif et == "vats":
            tint(DIM_BLUE, 80)
            pygame.draw.rect(screen, BLUE, (0,0,W,H), 8)
            for i in range(0, W, 40): pygame.draw.line(screen, (0, 60, 180), (i, 0), (i, H), 1)
            for i in range(0, H, 40): pygame.draw.line(screen, (0, 60, 180), (0, i), (W, i), 1)
            cx, cy = W//2, H//2
            ang = t_now * 2
            for i in range(4):
                rad = ang + (i * math.pi / 2)
                px = cx + 80 * math.cos(rad)
                py = cy + 80 * math.sin(rad)
                pygame.draw.line(screen, BLUE, (cx, cy), (px, py), 2)
                pygame.draw.circle(screen, BLUE, (int(px), int(py)), 5)
            v_rad = int(250 * p_ev)
            if v_rad > 10: pygame.draw.circle(screen, BLUE, (cx, cy), v_rad, 2)
            parts = ["HEAD", "TORSO", "L.ARM", "R.ARM", "LEGS"]
            active_part = parts[int(t_now * 2) % len(parts)]
            # BUGFIX HIER: Zeile war zu lang/komplex
            for i, p in enumerate(parts):
                col = WHITE if p == active_part else (0, 100, 200)
                mark = "X" if p == active_part else " "
                val_perc = random.randint(20, 95)
                # Sicherer String-Aufbau
                text_content = f"[{mark}] {p} - {val_perc}%"
                txt = font_small.render(text_content, True, col)
                
                lx, ly = W - 210, 115 + i * 30
                if p == active_part: pygame.draw.line(screen, BLUE, (cx, cy), (lx, ly), 1)
                screen.blit(txt, (W - 200, 100 + i * 30))
            pygame.draw.rect(screen, (0, 50, 100), (50, H-60, 200, 20))
            fill = int((math.sin(t_now*3)+1)/2 * 200)
            pygame.draw.rect(screen, BLUE, (50, H-60, fill, 20))
            screen.blit(font_v_small.render("CRIT CHANCE", True, BLUE), (50, H-85))

        elif et == "error":
            screen.fill((0, 0, 150))
            for i in range(int(p_ev * 12)):
                txt = font_small.render(f"0x{random.randint(1000,9999)}F: SEGMENTATION_FAULT_CORE_{i}", True, WHITE)
                screen.blit(txt, (40, 60 + i * 25))
            for qy in range(100, 200, 5):
                for qx in range(400, 500, 5):
                    if random.random() > 0.5: pygame.draw.rect(screen, WHITE, (qx, qy, 5, 5))
            bar_w = int(p_ev * 500)
            pygame.draw.rect(screen, WHITE, (70, H-60, 500, 20), 2)
            pygame.draw.rect(screen, WHITE, (74, H-56, bar_w, 12))
            screen.blit(font_small.render("DUMPING PHYSICAL MEMORY TO DISK...", True, WHITE), (70, H-90))

        elif et == "chem":
            r = int(127+127*math.sin(t_now*4))
            g = int(127+127*math.sin(t_now*4+2))
            b = int(127+127*math.sin(t_now*4+4))
            tint((r, g, b), 80)
            off_x = int(math.sin(t_now * 5) * 10)
            off_y = int(math.cos(t_now * 5) * 10)
            if img: 
                ghost = img.copy()
                ghost.set_alpha(100)
                screen.blit(ghost, (W - 360 + off_x, 40 + off_y))

        elif et == "vision":
            vp = int(130 + 30 * math.sin(t_now * 1.5))
            tint((100, 255, 100), vp)
            for i in range(3):
                sy = int((t_now * [150, 250, 400][i] + i * 100) % H)
                s_l = pygame.Surface((W, 3), pygame.SRCALPHA); s_l.fill((255, 255, 255, 60))
                screen.blit(s_l, (0, sy))
            pygame.draw.circle(screen, BLACK, (W//2, H//2), 350, 100) 
            cx, cy = W//2, H//2
            pygame.draw.line(screen, GREEN_SOFT, (cx-40, cy), (cx+40, cy), 1)
            pygame.draw.line(screen, GREEN_SOFT, (cx, cy-40), (cx, cy+40), 1)
            dist = int(140 + math.sin(t_now)*10)
            screen.blit(font_v_small.render(f"DIST: {dist}m", True, GREEN), (cx+50, cy+50))
            for i in range(0, W, 50):
                off = (i + int(t_now * 50)) % W
                pygame.draw.line(screen, GREEN_SOFT, (off, 0), (off, 15), 2)
                if i % 100 == 0: screen.blit(font_v_small.render(f"{i}", True, GREEN_SOFT), (off-10, 20))
            batt_w = int(50 - (p_ev * 50))
            pygame.draw.rect(screen, GREEN, (W-70, 20, 50, 15), 1)
            pygame.draw.rect(screen, GREEN, (W-70+1, 21, batt_w, 13))
            screen.blit(font_v_small.render("BATT", True, GREEN), (W-70, 5))

        elif et == "censored":
            for y in range(0, H, 20):
                line = "CONFIDENTIAL " * 10
                off_x = int(t_now * 20) % 100
                col = (30, 10, 0)
                screen.blit(font_v_small.render(line, True, col), (-off_x, y))
            tint(BLACK, 150)
            lx, ly = W//2 - 25, H//2 - 120
            pygame.draw.rect(screen, RED, (lx, ly+40, 50, 40)) 
            pygame.draw.arc(screen, RED, (lx, ly, 50, 50), 0, math.pi, 3) 
            if int(t_now * 4) % 2 == 0:
                box_rect = (W//2 - 200, H//2 - 60, 400, 160)
                pygame.draw.rect(screen, BLACK, box_rect)
                pygame.draw.rect(screen, RED, box_rect, 5)
                txt1 = font_body.render("ACCESS DENIED", True, RED)
                txt2 = font_small.render("SECURITY CLEARANCE REQUIRED", True, RED)
                screen.blit(txt1, (W//2 - txt1.get_width()//2, H//2 - 20))
                screen.blit(txt2, (W//2 - txt2.get_width()//2, H//2 + 30))
                bar_x, bar_y = W//2 - 150, H//2 + 70
                pygame.draw.rect(screen, RED, (bar_x, bar_y, 300, 20), 1)
                prog_w = int((t_now % 1) * 300)
                pygame.draw.rect(screen, RED, (bar_x+2, bar_y+2, prog_w, 16))

        elif et == "emote":
            ei = critl_imgs.get(random.randint(1,4))
            scale = 1.0 + 0.1 * math.sin(t_now * 10)
            if ei: 
                w_new, h_new = int(W*scale), int(H*scale)
                scaled_img = pygame.transform.scale(ei, (w_new, h_new))
                screen.blit(scaled_img, (W//2 - w_new//2, H//2 - h_new//2))

        if t_now - ev_start >= ev_dur: active_event = None

    else:
        # --- DASHBOARD ---
        mood = "müde" if is_p else ("genervt" if remain <= 120 else "neutral")
        img = critl_imgs.get(1 if mood=="neutral" else (2 if mood=="genervt" else 3))
        if img: screen.blit(img, (W - 360, 40)) 
        
        pi_temp, pi_watts = get_pi_stats()
        stat_text = font_v_small.render(f"TEMP: {pi_temp:.1f}C  PWR: {pi_watts:.1f}W", True, GREEN)
        screen.blit(stat_text, (20, 10))
        screen.blit(font_time.render(now.strftime("%H:%M"), True, GREEN), (30, 45))
        
        draw_status_icons(t_now)
        wd = {"Monday":"MONTAG","Tuesday":"DIENSTAG","Wednesday":"MITTWOCH","Thursday":"DONNERSTAG","Friday":"FREITAG","Saturday":"SAMSTAG","Sunday":"SONNTAG"}
        screen.blit(font_body.render(f"{wd.get(now.strftime('%A'),'TAG')}, {now.strftime('%d.%m.')}", True, GREEN_SOFT), (35, 120))
        
        # SMILIE AUS DATEI
        if t_now - last_face_change > 5:
            if CRITL_FACES:
                active_face = random.choice(CRITL_FACES)
            else:
                active_face = "NO FILE"
            last_face_change = t_now
        
        # Rendern
        screen.blit(font_smilie.render(active_face, True, (20, 100, 20)), (37, 182))
        screen.blit(font_smilie.render(active_face, True, GREEN), (35, 180))
        
        draw_bar(20, H-80, 600, 45, prog, is_p, remain, label, t_s, t_e)
        
        if not active_quote and t_now > next_quote:
            active_quote, q_until, next_quote = random.choice(CRITL_QUOTES[mood]), t_now+6, t_now+random.randint(30,60)
        
        if active_quote: draw_text_wrapped("CRITL: "+active_quote, 35, H-175, font_small, GREEN_SOFT)

    draw_edge_scan(t_now)
    sl = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 6): pygame.draw.line(sl, (0, 10, 0, 40), (0, y), (W, y), 1)
    screen.blit(sl, (0,0))
    if not active_event and t_now > next_event:
        active_event = random.choice(EVENTS)
        ev_start, ev_dur = t_now, random.randint(active_event["min"], active_event["max"])
        next_event = t_now + random.randint(120, 300) 
    pygame.display.flip()
