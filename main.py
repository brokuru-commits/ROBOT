#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame, sys, time, random, math
from datetime import datetime

# =========================
# DISPLAY / DESIGN
# =========================
W, H = 640, 480
FPS = 20

GREEN = (80, 255, 80)
GREEN_DIM = (20, 60, 20)
BLUE = (0, 180, 255)
WARN = (255, 180, 60)
RED = (160, 40, 40)
BLACK = (0, 0, 0)

BG_PATH = "bg.png"

# =========================
# INIT
# =========================
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
clock = pygame.time.Clock()

f_xl = pygame.font.SysFont("DejaVu Sans Mono", 56, True)
f_l  = pygame.font.SysFont("DejaVu Sans Mono", 36, True)
f_m  = pygame.font.SysFont("DejaVu Sans Mono", 28)
f_s  = pygame.font.SysFont("DejaVu Sans Mono", 22)
f_mono = pygame.font.SysFont("Courier", 28, True)

bg = pygame.image.load(BG_PATH).convert()
bg = pygame.transform.scale(bg, (W, H))

# =========================
# STUNDENPLAN
# =========================
PLAN_RAW = [
    (7,30,8,0,"PAUSE"),
    (8,0,8,45,"UNTERRICHT"),
    (8,45,8,50,"PAUSE"),
    (8,50,9,35,"UNTERRICHT"),
    (9,35,9,55,"PAUSE"),
    (9,55,10,40,"UNTERRICHT"),
    (10,40,10,45,"PAUSE"),
    (10,45,11,30,"UNTERRICHT"),
    (11,30,11,50,"PAUSE"),
    (11,50,12,35,"UNTERRICHT"),
    (12,35,12,40,"PAUSE"),
    (12,40,13,25,"UNTERRICHT"),
    (13,25,13,35,"PAUSE"),
    (13,35,14,20,"UNTERRICHT"),
    (14,20,14,25,"PAUSE"),
    (14,25,15,10,"UNTERRICHT"),
    (15,10,15,15,"PAUSE"),
    (15,15,16,0,"UNTERRICHT"),
    (16,0,17,0,"FEIERABEND"),
]

def number_lessons(plan):
    n = 1
    out = []
    for sh,sm,eh,em,label in plan:
        if label == "UNTERRICHT":
            label = f"UNTERRICHT {n}"
            n += 1
        out.append((sh,sm,eh,em,label))
    return out

PLAN = number_lessons(PLAN_RAW)

def secs(h,m,s=0): return h*3600+m*60+s

def get_status():
    now = datetime.now()
    cur = secs(now.hour, now.minute, now.second)
    for sh,sm,eh,em,label in PLAN:
        start = secs(sh,sm)
        end = secs(eh,em)
        if start <= cur < end:
            total = end-start
            return label, end-cur, (cur-start)/total
    return "FREIZEIT", 0, 0

def fmt(sec):
    m,s = divmod(max(0,int(sec)),60)
    return f"{m:02d}:{s:02d}"

def blend(c1,c2,t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

# =========================
# HAMSTER ENTITY
# =========================
HAMSTER_FRAMES = [
    ["(\\__/)", "(•ㅅ• ) < compiling reality", "/ 　 づ"],
    ["(\\__/)", "(ಠ_ಠ ) < why though", "/ 　 づ"],
    ["(\\__/)", "(¬_¬ ) < coffee missing", "/ 　 づ"],
    ["(\\__/)", "(ʘ_ʘ ) < anomaly?", "/ 　 づ"],
    ["(\\__/)", "(x_x ) < dead inside", "/ 　 づ"],
    ["(\\__/)", "(ง'̀-'́)ง < fighting bugs", "/ 　 づ"],
    ["(\\__/)", "(•ᴗ• ) < maybe ok", "/ 　 づ"],
]

hamster_idx = 0
next_face = time.time() + random.randint(2,5)

# =========================
# EVENTS
# =========================
EVENTS = [
    {"style":"scan","lines":[
        "[ SYS ] ENVIRONMENT SCAN",
        "[ OK ] REALITY FRAGILE",
        "[ OK ] HAMSTER AWAKE"
    ]},
    {"style":"warn","lines":[
        "[ WARNING ]",
        "ANOMALY DETECTED",
        "LIKELY YOU"
    ]},
    {"style":"leak","lines":[
        "[ LEAK ]",
        "Some data escaped.",
        "I was judging your code."
    ]},
    {"style":"glitch","lines":[
        "[ SYS ]",
        "THIS IS UNNECESSARILY HARD"
    ]},
    {"style":"exist","lines":[
        "[ HAMSTER LOG ]",
        "I maintain this world.",
        "You call it workflow."
    ]},
    {"style":"nerd","lines":[
        "[ NET ] WEBER MODE",
        "Latency: emotional",
        "Throughput: coffee-based"
    ]}
]

active_event = None
event_until = 0
next_event = time.time() + random.randint(40,90)

def event_color(style):
    return {
        "scan":GREEN,
        "warn":RED,
        "leak":BLUE,
        "glitch":WARN,
        "exist":GREEN,
        "nerd":GREEN
    }.get(style, GREEN)

# =========================
# EFFECTS
# =========================
def apply_event_effect(style):
    overlay = pygame.Surface((W,H), pygame.SRCALPHA)
    if style == "scan":
        y = int((time.time()*120)%H)
        pygame.draw.rect(overlay,(80,255,80,80),(0,y,W,8))
    elif style == "warn":
        overlay.fill((120,0,0,80))
    elif style == "leak":
        overlay.fill((0,40,60,70))
        for _ in range(120):
            overlay.set_at((random.randrange(W),random.randrange(H)),(0,200,255,90))
    screen.blit(overlay,(0,0))

def glitch():
    for _ in range(8):
        y = random.randrange(H)
        h = random.randrange(4,14)
        off = random.randrange(-25,25)
        r = pygame.Rect(0,y,W,h)
        piece = screen.subsurface(r).copy()
        screen.blit(piece,(off,y))

def draw_scanlines():
    sl = pygame.Surface((W,H), pygame.SRCALPHA)
    for y in range(0,H,3):
        sl.fill((0,0,0,35),(0,y,W,1))
    screen.blit(sl,(0,0))

# =========================
# MAIN LOOP
# =========================
while True:
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN:
            pygame.quit(); sys.exit()

    screen.blit(bg,(0,0))

    # Uhr
    now = datetime.now().strftime("%H:%M")
    screen.blit(f_xl.render(now,True,GREEN),(40,30))

    # Hamster Animation
    t = time.time()
    if t > next_face:
        hamster_idx = (hamster_idx + random.randint(1,3)) % len(HAMSTER_FRAMES)
        next_face = t + random.randint(2,6)

    y = 110
    for l in HAMSTER_FRAMES[hamster_idx]:
        screen.blit(f_mono.render(l,True,GREEN),(60,y))
        y += 34

    # Status & Balken
    label, remain, prog = get_status()
    is_pause = "PAUSE" in label
    base = BLUE if is_pause else GREEN
    col = base
    if remain <= 120:
        col = blend(base,WARN,1-remain/120)

    pygame.draw.rect(screen,GREEN_DIM,(60,320,520,28))
    pygame.draw.rect(screen,col,(60,320,int(520*prog),28))
    screen.blit(f_m.render(f"{label} – noch {fmt(remain)}",True,GREEN),(60,285))

    # Events
    if active_event is None and t > next_event:
        active_event = random.choice(EVENTS)
        event_until = t + random.randint(5,8)
        next_event = t + random.randint(80,160)

    if active_event:
        apply_event_effect(active_event["style"])
        if active_event["style"]=="glitch":
            glitch()
        c = event_color(active_event["style"])
        y = 200
        for l in active_event["lines"]:
            screen.blit(f_s.render(l,True,c),(W//2-200,y))
            y += 26
        if t > event_until:
            active_event = None

    draw_scanlines()
    pygame.display.flip()