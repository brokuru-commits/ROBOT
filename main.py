#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, math, random
from datetime import datetime
import pygame

# ============================================================
# FIXED SPECS
# ============================================================
W, H = 640, 480
FPS = 25

GREEN      = (80, 255, 80)
GREEN_SOFT = (120, 255, 120)
DIM_GREEN  = (18, 55, 18)
BLUE       = (0, 190, 255)
WARN       = (255, 180, 60)
ORANGE     = (255, 150, 50)
BLACK      = (0, 0, 0)

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

BG_PATH   = os.path.join(ASSET_DIR, "bg.png")
FONT_PATH = os.path.join(ASSET_DIR, "Monofonto.ttf")

CRITL_PATHS = {
    1: os.path.join(ASSET_DIR, "1.png"),
    2: os.path.join(ASSET_DIR, "2.png"),
    3: os.path.join(ASSET_DIR, "3.png"),
    4: os.path.join(ASSET_DIR, "4.png"),
}

# ============================================================
# STUNDENPLAN
# ============================================================
PLAN_RAW = [
    ("07:30","08:00","VORBEREITUNG"),
    ("08:00","08:45","UNTERRICHT"),
    ("08:45","08:50","PAUSE"),
    ("08:50","09:35","UNTERRICHT"),
    ("09:35","09:55","PAUSE"),
    ("09:55","10:40","UNTERRICHT"),
    ("10:40","10:45","PAUSE"),
    ("10:45","11:30","UNTERRICHT"),
    ("11:30","11:50","PAUSE"),
    ("11:50","12:35","UNTERRICHT"),
    ("12:35","12:40","PAUSE"),
    ("12:40","13:25","UNTERRICHT"),
    ("13:25","13:35","PAUSE"),
    ("13:35","14:20","UNTERRICHT"),
    ("14:20","14:25","PAUSE"),
    ("14:25","15:10","UNTERRICHT"),
    ("15:10","15:15","PAUSE"),
    ("15:15","16:00","UNTERRICHT"),
]

def number_lessons(plan):
    n=1; out=[]
    for a,b,l in plan:
        if l=="UNTERRICHT":
            l=f"{n}. STUNDE"
            n+=1
        out.append((a,b,l))
    return out

PLAN = number_lessons(PLAN_RAW)

def to_sec(t):
    h,m = map(int,t.split(":"))
    return h*3600+m*60

def get_status(now):
    cur = now.hour*3600+now.minute*60+now.second
    for a,b,l in PLAN:
        s,e = to_sec(a),to_sec(b)
        if s<=cur<e:
            total=e-s
            passed=cur-s
            return l,e-cur,passed/total
    return "FEIERABEND",0,1.0

def fmt(sec):
    m,s = divmod(int(sec),60)
    return f"{m:02d}:{s:02d}"

def clamp(x,a,b): return a if x<a else b if x>b else x

def blend(c1,c2,t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

# ============================================================
# EVENTS & SPRÜCHE
# ============================================================
CRITL_QUOTES = {
    "neutral": ["System läuft stabil.", "Alles im grünen Bereich.", "Hö hö hö...."],
    "genervt": ["Einfach nein.", "Wartung erforderlich.", "Ich repariere, du atmest."],
    "müde": ["Energie niedrig.", "Pause wäre sinnvoll.", "Funktioniere noch."],
    "arbeit": ["Scan läuft.", "Analysiere Umgebung.", "Effizienz maximiert."]
}

EVENTS = [
    {"type":"scan","min":6,"max":10},
    {"type":"warn","min":4,"max":7},
    {"type":"leak","min":4,"max":6},
    {"type":"glitch","min":2,"max":4},
    {"type":"emote","min":5,"max":5}
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

font_time  = load_font(68)
font_body  = load_font(30)
font_small = load_font(20)

try: bg = pygame.transform.scale(pygame.image.load(BG_PATH),(W,H))
except: bg = pygame.Surface((W,H)); bg.fill(BLACK)

critl_imgs={}
for k,p in CRITL_PATHS.items():
    try: critl_imgs[k]=pygame.transform.smoothscale(pygame.image.load(p).convert_alpha(),(170,170))
    except: critl_imgs[k]=None

# ============================================================
# DRAW FUNCTIONS
# ============================================================
def draw_bar(x, y, w, h, prog, is_pause, remain, label):
    pygame.draw.rect(screen, DIM_GREEN, (x, y, w, h))
    pygame.draw.rect(screen, GREEN, (x, y, w, h), 2)
    base = BLUE if is_pause else GREEN
    col = base
    if remain <= 120: col = blend(base, WARN, 1 - remain / 120)
    fill_w = int((w - 4) * prog)
    if fill_w > 0: pygame.draw.rect(screen, col, (x + 2, y + 2, fill_w, h - 4))
    
    txt = f"{label} | NOCH {fmt(remain)}" if remain > 0 else label
    s_light = font_small.render(txt, True, GREEN_SOFT)
    s_dark  = font_small.render(txt, True, BLACK)
    tx, ty = x + (w-s_light.get_width())//2, y + (h-s_light.get_height())//2
    
    screen.set_clip(pygame.Rect(x+2, y+2, fill_w, h-4))
    screen.blit(s_dark, (tx, ty))
    screen.set_clip(pygame.Rect(x+2+fill_w, y+2, w-4-fill_w, h-4))
    screen.blit(s_light, (tx, ty))
    screen.set_clip(None)

def draw_edge_scan(t):
    line_w, line_x = 40, int((t * 80) % W)
    c_val = int(math.sin(t * 2) * 127 + 128)
    col = (0, 255, c_val)
    if line_x + line_w > W:
        pygame.draw.line(screen, col, (line_x, H-10), (W, H-10), 2)
        pygame.draw.line(screen, col, (0, H-10), (line_w - (W - line_x), H-10), 2)
    else:
        pygame.draw.line(screen, col, (line_x, H-10), (line_x + line_w, H-10), 2)

def tint(color,alpha):
    s=pygame.Surface((W,H),pygame.SRCALPHA)
    s.fill((color[0],color[1],color[2],alpha))
    screen.blit(s,(0,0))

# ============================================================
# STATES
# ============================================================
active_event = None
event_start, event_dur = 0, 0
next_event = time.time() + 30
active_quote, quote_until = "", 0
next_quote = time.time() + 20
active_face = "(o_o)"
last_face_change = 0

# ============================================================
# MAIN LOOP
# ============================================================
while True:
    t_now = time.time()
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.quit(); sys.exit()

    now = datetime.now()
    label, remain, prog = get_status(now)
    is_pause = "PAUSE" in label or "VORBEREITUNG" in label

    # Hintergrund
    screen.blit(bg, (0, 0))

    if active_event and active_event["type"] == "emote":
        # FULLSCREEN EMOTE EVENT
        e_img = critl_imgs.get(random.randint(1,4))
        if e_img:
            full_img = pygame.transform.scale(e_img, (W, H))
            screen.blit(full_img, (0, 0))
    else:
        # NORMALES DASHBOARD
        screen.blit(font_time.render(now.strftime("%H:%M"), True, GREEN), (60, 40))
        wd_map = {"Monday":"MONTAG", "Tuesday":"DIENSTAG", "Wednesday":"MITTWOCH", "Thursday":"DONNERSTAG", "Friday":"FREITAG", "Saturday":"SAMSTAG", "Sunday":"SONNTAG"}
        day_str = wd_map.get(now.strftime("%A"), now.strftime("%A").upper())
        screen.blit(font_body.render(f"{day_str}, {now.strftime('%d.%m.')}", True, GREEN_SOFT), (60, 125))

        # ASCII Gesicht
        if t_now - last_face_change > 5:
            active_face = random.choice(["(o_o)", "[O.O]", "(^.^)", "<o.o>", "( -_-)"])
            last_face_change = t_now
        screen.blit(font_body.render(active_face, True, GREEN), (60, 210))

        # Balken & Scanline
        bar_y = H - 60
        draw_bar(60, bar_y, W - 120, 30, prog, is_pause, remain, label)
        
        # Mood & Small Critl
        mood = "neutral"
        if is_pause: mood = "müde"
        if remain <= 120 and not is_pause: mood = "genervt"
        
        c_mode = 1
        if mood == "müde": c_mode = 3
        elif mood == "genervt": c_mode = 2
        
        img = critl_imgs.get(c_mode)
        if img: screen.blit(img, (W - 190, bar_y - 180))

        # Sprüche
        if not active_quote and t_now > next_quote:
            active_quote = random.choice(CRITL_QUOTES[mood])
            quote_until, next_quote = t_now + 6, t_now + random.randint(30, 60)
        if active_quote:
            screen.blit(font_small.render("CRITL: " + active_quote, True, GREEN_SOFT), (60, bar_y - 30))
            if t_now > quote_until: active_quote = ""

    # Events Logik
    if active_event is None and t_now > next_event:
        active_event = random.choice(EVENTS)
        event_start, event_dur = t_now, active_event["min"]
        next_event = t_now + random.randint(60, 150)

    if active_event:
        et = active_event["type"]
        if et == "warn": tint((255, 50, 0), 60)
        elif et == "leak":
            tint((0, 100, 255), 50)
            for _ in range(50): screen.set_at((random.randrange(W), random.randrange(H)), GREEN)
        elif et == "glitch":
            yy = random.randrange(H); hh = random.randrange(5, 20); off = random.randrange(-15, 16)
            r = pygame.Rect(0, yy, W, hh)
            try:
                sub = screen.subsurface(r).copy()
                screen.blit(sub, (off, yy))
            except: pass
        
        if t_now - event_start >= event_dur: active_event = None

    draw_edge_scan(t_now)
    # Global Scanlines
    for y in range(0, H, 4): pygame.draw.line(screen, (0, 10, 0), (0, y), (W, y), 1)
    
    pygame.display.flip()
