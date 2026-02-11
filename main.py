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
    ("07:30","08:00","PAUSE"),
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
    ("16:00","17:00","FEIERABEND"),
]

def number_lessons(plan):
    n=1; out=[]
    for a,b,l in plan:
        if l=="UNTERRICHT":
            l=f"STUNDE {n}"
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
    return "FEIERABEND",0,0

def fmt(sec):
    m,s = divmod(int(sec),60)
    return f"{m:02d}:{s:02d}"

def clamp(x,a,b): return a if x<a else b if x>b else x

def blend(c1,c2,t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

# ============================================================
# CRITL SPRÜCHE
# ============================================================
CRITL_QUOTES = {
    "neutral":[
        "System läuft. Ich auch.",
        "Alles stabil. Verdächtig stabil.",
        "Ich halte das hier zusammen."
    ],
    "genervt":[
        "Nein, Martin. Einfach nein.",
        "‚Nur kurz‘ ist kein Wartungsplan.",
        "Ich repariere das. Du schaust zu."
    ],
    "müde":[
        "Energie niedrig. Pflichtbewusstsein hoch.",
        "Pause wäre sinnvoll.",
        "Ich funktioniere. Das reicht."
    ],
    "arbeit":[
        "Scan läuft. Kompetenz sowieso.",
        "Ich analysiere. Du atmest.",
        "Das wird effizient."
    ]
}

# ============================================================
# EVENTS
# ============================================================
EVENTS = [
    {"type":"scan","min":6,"max":10},
    {"type":"warn","min":4,"max":7},
    {"type":"leak","min":4,"max":6},
    {"type":"glitch","min":2,"max":4},
    {"type":"teacher","min":5,"max":8}
]

# ============================================================
# INIT
# ============================================================
pygame.init()
screen = pygame.display.set_mode((W,H),pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

def load_font(size):
    try: return pygame.font.Font(FONT_PATH,size)
    except: return pygame.font.SysFont("monospace",size)

font_time  = load_font(68)
font_body  = load_font(30)
font_small = load_font(22)

bg = pygame.transform.scale(pygame.image.load(BG_PATH),(W,H))

critl_imgs={}
for k,p in CRITL_PATHS.items():
    try:
        critl_imgs[k]=pygame.transform.smoothscale(
            pygame.image.load(p).convert_alpha(),(170,170)
        )
    except:
        critl_imgs[k]=None

# ============================================================
# HELPERS
# ============================================================
def draw_scanlines():
    s=pygame.Surface((W,H),pygame.SRCALPHA)
    for y in range(0,H,3):
        s.fill((0,0,0,35),(0,y,W,1))
    screen.blit(s,(0,0))

def draw_edge_scan(t):
    w,h,speed=90,2,35
    x=int((t*speed)%(W+w))-w
    pulse=0.5+0.5*math.sin(t*0.8)
    col=blend(GREEN,WARN,pulse*0.25)
    pygame.draw.rect(screen,col,(x,H-13,w,h))

def draw_bar(x,y,w,h,prog,is_pause,remain,label):
    pygame.draw.rect(screen,DIM_GREEN,(x,y,w,h))
    pygame.draw.rect(screen,GREEN,(x,y,w,h),2)
    base=BLUE if is_pause else GREEN
    col=base
    if remain<=120:
        col=blend(base,WARN,1-remain/120)
    fill=int((w-4)*prog)
    if fill>0:
        pygame.draw.rect(screen,col,(x+2,y+2,fill,h-4))
    txt_col=BLACK if fill>w*0.4 else GREEN_SOFT
    l=font_small.render(label,True,txt_col)
    r=font_small.render(f"noch {fmt(remain)}",True,txt_col)
    ty=y+(h-l.get_height())//2
    screen.blit(l,(x+10,ty))
    screen.blit(r,(x+w-r.get_width()-10,ty))

def tint(color,alpha):
    s=pygame.Surface((W,H),pygame.SRCALPHA)
    s.fill((color[0],color[1],color[2],alpha))
    screen.blit(s,(0,0))

# ============================================================
# EVENT STATE
# ============================================================
active_event=None
event_start=0
event_dur=0
next_event=time.time()+random.randint(40,90)

active_quote=""
quote_until=0
next_quote=time.time()+random.randint(20,50)

# ============================================================
# MAIN LOOP
# ============================================================
while True:
    clock.tick(FPS)

    for e in pygame.event.get():
        if e.type==pygame.KEYDOWN and e.key in (pygame.K_ESCAPE,pygame.K_q):
            pygame.quit(); sys.exit()

    now=datetime.now()
    label,remain,prog=get_status(now)
    is_pause="PAUSE" in label

    screen.blit(bg,(0,0))

    # Uhr + Datum
    screen.blit(font_time.render(now.strftime("%H:%M"),True,GREEN),(60,40))
    screen.blit(font_body.render(now.strftime("%A, %d.%m.%Y"),True,GREEN_SOFT),(60,120))

    # Balken
    bar_y=H-26-18
    draw_bar(70,bar_y,W-120,26,prog,is_pause,remain,label)

    draw_edge_scan(time.time())

    # Critl Stimmung
    mood="neutral"
    if is_pause: mood="müde"
    if remain<=120 and "UNTERRICHT" in label: mood="genervt"

    mode=1
    if mood=="müde": mode=3
    if mood=="genervt": mode=2

    img=critl_imgs.get(mode)
    if img:
        screen.blit(img,(W-img.get_width()-20,bar_y-img.get_height()-14))

    # Quote
    t_now=time.time()
    if not active_quote and t_now>next_quote:
        active_quote=random.choice(CRITL_QUOTES[mood])
        quote_until=t_now+6
        next_quote=t_now+random.randint(30,60)

    if active_quote:
        screen.blit(font_small.render("CRITL: "+active_quote,True,GREEN_SOFT),
                    (60,bar_y-26))
        if t_now>quote_until:
            active_quote=""

    # Events
    if active_event is None and t_now>next_event:
        active_event=random.choice(EVENTS)
        event_start=t_now
        event_dur=random.randint(active_event["min"],active_event["max"])
        next_event=t_now+random.randint(70,140)

    if active_event:
        p=clamp((t_now-event_start)/event_dur,0,1)
        et=active_event["type"]

        if et=="scan":
            tint(ORANGE,70)
            pygame.draw.rect(screen,ORANGE,(80,220,480,20))
            pygame.draw.rect(screen,BLACK,(80,220,int(480*(1-p)),20))
        elif et=="warn":
            tint((255,80,60),50)
        elif et=="leak":
            tint((0,60,80),60)
            for _ in range(120):
                screen.set_at((random.randrange(W),random.randrange(H)),(0,210,255))
        elif et=="glitch":
            for _ in range(6):
                yy=random.randrange(H)
                hh=random.randrange(4,12)
                off=random.randrange(-20,21)
                r=pygame.Rect(0,yy,W,hh)
                piece=screen.subsurface(r).copy()
                screen.blit(piece,(off,yy))
        elif et=="teacher":
            screen.blit(font_body.render("Unterrichten ist Debugging mit Publikum.",True,WARN),(60,200))

        if t_now-event_start>=event_dur:
            active_event=None

    draw_scanlines()
    pygame.display.flip()
