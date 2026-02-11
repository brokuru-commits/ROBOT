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
WARN       = (255, 180, 60)
ORANGE     = (255, 150, 50)
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)

# PFADE
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
BG_PATH   = os.path.join(ASSET_DIR, "bg.png")
FONT_PATH = os.path.join(ASSET_DIR, "Monofonto.ttf")

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
# TEXTE & EVENTS
# ============================================================
CRITL_QUOTES = {
    "neutral": ["System läuft.", "Alles stabil.", "Guck nicht so!"],
    "genervt": ["Nein Martin.", "Wartung? Später.", "Kein Wunderheiler."],
    "müde": ["Energie bei 2%.", "Pause? Jetzt?", "Simuliere Bereitschaft."],
    "arbeit": ["Scan läuft...", "Langeweile erkannt.", "Effizienz? Nö."]
}

EVENTS = [
    {"type":"rads",     "min":25, "max":45},
    {"type":"critical", "min":30, "max":45},
    {"type":"vats",     "min":20, "max":40},
    {"type":"error",    "min":20, "max":35},
    {"type":"chem",     "min":20, "max":35},
    {"type":"vision",   "min":25, "max":45},
    {"type":"censored", "min":20, "max":45},
    {"type":"emote",    "min":10, "max":15}
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

try: bg = pygame.transform.scale(pygame.image.load(BG_PATH),(W,H))
except: bg = pygame.Surface((W,H)); bg.fill(BLACK)

# HAMSTER: 350x350 Pixel
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
    # Rahmen & Hintergrund
    pygame.draw.rect(screen, DIM_GREEN, (x, y, w, h))
    pygame.draw.rect(screen, GREEN, (x, y, w, h), 3)
    
    # Füllung
    col = BLUE if is_pause else (blend(GREEN, WARN, 1-remain/120) if remain <= 120 else GREEN)
    fill_w = int((w - 6) * prog)
    if fill_w > 0: pygame.draw.rect(screen, col, (x + 3, y + 3, fill_w, h - 6))
    
    # Text zusammenbauen (Einheitlich)
    full_text = f"{t_start}-{t_end} | {label}"
    if remain > 0: full_text += f" | NOCH {fmt(remain)}"
    
    s_light = font_small.render(full_text, True, GREEN_SOFT)
    s_dark  = font_small.render(full_text, True, BLACK)
    
    tx = x + (w - s_light.get_width()) // 2
    ty = y + (h - s_light.get_height()) // 2
    
    # Clipping für Invertierungs-Effekt
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
    
    # WiFi
    w_v = int(100 + 100 * math.sin(t * 0.8))
    s_w = pygame.Surface((34,34), pygame.SRCALPHA)
    for i in range(3): pygame.draw.arc(s_w, (r, g, b, w_v), (5+i*4, 8+i*4, 24-i*8, 24-i*8), math.pi/4, 3*math.pi/4, 2)
    screen.blit(s_w, (start_x, y))
    
    # Rad
    r_v = int(100 + 100 * math.sin(t * 0.5))
    s_r = pygame.Surface((34,34), pygame.SRCALPHA); c=(17,17)
    pygame.draw.circle(s_r, (r, g, b, r_v), c, 4)
    for i in range(3):
        ang = i * (2 * math.pi / 3) - (math.pi / 2)
        p1 = (c[0] + 14 * math.cos(ang - 0.5), c[1] + 14 * math.sin(ang - 0.5))
        p2 = (c[0] + 14 * math.cos(ang + 0.5), c[1] + 14 * math.sin(ang + 0.5))
        pygame.draw.polygon(s_r, (r, g, b, r_v), [c, p1, p2])
    screen.blit(s_r, (start_x + 35, y))
    
    # Blitz
    bc = (200, 255, 200, 255) if random.random() > 0.98 else (r//2, g//2, b//2, 100)
    s_b = pygame.Surface((34,34), pygame.SRCALPHA)
    pts = [(17, 4), (24, 16), (17, 16), (20, 30), (10, 16), (17, 16)]
    pygame.draw.polygon(s_b, bc, pts)
    screen.blit(s_b, (start_x + 70, y))

# ============================================================
# MAIN LOOP
# ============================================================
active_event, ev_start, ev_dur = None, 0, 0
next_event = time.time() + 180 
active_quote, q_until, next_quote = "", 0, time.time()+20
active_face, last_face_change = "(o_o)", 0

while True:
    t_now = time.time(); clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q): pygame.quit(); sys.exit()

    now = datetime.now()
    label, remain, prog, t_s, t_e = get_status(now)
    is_p = "PAUSE" in label or "VORBEREITUNG" in label
    
    screen.blit(bg, (0, 0))

    if active_event:
        p_ev = clamp((t_now - ev_start) / ev_dur, 0, 1)
        et = active_event["type"]

        # 1. RADS (Massives Rauschen)
        if et == "rads":
            tint((0, 255, 0), 60)
            wave_y = int((t_now * 150) % H)
            pygame.draw.rect(screen, (0, 255, 0, 40), (0, wave_y, W, 60))
            tint((0, 255, 0), int(30 + 20 * math.sin(t_now * 10)))
            for _ in range(1000): # 1000 Partikel
                screen.set_at((random.randrange(W), random.randrange(H)), GREEN)

        # 2. CRITICAL (Screen Shake & Glitch)
        elif et == "critical":
            tint((100, 0, 0), 80)
            shake = int(2 + 28 * p_ev)
            ox, oy = random.randint(-shake, shake), random.randint(-shake, shake)
            screen.blit(screen.copy(), (ox, oy)) # Glitch
            if math.sin(t_now * (5 + 25 * p_ev)) > 0: 
                tint((255, 0, 0), int(50 + 70 * p_ev))

        # 3. VATS (Gitter & Scan)
        elif et == "vats":
            tint((0, 0, 100), 50)
            pygame.draw.rect(screen, BLUE, (0,0,W,H), 12)
            # Gitterlinien
            for i in range(0, W, 40): pygame.draw.line(screen, (0, 60, 180), (i, 0), (i, H), 1)
            for i in range(0, H, 40): pygame.draw.line(screen, (0, 60, 180), (0, i), (W, i), 1)
            v_rad = int(250 * p_ev)
            pygame.draw.circle(screen, BLUE, (W//2,H//2), max(5, v_rad), 2)
            for _ in range(3):
                tx, ty = random.randint(50, W-150), random.randint(50, H-100)
                screen.blit(font_small.render(f"{random.randint(10,99)}%", True, BLUE), (tx, ty))

        # 4. ERROR (Textzeilen)
        elif et == "error":
            screen.fill((0, 0, 150))
            for i in range(int(p_ev * 15)):
                txt = font_small.render(f"0x00{random.randint(1000, 9999)}: STACK_OVERFLOW", True, WHITE)
                screen.blit(txt, (40, 60 + i * 25))

        # 5. CHEM (Farbverlauf)
        elif et == "chem":
            r = int(127+127*math.sin(t_now*4))
            g = int(127+127*math.sin(t_now*4+2))
            b = int(127+127*math.sin(t_now*4+4))
            tint((r, g, b), 120)

        # 6. VISION (3 Scanlinien + Rauschen)
        elif et == "vision":
            vp = int(130 + 30 * math.sin(t_now * 1.5))
            tint((100, 255, 100), vp)
            for i in range(3):
                sy = int((t_now * [150, 250, 400][i] + i * 100) % H)
                s_l = pygame.Surface((W, 3), pygame.SRCALPHA)
                s_l.fill((255, 255, 255, 60))
                screen.blit(s_l, (0, sy))
            for _ in range(300): 
                screen.set_at((random.randrange(W), random.randrange(H)), (180, 255, 180))

        # 7. CENSORED (Schwarze Balken)
        elif et == "censored":
            tint((20, 10, 0), 200)
            for i in range(0, H, 40):
                off = int(math.sin(t_now * 5 + i) * 20)
                if (i // 40) % 2 == 0: pygame.draw.rect(screen, BLACK, (off, i, W, 25))
            st = font_time.render("REDACTED", True, (200, 0, 0))
            screen.blit(st, (W//2 - st.get_width()//2, H//2 - st.get_height()//2))

        # 8. EMOTE
        elif et == "emote":
            ei = critl_imgs.get(random.randint(1,4))
            if ei: screen.blit(pygame.transform.scale(ei, (W,H)), (0,0))

        if t_now - ev_start >= ev_dur: active_event = None

    else:
        # --- DASHBOARD (HOMESCREEN) ---
        mood = "müde" if is_p else ("genervt" if remain <= 120 else "neutral")
        img = critl_imgs.get(1 if mood=="neutral" else (2 if mood=="genervt" else 3))
        
        # Hamster (350px)
        if img: screen.blit(img, (W - 360, 40)) 
        
        # UI
        screen.blit(font_time.render(now.strftime("%H:%M"), True, GREEN), (30, 30))
        draw_status_icons(t_now)
        wd = {"Monday":"MONTAG","Tuesday":"DIENSTAG","Wednesday":"MITTWOCH","Thursday":"DONNERSTAG","Friday":"FREITAG","Saturday":"SAMSTAG","Sunday":"SONNTAG"}
        screen.blit(font_body.render(f"{wd.get(now.strftime('%A'),'TAG')}, {now.strftime('%d.%m.')}", True, GREEN_SOFT), (35, 110))
        
        # Smilie
        if t_now - last_face_change > 5:
            all_faces = ["(o_o)", "[O.O]", "( -_-)", "<o_o>", "(u_u)", "(^.^)", "(⌐■_■)", "(◕‿◕)"]
            active_face = random.choice(all_faces); last_face_change = t_now
        screen.blit(font_body.render(active_face, True, (20, 100, 20)), (37, 182))
        screen.blit(font_body.render(active_face, True, GREEN), (35, 180))
        
        # Balken (Vereint)
        draw_bar(20, H-80, 600, 45, prog, is_p, remain, label, t_s, t_e)
        
        # Zitat
        if not active_quote and t_now > next_quote:
            active_quote, q_until, next_quote = random.choice(CRITL_QUOTES[mood]), t_now+6, t_now+random.randint(30,60)
        if active_quote: draw_text_wrapped("CRITL: "+active_quote, 35, H-130, font_small, GREEN_SOFT)

    # Global
    draw_edge_scan(t_now)
    sl = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 6): pygame.draw.line(sl, (0, 10, 0, 40), (0, y), (W, y), 1)
    screen.blit(sl, (0,0))
    
    # Event Trigger
    if not active_event and t_now > next_event:
        active_event = random.choice(EVENTS)
        ev_start, ev_dur = t_now, random.randint(active_event["min"], active_event["max"])
        next_event = t_now + random.randint(180, 600)
    
    pygame.display.flip()
