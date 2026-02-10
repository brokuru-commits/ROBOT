#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import math
from datetime import datetime

import pygame

# =========================
# FIXED SPECS
# =========================
W, H = 640, 480
FPS = 25

# Fallout-ish palette
GREEN      = ( 80, 255,  80)
GREEN_SOFT = (120, 255, 120)
DIM_GREEN  = ( 18,  55,  18)
BLUE       = (  0, 190, 255)
WARN       = (255, 180,  60)
RED_TINT   = (120,  10,  10)
WHITE      = (235, 255, 235)
BLACK      = (  0,   0,   0)

# Assets
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
BG_PATH   = os.path.join(ASSET_DIR, "bg.png")

# Critl images (optional, but expected)
CRITL_PATHS = {
    1: os.path.join(ASSET_DIR, "1.png"),  # neutral / idle
    2: os.path.join(ASSET_DIR, "2.png"),  # genervt / warn
    3: os.path.join(ASSET_DIR, "3.png"),  # müde
    4: os.path.join(ASSET_DIR, "4.png"),  # arbeitet / kaffee
}

# =========================
# SCHEDULE
# =========================
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

def parse_hm(s):
    h, m = s.split(":")
    return int(h), int(m)

def to_secs(h, m, s=0):
    return h*3600 + m*60 + s

def number_lessons(plan_raw):
    out = []
    n = 1
    for a, b, label in plan_raw:
        if label.upper() == "UNTERRICHT":
            label = f"UNTERRICHT {n}"
            n += 1
        out.append((a, b, label))
    return out

PLAN = number_lessons(PLAN_RAW)

def get_status(now):
    cur = to_secs(now.hour, now.minute, now.second)
    for a, b, label in PLAN:
        sh, sm = parse_hm(a)
        eh, em = parse_hm(b)
        start = to_secs(sh, sm)
        end   = to_secs(eh, em)
        if start <= cur < end:
            total = max(1, end - start)
            passed = cur - start
            remain = end - cur
            progress = passed / total
            return label, remain, progress
    return "FREIZEIT", 0, 0.0

def fmt_mmss(seconds):
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def clamp(x, a, b):
    return a if x < a else b if x > b else x

def blend(c1, c2, t):
    t = clamp(t, 0.0, 1.0)
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

# =========================
# CRITL EVENTS (Deutsch, sarkastisch, nerdig)
# =========================
EVENTS = [
    {
        "style": "scan",
        "lines": [
            "[ SYS ] UMGEBUNGSSCAN LÄUFT …",
            "[ OK  ] SPEICHER STABIL",
            "[ OK  ] TEMPERATUR IM RAHMEN",
            "[ NOTE] CRITL ARBEITET. DU NICHT."
        ],
        "min_s": 4, "max_s": 7
    },
    {
        "style": "warn",
        "lines": [
            "[ WARNUNG ] ANOMALIE ERKANNT",
            "URSACHE: UNKLAR",
            "VERDACHT: „NUR KURZ WAS ÄNDERN“",
            "EMPFEHLUNG: HÄNDE WEG."
        ],
        "min_s": 5, "max_s": 8
    },
    {
        "style": "leak",
        "lines": [
            "[ LEAK ]",
            "Ein paar Daten sind entkommen.",
            "Ich habe nichts gesehen.",
            "Frag nicht nach Logfiles."
        ],
        "min_s": 4, "max_s": 7
    },
    {
        "style": "glitch",
        "lines": [
            "[ SYS ]",
            "DAS IST UNNÖTIG ANSTRENGEND.",
            "ABER WIR TUN SO, ALS WÄRE DAS NORMAL."
        ],
        "min_s": 4, "max_s": 6
    },
    {
        "style": "exist",
        "lines": [
            "[ CRITL LOG ]",
            "Ich halte das hier zusammen.",
            "Du nennst es „Workflow“.",
            "Ich nenne es „Eindämmung“."
        ],
        "min_s": 5, "max_s": 9
    },
    {
        "style": "weber",
        "lines": [
            "[ NET ] WEBER-MODUS AKTIV",
            "Latenz: emotional",
            "Durchsatz: kaffeeabhängig",
            "Fazit: wissenschaftlich unerquicklich."
        ],
        "min_s": 5, "max_s": 8
    },
    {
        "style": "teacher",
        "lines": [
            "[ SCHULE ]",
            "Unterrichten ist Debugging mit Publikum.",
            "Fehler kommen wieder.",
            "Man nennt es „Lernprozess“."
        ],
        "min_s": 5, "max_s": 9
    },
    {
        "style": "martin",
        "lines": [
            "Martin.",
            "Pause.",
            "Jetzt."
        ],
        "min_s": 3, "max_s": 5
    },
]

# Rare, short comments (no big overlay)
COMMENTS = [
    "System stabil. Auffällig stabil.",
    "Alles läuft. Das macht mich misstrauisch.",
    "Ich habe etwas repariert, das du nicht bemerkt hast.",
    "Geplant war Ordnung. Eingetreten ist Alltag.",
    "Scheitern war eine Option. Wir haben sie ignoriert.",
    "Das Problem ist gelöst. Die Ursache bleibt menschlich.",
    "Pause erhöht Stabilität. Theoretisch.",
    "Ich sage nicht „Ich hab’s gesagt“. Innerlich schon.",
    "HEUM-Tec läuft. Trotz Realität.",
]

def pick_event(label):
    u = label.upper()
    if "PAUSE" in u:
        pool = [e for e in EVENTS if e["style"] in ("scan","leak","exist","martin","weber")]
    elif "UNTERRICHT" in u:
        pool = [e for e in EVENTS if e["style"] in ("teacher","warn","glitch","exist","weber")]
    elif "FEIER" in u:
        pool = [e for e in EVENTS if e["style"] in ("exist","leak","scan")]
    else:
        pool = EVENTS
    return random.choice(pool) if pool else random.choice(EVENTS)

# =========================
# EFFECT LAYERS
# =========================
def overlay_tint(color_rgb, alpha):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((color_rgb[0], color_rgb[1], color_rgb[2], alpha))
    return ov

def draw_scan_sweep():
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    base_alpha = 70
    ov.fill((0, 35, 0, base_alpha))
    y = int((time.time() * 120) % H)
    pygame.draw.rect(ov, (120, 255, 120, 90), (0, y, W, 10))
    screen.blit(ov, (0, 0))

def draw_leak_noise():
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 30, 40, 60))
    for _ in range(180):
        ov.set_at((random.randrange(W), random.randrange(H)), (0, 210, 255, 90))
    screen.blit(ov, (0, 0))

def glitch_slices():
    # subtle horizontal slice shifts
    for _ in range(10):
        y = random.randrange(H)
        h = random.randrange(4, 14)
        off = random.randrange(-28, 29)
        r = pygame.Rect(0, y, W, h)
        piece = screen.subsurface(r).copy()
        screen.blit(piece, (off, y))

def draw_scanlines():
    sl = pygame.Surface((W, H), pygame.SRCALPHA)
    # every 3px one dark line
    for y in range(0, H, 3):
        sl.fill((0, 0, 0, 35), (0, y, W, 1))
    screen.blit(sl, (0, 0))

# =========================
# UI DRAW HELPERS
# =========================
def draw_progress_bar(x, y, w, h, progress, is_pause, remain_s):
    # background + frame
    pygame.draw.rect(screen, DIM_GREEN, (x, y, w, h))
    pygame.draw.rect(screen, GREEN, (x, y, w, h), 2)

    # base fill color
    base = BLUE if is_pause else GREEN

    # smooth warning shift for last 120 seconds
    if remain_s <= 120:
        t = 1.0 - (remain_s / 120.0)
        fill = blend(base, WARN, t)
    else:
        fill = base

    fill_w = int((w - 4) * clamp(progress, 0.0, 1.0))
    if fill_w > 0:
        pygame.draw.rect(screen, fill, (x + 2, y + 2, fill_w, h - 4))

def safe_load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        return None

# =========================
# INIT GRAPHICS
# =========================
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Fonts (bigger for readability)
f_time = pygame.font.SysFont("DejaVu Sans Mono", 68, True)
f_h1   = pygame.font.SysFont("DejaVu Sans Mono", 34, True)
f_h2   = pygame.font.SysFont("DejaVu Sans Mono", 28, True)
f_body = pygame.font.SysFont("DejaVu Sans Mono", 24)
f_small= pygame.font.SysFont("DejaVu Sans Mono", 20)

# Background
bg = None
if os.path.exists(BG_PATH):
    try:
        bg = pygame.image.load(BG_PATH).convert()
        bg = pygame.transform.scale(bg, (W, H))
    except Exception:
        bg = None

# Critl image cache
CRITL_SIZE = (170, 170)  # sized to never cover text
critl_imgs = {}
for k, p in CRITL_PATHS.items():
    critl_imgs[k] = safe_load_image(p, CRITL_SIZE)

# =========================
# BOOT SEQUENCE (Deutsch, Critl kennt Martin + HEUM-Tec)
# =========================
BOOT_LINES = [
    "HEUM-Tec Systemstart",
    "-------------------",
    "Initialisiere Kernmodule …",
    "Lade Zeitlogik …",
    "Überprüfe Realität …",
    "Geduld nicht gefunden.",
    "",
    "Guten Morgen, Martin.",
    "",
    "Critl ist online.",
    "Ich kümmere mich darum.",
]
BOOT_DURATION = 5.5  # seconds total
BOOT_TYPE_SPEED = 22  # chars/sec

# =========================
# STATE
# =========================
state = "BOOT"
boot_start = time.time()

active_event = None
event_until = 0.0
next_event = time.time() + random.randint(45, 95)

active_comment = ""
comment_until = 0.0
next_comment = time.time() + random.randint(25, 55)

# Critl mood switching
critl_mode = 1  # 1 neutral, 2 annoyed, 3 tired, 4 working

def choose_critl_mode(label, event_style=None):
    # event overrides
    if event_style in ("warn", "glitch"):
        return 2
    if event_style in ("scan", "leak"):
        return 4

    u = label.upper()
    now = datetime.now()
    # tired in pauses or late afternoon
    if "PAUSE" in u:
        return 3
    if now.hour >= 15:
        return 3
    if "FEIER" in u:
        return 3
    return 1

def draw_boot():
    # bg
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(BLACK)

    elapsed = time.time() - boot_start

    # typewriter rendering by total characters budget
    chars_budget = int(elapsed * BOOT_TYPE_SPEED)

    y = 60
    for line in BOOT_LINES:
        # consume budget
        if chars_budget <= 0:
            break

        # render partial line
        take = min(len(line), chars_budget)
        text = line[:take]
        chars_budget -= take
        # also consume newline "pause" lightly
        chars_budget -= 1

        surf = f_body.render(text, True, GREEN_SOFT)
        screen.blit(surf, (60, y))
        y += 28

    # progress bar
    t = clamp(elapsed / BOOT_DURATION, 0.0, 1.0)
    pygame.draw.rect(screen, DIM_GREEN, (60, H-90, W-120, 18))
    pygame.draw.rect(screen, GREEN, (60, H-90, int((W-120)*t), 18))

    draw_scanlines()

    if elapsed >= BOOT_DURATION:
        return True
    return False

def draw_event_box(lines, color):
    # draw a readable overlay box that does NOT collide with Critl image (bottom-right)
    box_x = 60
    box_w = W - 60 - 240  # leaves space for Critl (right side)
    box_y = 210
    box_h = 150

    # background panel
    panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 120))
    screen.blit(panel, (box_x, box_y))

    # border
    pygame.draw.rect(screen, color, (box_x, box_y, box_w, box_h), 2)

    y = box_y + 12
    for line in lines:
        surf = f_small.render(line, True, color)
        screen.blit(surf, (box_x + 14, y))
        y += 24
        if y > box_y + box_h - 20:
            break

def draw_home():
    global active_event, event_until, next_event
    global active_comment, comment_until, next_comment
    global critl_mode

    # Background
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(BLACK)

    now = datetime.now()
    label, remain_s, prog = get_status(now)

    # Time
    t_surf = f_time.render(now.strftime("%H:%M"), True, GREEN)
    screen.blit(t_surf, (60, 40))

    # Status line
    is_pause = "PAUSE" in label.upper()
    status_txt = f"{label}  |  noch {fmt_mmss(remain_s)}"
    s_surf = f_h2.render(status_txt, True, GREEN_SOFT)
    screen.blit(s_surf, (60, 125))

    # Progress bar
    draw_progress_bar(
        x=60, y=165, w=W-120, h=26,
        progress=prog, is_pause=is_pause, remain_s=remain_s
    )

    # Comment system (short, rare, below bar)
    t_now = time.time()
    if not active_comment and t_now > next_comment:
        active_comment = random.choice(COMMENTS)
        comment_until = t_now + random.randint(4, 7)
        next_comment = t_now + random.randint(35, 80)

    if active_comment:
        c_surf = f_body.render(f"CRITL: {active_comment}", True, GREEN_SOFT)
        screen.blit(c_surf, (60, 200))
        if t_now > comment_until:
            active_comment = ""

    # Event trigger (rare)
    if active_event is None and t_now > next_event:
        active_event = pick_event(label)
        dur = random.randint(active_event["min_s"], active_event["max_s"])
        event_until = t_now + dur
        next_event = t_now + random.randint(80, 160)

    # Decide Critl mood (event can override)
    style = active_event["style"] if active_event else None
    critl_mode = choose_critl_mode(label, style)

    # Critl image (must not cover text): bottom-right
    critl_img = critl_imgs.get(critl_mode) or critl_imgs.get(1)
    if critl_img:
        cx = W - critl_img.get_width() - 40
        cy = H - critl_img.get_height() - 45
        screen.blit(critl_img, (cx, cy))

        # subtle "glass" overlay so it feels integrated
        glass = pygame.Surface((critl_img.get_width(), critl_img.get_height()), pygame.SRCALPHA)
        glass.fill((0, 0, 0, 35))
        screen.blit(glass, (cx, cy))

    # Event effects + box
    if active_event:
        st = active_event["style"]

        # stronger screen effects (but controlled)
        if st == "warn":
            # red tint pulse
            a = 55 + int(35 * (0.5 + 0.5*math.sin(t_now * 6)))
            screen.blit(overlay_tint(RED_TINT, a), (0, 0))
        elif st == "scan":
            draw_scan_sweep()
        elif st == "leak":
            draw_leak_noise()
        elif st == "glitch":
            # one quick slice glitch
            glitch_slices()

        # event box (color by style)
        col = {
            "warn": (255, 80, 80),
            "scan": GREEN,
            "leak": BLUE,
            "glitch": WARN,
            "exist": GREEN_SOFT,
            "weber": GREEN_SOFT,
            "teacher": GREEN_SOFT,
            "martin": (255, 110, 110),
        }.get(st, GREEN)

        draw_event_box(active_event["lines"], col)

        if t_now > event_until:
            active_event = None

    # Always-on scanlines
    draw_scanlines()

# =========================
# MAIN LOOP
# =========================
while True:
    clock.tick(FPS)

    # Basic input (ESC/Q quits). Touch not required for this UI.
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_q):
                pygame.quit()
                sys.exit()

    if state == "BOOT":
        done = draw_boot()
        if done:
            state = "HOME"
    else:
        draw_home()

    pygame.display.flip()