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

GREEN      = (80, 255, 80)
GREEN_SOFT = (120, 255, 120)
DIM_GREEN  = (18, 55, 18)
BLUE       = (0, 190, 255)
WARN       = (255, 180, 60)
ORANGE     = (255, 150, 50)
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)

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
        if s<=cur<e: return l, e-cur, (cur-s)/(e-s)
    return "FEIERABEND",0,1.0

def fmt(sec):
    m,s = divmod(int(sec),60); return f"{m:02d}:{s:02d}"

def clamp(x,a,b): return a if x<a else b if x>b else x

def blend(c1,c2,t): return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

# ============================================================
# SPRÜCHE & LÄNGERE EVENTS
# ============================================================
CRITL_QUOTES = {
    "neutral": ["System läuft. Du auch?", "Alles stabil. Zu stabil...", "Guck nicht so, ich arbeite!"],
    "genervt": ["Nein Martin, einfach nein.", "Wartung? Mach ich später.", "Ich bin ein Bot, kein Wunderheiler."],
    "müde": ["Energie bei 2%. Wie du.", "Pause? Jetzt?", "Ich simuliere nur noch Bereitschaft."],
    "arbeit": ["Scan läuft. IQ nicht gefunden.", "Analysiere... Langeweile erkannt.", "Effizienz ist keine Option."]
}

# EVENT ZEITEN MASSIV ERHÖHT (20-45 Sekunden)
EVENTS = [
    {"type":"rads",     "min":25, "max":45},
    {"type":"critical", "min":30, "max":45},
    {"type":"vats",     "min":20, "max":40},
    {"type":"error",    "min":15, "max":30},
    {"type":"chem",     "min":20, "max":35},
    {"type":"vision",   "min":20, "max":40},
    {"type":"censored", "min":20, "max":45},
    {"type":"emote",    "min":10, "max":15}
]

EVENT_QUOTES = {
    "rads": "STRAHLUNGS-ALARM! Deine Butterbrote leuchten gleich.",
    "critical": "KERN-SCHMELZE! Verlass das Gebäude. Jetzt.",
    "vats": "V.A.T.S. AKTIV. Ziel: Die nächste Kaffeemaschine.",
    "error": "FATAL ERROR! Wer hat das System getreten?",
    "chem": "PSYCHO-RAUSCH! Alles so schön bunt hier...",
    "vision": "NACHTSICHT AN. Wer hat das Licht ausgemacht?",
    "censored": "ZENSUR! Du weißt zu viel für einen Schüler."
}

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

font_time, font_body, font_small = load_font(75), load_font(32), load_font(24)

try: bg = pygame.transform.scale(pygame.image.load(BG_PATH),(W,H))
except: bg = pygame.Surface((W,H)); bg.fill(BLACK)

critl_imgs={}
for k,p in CRITL_PATHS.items():
    try: critl_imgs[k]=pygame.transform.smoothscale(pygame.image.load(p).convert_alpha(),(225,225))
    except: critl_imgs[k]=None

def draw_text_wrapped(text, x, y, font, color, max_w=580):
    words = text.split(' '); lines = []; cur_l = ""
    for w_ in words:
        if font.size(cur_l + w_)[0] < max_w: cur_l += w_ + " "
        else: lines.append(cur_l); cur_l = w_ + " "
    lines.append(cur_l)
    for i, l in enumerate(lines):
        screen.blit(font.render(l.strip(), True, color), (x, y + i * (font.get_height() + 2)))

def draw_bar(x, y, w, h, prog, is_pause, remain, label):
    pygame.draw.rect(screen, DIM_GREEN, (x, y, w, h))
    pygame.draw.rect(screen, GREEN, (x, y, w, h), 3)
    col = BLUE if is_pause else (blend(GREEN, WARN, 1-remain/120) if remain <= 120 else GREEN)
    fill_w = int((w - 6) * prog)
    if fill_w > 0: pygame.draw.rect(screen, col, (x + 3, y + 3, fill_w, h - 6))
    txt = f"{label} | NOCH {fmt(remain)}" if remain > 0 else label
    sl, sd = font_small.render(txt, True, GREEN_SOFT), font_small.render(txt, True, BLACK)
    tx, ty = x + (w-sl.get_width())//2, y + (h-sl.get_height())//2
    screen.set_clip(pygame.Rect(x+3, y+3, fill_w, h-6))
    screen.blit(sd, (tx, ty))
    screen.set_clip(pygame.Rect(x+3+fill_w, y+3, w-6-fill_w, h-6))
    screen.blit(sl, (tx, ty))
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
    start_x = W - 140
    y = 40
    wifi_val = int(140 + 115 * math.sin(t * 4))
    wifi_col = (0, 180, 255, wifi_val)
    s_wifi = pygame.Surface((34, 34), pygame.SRCALPHA)
    for i in range(3):
        pygame.draw.arc(s_wifi, wifi_col, (5+i*4, 8+i*4, 24-i*8, 24-i*8), math.pi/4, 3*math.pi/4, 2)
    screen.blit(s_wifi, (start_x, y))
    rad_val = int(140 + 115 * math.sin(t * 2))
    rad_col = (255, 170, 0, rad_val)
    s_rad = pygame.Surface((34, 34), pygame.SRCALPHA)
    c = (17, 17)
    pygame.draw.circle(s_rad, rad_col, c, 4)
    for i in range(3):
        ang = i * (2 * math.pi / 3) - (math.pi / 2)
        p1 = (c[0] + 14 * math.cos(ang - 0.5), c[1] + 14 * math.sin(ang - 0.5))
        p2 = (c[0] + 14 * math.cos(ang + 0.5), c[1] + 14 * math.sin(ang + 0.5))
        pygame.draw.polygon(s_rad, rad_col, [c, p1, p2])
    screen.blit(s_rad, (start_x + 45, y))
    bolt_col = (255, 255, 100, 255) if random.random() > 0.92 else (140, 140, 0, 180)
    s_bolt = pygame.Surface((34, 34), pygame.SRCALPHA)
    pts = [(17, 4), (24, 16), (17, 16), (20, 30), (10, 16), (17, 16)]
    pygame.draw.polygon(s_bolt, bolt_col, pts)
    screen.blit(s_bolt, (start_x + 90, y))

# ============================================================
# MAIN LOOP
# ============================================================
active_event, ev_start, ev_dur = None, 0, 0
next_event, active_quote, q_until, next_quote = time.time()+30, "", 0, time.time()+20
active_face, last_face_change = "(o_o)", 0

while True:
    t_now = time.time(); clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q): pygame.quit(); sys.exit()

    now = datetime.now()
    label, remain, prog = get_status(now)
    is_p = "PAUSE" in label or "VORBEREITUNG" in label
    
    # 1. Immer Hintergrund zeichnen
    screen.blit(bg, (0, 0))

    # --- EVENT LOGIK (HOMESCREEN AUSBLENDEN) ---
    if active_event:
        p_ev = clamp((t_now - ev_start) / ev_dur, 0, 1)
        et = active_event["type"]

        if et == "rads":
            tint((0, 255, 0), 60) # Hintergrund Grün
            wave_y = int((t_now * 150) % H)
            pygame.draw.rect(screen, (0, 255, 0, 40), (0, wave_y, W, 60))
            tint((0, 255, 0), int(30 + 20 * math.sin(t_now * 10)))
            for _ in range(250): screen.set_at((random.randrange(W), random.randrange(H)), GREEN)

        elif et == "critical":
            tint((100, 0, 0), 80) # Hintergrund Dunkelrot
            shake = int(2 + 25 * p_ev)
            ox, oy = random.randint(-shake, shake), random.randint(-shake, shake)
            screen.blit(screen.copy(), (ox, oy))
            if math.sin(t_now * (5 + 20 * p_ev)) > 0: tint((255, 0, 0), int(40 + 60 * p_ev))
            s_a = font_time.render("ALARM", True, WHITE)
            screen.blit(s_a, (W//2-s_a.get_width()//2+ox, H//2-60+oy))

        elif et == "vats":
            tint((0, 0, 100), 50) # Hintergrund Dunkelblau
            pygame.draw.rect(screen, BLUE, (0,0,W,H), 12)
            for i in range(0, W, 20): pygame.draw.line(screen, (0, 50, 150), (i, 0), (i, H), 1)
            for i in range(0, H, 20): pygame.draw.line(screen, (0, 50, 150), (0, i), (W, i), 1)
            v_rad = int(250 * p_ev)
            if v_rad < 5: v_rad = 5
            thick = int(2 + 4 * math.sin(t_now * 5))
            if thick < 1: thick = 1
            pygame.draw.circle(screen, BLUE, (W//2,H//2), v_rad, thick)
            for _ in range(3):
                tx, ty = random.randint(50, W-150), random.randint(50, H-100)
                pygame.draw.rect(screen, BLUE, (tx, ty, 100, 40), 2)
                perc = font_small.render(f"{random.randint(10,99)}%", True, BLUE)
                screen.blit(perc, (tx + 5, ty + 5))
            pygame.draw.line(screen, WHITE, (W//2-20, H//2), (W//2+20, H//2), 2)
            pygame.draw.line(screen, WHITE, (W//2, H//2-20), (W//2, H//2+20), 2)

        elif et == "error":
            screen.fill((0, 0, 150)) # Vollflächig Blau
            header = font_body.render("*** TERMINAL ERROR ***", True, WHITE)
            screen.blit(header, (W//2 - header.get_width()//2, 40))
            line_count = int(p_ev * 12)
            for i in range(line_count):
                addr = f"0x00{random.randint(1000, 9999)}: CRITICAL_MEMORY_CORRUPTION"
                txt = font_small.render(addr, True, WHITE)
                screen.blit(txt, (40, 100 + i * 25))
            if int(t_now * 4) % 2 == 0:
                pygame.draw.rect(screen, WHITE, (40, 100 + line_count * 25, 15, 20))
            draw_text_wrapped("SYSTEM REBOOT IN PROGRESS...", 40, H-80, font_small, WARN)

        elif et == "chem":
            r = int(127 + 127 * math.sin(t_now * 4))
            g = int(127 + 127 * math.sin(t_now * 4 + 2))
            b = int(127 + 127 * math.sin(t_now * 4 + 4))
            tint((r, g, b), 120) # Starke wechselnde Tönung

        elif et == "vision":
            tint((150, 255, 150), 160) # Hellgrün Überstrahlt
            pygame.draw.circle(screen, BLACK, (0, 0), 120, 0)
            pygame.draw.circle(screen, BLACK, (W, 0), 120, 0)
            pygame.draw.circle(screen, BLACK, (0, H), 120, 0)
            pygame.draw.circle(screen, BLACK, (W, H), 120, 0)

        elif et == "censored":
            tint((20, 10, 0), 200) # Fast Schwarz-Orange
            for i in range(0, H, 40):
                off = int(math.sin(t_now * 5 + i) * 20)
                if (i // 40) % 2 == 0: pygame.draw.rect(screen, BLACK, (off, i, W, 25))
            stempel = font_time.render("REDACTED", True, (200, 0, 0))
            screen.blit(stempel, (W//2 - stempel.get_width()//2, H//2 - stempel.get_height()//2))

        elif et == "emote":
            ei = critl_imgs.get(random.randint(1,4))
            if ei: screen.blit(pygame.transform.scale(ei, (W,H)), (0,0))

        # Event Quote (Wird während des Events angezeigt)
        if et != "emote" and et in EVENT_QUOTES:
            draw_text_wrapped(EVENT_QUOTES[et], 40, 40, font_small, WHITE)

        if t_now - ev_start >= ev_dur: active_event = None

    else:
        # --- HOMESCREEN DASHBOARD (NUR WENN KEIN EVENT) ---
        screen.blit(font_time.render(now.strftime("%H:%M"), True, GREEN), (30, 30))
        draw_status_icons(t_now)
        wd_names = {"Monday":"MONTAG","Tuesday":"DIENSTAG","Wednesday":"MITTWOCH","Thursday":"DONNERSTAG","Friday":"FREITAG","Saturday":"SAMSTAG","Sunday":"SONNTAG"}
        screen.blit(font_body.render(f"{wd_names.get(now.strftime('%A'),'TAG')}, {now.strftime('%d.%m.')}", True, GREEN_SOFT), (35, 110))

        if t_now - last_face_change > 5:
            active_face = random.choice(["(o_o)", "[O.O]", "(^.^)", "<o.o>", "( -_-)", "[(X)]"])
            last_face_change = t_now
        screen.blit(font_body.render(active_face, True, GREEN), (35, 180))

        draw_bar(20, H-80, 600, 45, prog, is_p, remain, label)

        mood = "müde" if is_p else ("genervt" if remain <= 120 else "neutral")
        c_idx = 1 if mood=="neutral" else (2 if mood=="genervt" else 3)
        img = critl_imgs.get(c_idx)
        if img: screen.blit(img, (W - 240, H - 335))

        if not active_quote and t_now > next_quote:
            active_quote, q_until, next_quote = random.choice(CRITL_QUOTES[mood]), t_now+6, t_now+random.randint(30,60)
        if active_quote: draw_text_wrapped("CRITL: "+active_quote, 35, H-130, font_small, GREEN_SOFT)

    # --- GLOBALE EFFEKTE ---
    draw_edge_scan(t_now)
    s_lines = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 6):
        pygame.draw.line(s_lines, (0, 10, 0, 40), (0, y), (W, y), 1)
    screen.blit(s_lines, (0,0))

    # Event Timer Check
    if not active_event and t_now > next_event:
        active_event = random.choice(EVENTS)
        ev_start, ev_dur = t_now, random.randint(active_event["min"], active_event["max"])
        next_event = t_now + random.randint(40, 90) # Schnellere Event-Abfolge
    
    pygame.display.flip()
