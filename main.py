#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import sys
import time
import random
from datetime import datetime

# =============================
# BASIS
# =============================
W, H = 480, 320
FPS = 20

F_GREEN = (80, 255, 80)
F_DIM   = (20, 60, 20)
F_WARN  = (255, 180, 60)
F_BLUE  = (0, 180, 255)
BLACK   = (0, 0, 0)

pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
clock = pygame.time.Clock()

f_xl = pygame.font.SysFont("DejaVu Sans Mono", 48, True)
f_l  = pygame.font.SysFont("DejaVu Sans Mono", 32, True)
f_m  = pygame.font.SysFont("DejaVu Sans Mono", 26)
f_s  = pygame.font.SysFont("DejaVu Sans Mono", 20)
f_mono = pygame.font.SysFont("Courier", 26, True)

# =============================
# STUNDENPLAN
# =============================
PLAN = [
    (7,30, 8,0,  "PAUSE"),
    (8,0,  8,45, "UNTERRICHT"),
    (8,45, 8,50, "PAUSE"),
    (8,50, 9,35, "UNTERRICHT"),
    (9,35, 9,55, "PAUSE"),
    (9,55, 10,40,"UNTERRICHT"),
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
    (15,15,16,0, "UNTERRICHT"),
    (16,0, 17,0, "FEIERABEND")
]

def secs(h,m,s=0): return h*3600+m*60+s

def get_status():
    now = datetime.now()
    cur = secs(now.hour, now.minute, now.second)
    for sh,sm,eh,em,label in PLAN:
        start = secs(sh,sm)
        end   = secs(eh,em)
        if start <= cur < end:
            total = end-start
            done  = cur-start
            return label, end-cur, done/total
    return "FREIZEIT", 0, 0

def fmt(sec):
    m,s = divmod(max(0,int(sec)),60)
    return f"{m:02d}:{s:02d}"

def blend(c1,c2,t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

# =============================
# HAMSTER (SYSTEM ENTITY)
# =============================
HAMSTER = [
    "(\\__/)",
    "(•ㅅ• )   < compiling reality",
    "/ 　 づ"
]

EVENTS = [
    ["[ SYS ] SCANNING ENVIRONMENT",
     "[ OK ] REALITY STABLE",
     "[ OK ] HAMSTER AWAKE"],

    ["[ WARNING ]",
     "ANOMALY DETECTED",
     "PROBABLY YOU"],

    ["[ LEAK ]",
     "SOME DATA ESCAPED",
     "I SAW NOTHING"],

    ["[ ALERT ]",
     "MICRO NUCLEAR HOLE",
     "SIZE: IRRELEVANT"],

    ["[ SYS ]",
     "THIS IS",
     "UNNECESSARILY HARD"],

    ["[ HAMSTER ]",
     "I FIXED IT",
     "DON'T ASK HOW"],

    ["[ HAMSTER ]",
     "WHY ARE YOU STILL HERE?"],

    ["[ SYS ]",
     "EVERYTHING IS FINE",
     "STOP ASKING"]
]

active_event = None
event_until = 0
next_event  = time.time()+random.randint(30,90)

# =============================
# MAIN LOOP
# =============================
while True:
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN:
            pygame.quit(); sys.exit()

    screen.fill(BLACK)

    # Uhr
    now = datetime.now().strftime("%H:%M")
    screen.blit(f_xl.render(now,True,F_GREEN),(20,10))

    # Hamster ASCII
    y = 80
    for l in HAMSTER:
        screen.blit(f_mono.render(l,True,F_GREEN),(40,y))
        y+=28

    # Status
    label, remain, prog = get_status()
    is_pause = "PAUSE" in label

    base = F_BLUE if is_pause else F_GREEN
    color = base
    if remain <= 120:
        color = blend(base,F_WARN,1-remain/120)

    # Balken
    pygame.draw.rect(screen,F_DIM,(40,200,400,26))
    pygame.draw.rect(screen,color,(40,200,int(400*prog),26))
    txt = f"{label} – noch {fmt(remain)}"
    screen.blit(f_m.render(txt,True,F_GREEN),(40,170))

    # Zufalls-Events
    t = time.time()
    if active_event is None and t > next_event:
        active_event = random.choice(EVENTS)
        event_until = t+random.randint(4,6)
        next_event = t+random.randint(60,140)

    if active_event:
        y = 240
        for l in active_event:
            screen.blit(f_s.render(l,True,F_GREEN),(W//2-150,y))
            y+=22
        if t > event_until:
            active_event = None

    pygame.display.flip()
