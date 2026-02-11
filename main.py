#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import math
import random
from datetime import datetime

import pygame


# ============================================================
# FIXED SPECS
# ============================================================
W, H = 640, 480
FPS = 25

# Fallout-ish Palette
GREEN      = ( 80, 255,  80)
GREEN_SOFT = (120, 255, 120)
DIM_GREEN  = ( 18,  55,  18)
BLUE       = (  0, 190, 255)
WARN       = (255, 180,  60)
RED_TEXT   = (255,  90,  90)
RED_TINT   = (120,  10,  10)
BLACK      = (  0,   0,   0)

# Paths
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
BG_PATH   = os.path.join(ASSET_DIR, "bg.png")

FONT_PATH = os.path.join(ASSET_DIR, "Monofonto.ttf")  # empfohlen
# Fallback: monospace sysfont

CRITL_PATHS = {
    1: os.path.join(ASSET_DIR, "1.png"),  # neutral
    2: os.path.join(ASSET_DIR, "2.png"),  # genervt/warn
    3: os.path.join(ASSET_DIR, "3.png"),  # müde
    4: os.path.join(ASSET_DIR, "4.png"),  # arbeitet/scan/leak
}


# ============================================================
# SCHEDULE (Unterricht nummerieren)
# ============================================================
PLAN_RAW = [
    ("07:30", "08:00", "PAUSE"),
    ("08:00", "08:45", "UNTERRICHT"),
    ("08:45", "08:50", "PAUSE"),
    ("08:50", "09:35", "UNTERRICHT"),
    ("09:35", "09:55", "PAUSE"),
    ("09:55", "10:40", "UNTERRICHT"),
    ("10:40", "10:45", "PAUSE"),
    ("10:45", "11:30", "UNTERRICHT"),
    ("11:30", "11:50", "PAUSE"),
    ("11:50", "12:35", "UNTERRICHT"),
    ("12:35", "12:40", "PAUSE"),
    ("12:40", "13:25", "UNTERRICHT"),
    ("13:25", "13:35", "PAUSE"),
    ("13:35", "14:20", "UNTERRICHT"),
    ("14:20", "14:25", "PAUSE"),
    ("14:25", "15:10", "UNTERRICHT"),
    ("15:10", "15:15", "PAUSE"),
    ("15:15", "16:00", "UNTERRICHT"),
    ("16:00", "17:00", "FEIERABEND"),
]

def parse_hm(s):
    h, m = s.split(":")
    return int(h), int(m)

def to_secs(h, m, s=0):
    return h*3600 + m*60 + s

def number_lessons(plan_raw):
    n = 1
    out = []
    for a, b, label in plan_raw:
        if label.upper() == "UNTERRICHT":
            label = f"UNTERRICHT {n}"
            n += 1
        out.append((a, b, label))
    return out

PLAN = number_lessons(PLAN_RAW)

def clamp(x, a, b):
    return a if x < a else b if x > b else x

def blend(c1, c2, t):
    t = clamp(t, 0.0, 1.0)
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def fmt_mmss(seconds):
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

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
            prog = passed / total
            return label, remain, prog
    return "FREIZEIT", 0, 0.0


# ============================================================
# EVENTS (Deutsch, Critl)
# ============================================================
EVENTS = [
    {"style":"scan", "lines":[
        "[ SYS ] UMGEBUNGSSCAN LÄUFT …",
        "[ OK  ] SPEICHER STABIL",
        "[ OK  ] TEMPERATUR IM RAHMEN",
        "[ NOTE] CRITL ARBEITET. DU NICHT."
    ], "min_s":5, "max_s":8},

    {"style":"warn", "lines":[
        "[ WARNUNG ] ANOMALIE ERKANNT",
        "URSACHE: UNKLAR",
        "VERDACHT: „NUR KURZ WAS ÄNDERN“",
        "EMPFEHLUNG: HÄNDE WEG."
    ], "min_s":5, "max_s":9},

    {"style":"leak", "lines":[
        "[ LEAK ]",
        "Ein paar Daten sind entkommen.",
        "Ich habe nichts gesehen.",
        "Frag nicht nach Logfiles."
    ], "min_s":4, "max_s":7},

    {"style":"glitch", "lines":[
        "[ SYS ]",
        "DAS IST UNNÖTIG ANSTRENGEND.",
        "ABER WIR TUN SO, ALS WÄRE DAS NORMAL."
    ], "min_s":4, "max_s":6},

    {"style":"teacher", "lines":[
        "[ SCHULE ]",
        "Unterrichten ist Debugging mit Publikum.",
        "Fehler kommen wieder.",
        "Man nennt es „Lernprozess“."
    ], "min_s":6, "max_s":10},

    {"style":"exist", "lines":[
        "[ CRITL LOG ]",
        "Ich halte das hier zusammen.",
        "Du nennst es „Workflow“.",
        "Ich nenne es „Eindämmung“."
    ], "min_s":6, "max_s":10},

    {"style":"weber", "lines":[
        "[ NET ] WEBER-MODUS AKTIV",
        "Latenz: emotional",
        "Durchsatz: kaffeeabhängig",
        "Fazit: wissenschaftlich unerquicklich."
    ], "min_s":6, "max_s":9},

    {"style":"martin", "lines":[
        "Martin.",
        "Pause.",
        "Jetzt."
    ], "min_s":3, "max_s":5},
]

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

def style_color(style):
    return {
        "warn": RED_TEXT,
        "leak": BLUE,
        "scan": GREEN,
        "glitch": WARN,
        "teacher": GREEN_SOFT,
        "exist": GREEN_SOFT,
        "weber": GREEN_SOFT,
        "martin": RED_TEXT,
    }.get(style, GREEN)


# ============================================================
# GRAPHICS HELPERS
# ============================================================
def safe_load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        return None

def draw_scanlines(surface):
    sl = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 3):
        sl.fill((0, 0, 0, 35), (0, y, W, 1))
    surface.blit(sl, (0, 0))

def draw_edge_scan(surface, y, t):
    scan_w = 140
    speed = 90.0  # px/s
    x = int((t * speed) % (W + scan_w)) - scan_w
    pulse = 0.5 + 0.5 * math.sin(t * 2.0)
    col = blend(GREEN, WARN, pulse * 0.35)
    pygame.draw.rect(surface, col, (x, y, scan_w, 3))

def glitch_slices(surface):
    for _ in range(10):
        y = random.randrange(H)
        h = random.randrange(4, 14)
        off = random.randrange(-28, 29)
        r = pygame.Rect(0, y, W, h)
        piece = surface.subsurface(r).copy()
        surface.blit(piece, (off, y))

def draw_event_effect(style, surface, t):
    if style == "warn":
        a = 55 + int(35 * (0.5 + 0.5 * math.sin(t * 6)))
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((RED_TINT[0], RED_TINT[1], RED_TINT[2], a))
        surface.blit(ov, (0, 0))

    elif style == "scan":
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 35, 0, 70))
        y = int((t * 120) % H)
        pygame.draw.rect(ov, (120, 255, 120, 90), (0, y, W, 10))
        surface.blit(ov, (0, 0))

    elif style == "leak":
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 30, 40, 60))
        for _ in range(180):
            ov.set_at((random.randrange(W), random.randrange(H)), (0, 210, 255, 90))
        surface.blit(ov, (0, 0))

    elif style == "glitch":
        glitch_slices(surface)

def draw_wrapped_text(surface, text, font, color, x, y, max_width, line_height):
    words = text.split(" ")
    line = ""
    cy = y
    for w in words:
        test = line + w + " "
        if font.size(test)[0] <= max_width:
            line = test
        else:
            surface.blit(font.render(line, True, color), (x, cy))
            cy += line_height
            line = w + " "
    if line:
        surface.blit(font.render(line, True, color), (x, cy))
        cy += line_height
    return cy

def draw_progress_bar(surface, x, y, w, h, progress, is_pause, remain_s):
    pygame.draw.rect(surface, DIM_GREEN, (x, y, w, h))
    pygame.draw.rect(surface, GREEN, (x, y, w, h), 2)

    base = BLUE if is_pause else GREEN
    fill = base
    if remain_s <= 120:
        t = 1.0 - (remain_s / 120.0)
        fill = blend(base, WARN, t)

    fill_w = int((w - 4) * clamp(progress, 0.0, 1.0))
    if fill_w > 0:
        pygame.draw.rect(surface, fill, (x + 2, y + 2, fill_w, h - 4))

def draw_event_box(surface, lines, color, safe_rect):
    # safe_rect: where the event box is allowed to exist
    x, y, w, h = safe_rect
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 120))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, color, (x, y, w, h), 2)

    ty = y + 12
    for line in lines:
        surf = font_small.render(line, True, color)
        surface.blit(surf, (x + 14, ty))
        ty += 24
        if ty > y + h - 20:
            break


# ============================================================
# INIT PYGAME + ASSETS
# ============================================================
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
clock = pygame.time.Clock()

def load_font(size, bold=False):
    try:
        return pygame.font.Font(FONT_PATH, size)
    except Exception:
        return pygame.font.SysFont("monospace", size, bold=bold)

font_time  = load_font(72, True)
font_h2    = load_font(30)
font_body  = load_font(24)
font_quote = load_font(18)   # kleiner: Quotes passen immer
font_small = load_font(20)

bg = None
if os.path.exists(BG_PATH):
    try:
        bg = pygame.image.load(BG_PATH).convert()
        bg = pygame.transform.scale(bg, (W, H))
    except Exception:
        bg = None

CRITL_SIZE = (170, 170)
critl_imgs = {k: safe_load_image(p, CRITL_SIZE) for k, p in CRITL_PATHS.items()}

# ============================================================
# BOOT
# ============================================================
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
BOOT_DURATION = 5.5
BOOT_SPEED = 22  # chars per second

# ============================================================
# STATE
# ============================================================
state = "BOOT"
boot_start = time.time()

active_event = None
event_until = 0.0
next_event = time.time() + random.randint(45, 95)

active_comment = ""
comment_until = 0.0
next_comment = time.time() + random.randint(25, 55)

critl_mode = 1  # 1 neutral, 2 annoyed/warn, 3 tired, 4 working

def choose_critl_mode(label, event_style=None):
    if event_style in ("warn", "glitch"):
        return 2
    if event_style in ("scan", "leak"):
        return 4
    u = label.upper()
    now = datetime.now()
    if "PAUSE" in u:
        return 3
    if now.hour >= 15:
        return 3
    if "FEIER" in u:
        return 3
    return 1

def draw_boot():
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(BLACK)

    elapsed = time.time() - boot_start
    chars_budget = int(elapsed * BOOT_SPEED)

    y = 70
    for line in BOOT_LINES:
        if chars_budget <= 0:
            break
        take = min(len(line), chars_budget)
        text = line[:take]
        chars_budget -= take
        chars_budget -= 1
        screen.blit(font_body.render(text, True, GREEN_SOFT), (60, y))
        y += 28

    # simple progress
    t = clamp(elapsed / BOOT_DURATION, 0.0, 1.0)
    pygame.draw.rect(screen, DIM_GREEN, (60, H - 70, W - 120, 18))
    pygame.draw.rect(screen, GREEN, (60, H - 70, int((W - 120) * t), 18))

    # subtle edge scan at bottom
    draw_edge_scan(screen, H - 18, time.time())

    draw_scanlines(screen)

    return elapsed >= BOOT_DURATION

def draw_home():
    global active_event, event_until, next_event
    global active_comment, comment_until, next_comment
    global critl_mode

    t_now = time.time()

    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(BLACK)

    now = datetime.now()
    label, remain_s, prog = get_status(now)
    is_pause = "PAUSE" in label.upper()

    # ---- TOP LEFT: TIME + DATE (wieder drin)
    time_surf = font_time.render(now.strftime("%H:%M"), True, GREEN)
    screen.blit(time_surf, (60, 35))

    date_text = now.strftime("%A, %d.%m.%Y")
    date_surf = font_body.render(date_text, True, GREEN_SOFT)
    screen.blit(date_surf, (60, 35 + time_surf.get_height() + 6))

    # ---- STATUS TEXT (unter Datum)
    status_txt = f"{label}  |  noch {fmt_mmss(remain_s)}"
    screen.blit(font_h2.render(status_txt, True, GREEN_SOFT), (60, 160))

    # ---- BOTTOM-ANCHORED PROGRESS BAR (immer unten)
    bar_h = 26
    bar_x = 60
    bar_w = W - 120
    bar_y = H - bar_h - 18  # wirklich unten

    draw_progress_bar(screen, bar_x, bar_y, bar_w, bar_h, prog, is_pause, remain_s)

    # ---- EDGE SCAN (dezent, unten, links->rechts, farbvar.)
    draw_edge_scan(screen, H - 18, t_now)

    # ---- Critl Position: unten rechts, aber NICHT über Balken
    # Critl sitzt "im Bild", knapp über dem Balken, ohne Text zu überdecken.
    style = active_event["style"] if active_event else None
    critl_mode = choose_critl_mode(label, style)

    critl_img = critl_imgs.get(critl_mode) or critl_imgs.get(1)
    if critl_img:
        cx = W - critl_img.get_width() - 20
        cy = bar_y - critl_img.get_height() - 14  # über dem Balken
        screen.blit(critl_img, (cx, cy))

        # Glas/CRT-Einbettung
        glass = pygame.Surface(critl_img.get_size(), pygame.SRCALPHA)
        glass.fill((0, 0, 0, 45))
        screen.blit(glass, (cx, cy))

    # ---- Comments (kleiner + wrap), ohne Critl zu überdecken
    if not active_comment and t_now > next_comment:
        active_comment = random.choice(COMMENTS)
        comment_until = t_now + random.randint(4, 7)
        next_comment = t_now + random.randint(35, 80)

    if active_comment:
        # safe width: leave room for Critl area
        max_w = W - 320
        draw_wrapped_text(
            screen,
            f"CRITL: {active_comment}",
            font_quote,
            GREEN_SOFT,
            x=60,
            y=198,
            max_width=max_w,
            line_height=22
        )
        if t_now > comment_until:
            active_comment = ""

    # ---- Events (selten)
    if active_event is None and t_now > next_event:
        active_event = pick_event(label)
        dur = random.randint(active_event["min_s"], active_event["max_s"])
        event_until = t_now + dur
        next_event = t_now + random.randint(80, 160)

    # ---- Event effects + box (in safe zone, niemals über Critl/Balken)
    if active_event:
        st = active_event["style"]
        draw_event_effect(st, screen, t_now)

        # safe rect for event box:
        # left side area, not touching Critl and not touching bottom bar
        safe_x = 60
        safe_y = 240
        safe_w = W - 60 - 260   # leaves space for Critl on right
        safe_h = bar_y - safe_y - 12  # ends above the bar
        safe_rect = (safe_x, safe_y, max(200, safe_w), max(80, safe_h))

        col = style_color(st)
        draw_event_box(screen, active_event["lines"], col, safe_rect)

        if t_now > event_until:
            active_event = None

    # ---- Scanlines ALWAYS
    draw_scanlines(screen)


# ============================================================
# MAIN LOOP
# ============================================================
while True:
    clock.tick(FPS)

    # Quit keys
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_q):
                pygame.quit()
                sys.exit()

    if state == "BOOT":
        if draw_boot():
            state = "HOME"
    else:
        draw_home()

    pygame.display.flip()