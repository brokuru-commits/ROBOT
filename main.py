#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import urllib.request
import urllib.error
import py_compile
from datetime import datetime

import pygame

# =========================
# CONFIG
# =========================
# Nicht hart nötig, aber wenn du damit stabil bist, lass es drin:
os.environ.setdefault("SDL_VIDEODRIVER", "x11")

W, H = 480, 320
FPS = 25  # reicht völlig für UI

# Farben (Fallout-ish)
FALLOUT_GREEN = (50, 255, 50)
FALLOUT_DIM   = (10, 80, 10)
BLACK         = (0, 0, 0)
WHITE         = (255, 255, 255)
ALERT_RED     = (255, 50, 50)
BLUE_NEON     = (0, 200, 255)
PURPLE        = (140, 60, 180)

# Pfade
BASE_DIR = os.path.expanduser("~/robot/ui/assets")
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
BG_PATH   = os.path.join(BASE_DIR, "bg.png")

# Cache (offline-sicher)
CACHE_DIR = os.path.expanduser("~/.cache/heum-tec")
TODO_CACHE = os.path.join(CACHE_DIR, "todo.txt")
ART_CACHE  = os.path.join(CACHE_DIR, "art.txt")
Q_CACHE    = os.path.join(CACHE_DIR, "quotes.txt")

# Repo (raw)
REPO_URL  = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/"
UPDATE_URL = REPO_URL + "main.py"
TODO_URL   = REPO_URL + "todo.txt"
ART_URL    = REPO_URL + "art.txt"
QUOTES_URL = REPO_URL + "quotes.txt"  # optional, falls du es nutzt

# Fetch-Intervalle (Sekunden)
FETCH_TODO_EVERY = 60
FETCH_ART_EVERY  = 300
FETCH_Q_EVERY    = 600

# Stundenplan (Start h,m / Ende h,m / Label)
PLAN = [
    (7, 30, 8, 0,  "ANKUNFT/PAUSE"),
    (8, 0,  8, 45, "UNTERRICHT 1"),
    (8, 45, 8, 50, "PAUSE (5min)"),
    (8, 50, 9, 35, "UNTERRICHT 2"),
    (9, 35, 9, 55, "PAUSE (20min)"),
    (9, 55, 10, 40,"UNTERRICHT 3"),
    (10,40, 10,45, "PAUSE (5min)"),
    (10,45, 11,30, "UNTERRICHT 4"),
    (11,30, 11,50, "PAUSE (20min)"),
    (11,50, 12,35, "UNTERRICHT 5"),
    (12,35, 12,40, "PAUSE (5min)"),
    (12,40, 13,25, "UNTERRICHT 6"),
    (13,25, 13,35, "PAUSE (10min)"),
    (13,35, 14,20, "UNTERRICHT 7"),
    (14,20, 14,25, "PAUSE (5min)"),
    (14,25, 15,10, "UNTERRICHT 8"),
    (15,10, 15,15, "PAUSE (5min)"),
    (15,15, 16,0,  "UNTERRICHT 9"),
    (16,0,  17,0,  "FEIERABEND"),
]

def ensure_cache_dir():
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
    except Exception:
        pass

def read_cache(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip("\n") for l in f.readlines()]
        return [l.strip() for l in lines if l.strip()]
    except Exception:
        return []

def write_cache(path, lines):
    try:
        ensure_cache_dir()
        with open(path, "w", encoding="utf-8") as f:
            for l in lines:
                f.write(l.rstrip() + "\n")
    except Exception:
        pass

def fetch_lines(url, timeout=2):
    """Lädt Textzeilen; blockiert nie länger als timeout."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = r.read().decode("utf-8", errors="ignore")
        lines = [l.strip() for l in data.splitlines() if l.strip()]
        return lines
    except Exception:
        return []

def get_temp_c():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read()) / 1000.0
    except Exception:
        return 0.0

def secs_today(dt):
    return dt.hour * 3600 + dt.minute * 60 + dt.second

def get_status_seconds():
    """Sekunden-genauer Status: label, remaining_seconds, progress(0..1)."""
    now = datetime.now()
    cur = secs_today(now)
    for (sh, sm, eh, em, label) in PLAN:
        start = sh * 3600 + sm * 60
        end   = eh * 3600 + em * 60
        if start <= cur < end:
            total = max(1, end - start)
            passed = cur - start
            progress = passed / total
            remain = end - cur
            return label, remain, progress
    return "FREIZEIT", 0, 0.0

def fmt_mmss(seconds):
    if seconds < 0:
        seconds = 0
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return "%02d:%02d:%02d" % (h, m, s)
    return "%02d:%02d" % (m, s)

def bar_color_for(label):
    u = label.upper()
    if "PAUSE" in u:
        return BLUE_NEON
    if "FEIER" in u:
        return PURPLE
    return FALLOUT_GREEN

def safe_update_self(update_url):
    """
    Safe self-update:
    - download to .new
    - py_compile check
    - backup .bak
    - atomic replace
    """
    this_file = os.path.abspath(__file__)
    new_file = this_file + ".new"
    bak_file = this_file + ".bak"

    try:
        urllib.request.urlretrieve(update_url, new_file)
    except Exception as e:
        return False, "Download fehlgeschlagen"

    # Syntax check
    try:
        py_compile.compile(new_file, doraise=True)
    except Exception:
        try:
            os.remove(new_file)
        except Exception:
            pass
        return False, "Update ist kaputt (Syntax)."

    # Backup + replace
    try:
        if os.path.exists(bak_file):
            os.remove(bak_file)
        if os.path.exists(this_file):
            os.replace(this_file, bak_file)
        os.replace(new_file, this_file)
    except Exception:
        # rollback attempt
        try:
            if os.path.exists(bak_file):
                os.replace(bak_file, this_file)
        except Exception:
            pass
        return False, "Konnte nicht ersetzen."

    return True, "Update installiert. Neustart nötig."

def load_ascii_art(art_lines):
    """Unterstützt Blöcke getrennt durch ---"""
    if not art_lines:
        return ["(o.o)", "/|_|\\", " | |"]
    joined = "\n".join(art_lines)
    parts = [p.strip() for p in joined.split("---") if p.strip()]
    if not parts:
        return ["(o.o)", "/|_|\\", " | |"]
    return random.choice(parts).splitlines()

def draw_button(screen, rect, text, font, fg, bg=FALLOUT_DIM, border=2):
    pygame.draw.rect(screen, bg, rect)
    pygame.draw.rect(screen, fg, rect, border)
    surf = font.render(text, True, fg)
    screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))

def main():
    pygame.init()
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    # Assets
    bg_img = None
    try:
        if os.path.exists(BG_PATH):
            bg_img = pygame.image.load(BG_PATH).convert()
            bg_img = pygame.transform.scale(bg_img, (W, H))
    except Exception:
        bg_img = None

    # Fonts
    def load_font(path, size, fallback_size=24):
        try:
            if os.path.exists(path):
                return pygame.font.Font(path, size)
        except Exception:
            pass
        return pygame.font.SysFont(None, fallback_size)

    f_xl = load_font(FONT_PATH, 52, 44)
    f_l  = load_font(FONT_PATH, 30, 28)
    f_m  = load_font(FONT_PATH, 22, 22)
    f_s  = load_font(FONT_PATH, 16, 16)
    f_mono = pygame.font.SysFont("Courier", 18, bold=True)

    # Cache laden (offline)
    ensure_cache_dir()
    todos = read_cache(TODO_CACHE)
    art_lines = read_cache(ART_CACHE)
    quote_lines = read_cache(Q_CACHE)

    ascii_art = load_ascii_art(art_lines)

    # State
    state = "BOOT"
    boot_start = time.time()
    last_col_change = time.time()
    emoji_color = FALLOUT_GREEN

    # Fetch timers
    last_todo_fetch = 0
    last_art_fetch  = 0
    last_q_fetch    = 0

    # Calc Vars (noch simpel gehalten)
    calc_inp = ""
    calc_res = ""
    calc_face = "( -_-)"

    # Buttons
    btn_home = pygame.Rect(390, 10, 80, 40)
    btn_nav_todo = pygame.Rect(20, 245, 130, 60)
    btn_nav_calc = pygame.Rect(175, 245, 130, 60)
    btn_nav_upd  = pygame.Rect(330, 245, 130, 60)

    # Update confirm buttons
    btn_yes = pygame.Rect(60, 180, 160, 80)
    btn_no  = pygame.Rect(260, 180, 160, 80)

    # Calc keyboard layout (sichtbar!)
    # Bereich: y 150..310
    keys = [
        ("7",  30, 150), ("8", 100, 150), ("9", 170, 150),
        ("4",  30, 200), ("5", 100, 200), ("6", 170, 200),
        ("1",  30, 250), ("2", 100, 250), ("3", 170, 250),
        ("C",  30, 295), ("0", 100, 295), ("=", 170, 295),
    ]
    KEY_W, KEY_H = 60, 30  # passt sauber

    def schedule_fetches():
        nonlocal todos, ascii_art, quote_lines, last_todo_fetch, last_art_fetch, last_q_fetch
        now = time.time()

        # TODO
        if now - last_todo_fetch > FETCH_TODO_EVERY:
            last_todo_fetch = now
            new = fetch_lines(TODO_URL, timeout=2)
            if new:
                todos = new
                write_cache(TODO_CACHE, todos)

        # ART
        if now - last_art_fetch > FETCH_ART_EVERY:
            last_art_fetch = now
            new = fetch_lines(ART_URL, timeout=2)
            if new:
                write_cache(ART_CACHE, new)
                ascii_art[:] = load_ascii_art(new)

        # Quotes (optional)
        if now - last_q_fetch > FETCH_Q_EVERY:
            last_q_fetch = now
            new = fetch_lines(QUOTES_URL, timeout=2)
            if new:
                quote_lines = new
                write_cache(Q_CACHE, quote_lines)

    # Helper: background
    def draw_bg():
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(BLACK)

    # Main loop
    while True:
        clock.tick(FPS)
        click_pos = None

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                click_pos = e.pos
            elif e.type == pygame.FINGERDOWN:
                click_pos = (int(e.x * W), int(e.y * H))

        # Hintergrund
        if state == "BOOT":
            screen.fill(BLACK)
        else:
            draw_bg()

        # Hintergrund-Fetch (blockiert nicht hart; maximal 2s und selten)
        # Auf BOOT lieber NICHT dauernd, sonst "Boot hängt" bei schlechtem Netz.
        if state in ("HOME", "TODO") and int(time.time()) % 2 == 0:
            schedule_fetches()

        # =========================
        # BOOT
        # =========================
        if state == "BOOT":
            elapsed = time.time() - boot_start
            rnd_col = (random.randint(50, 255), random.randint(100, 255), random.randint(50, 255))
            title = f_xl.render("HEUM-TEC", True, rnd_col)
            screen.blit(title, (W//2 - title.get_width()//2, H//2 - 70))

            # Loading bar
            bar_w = int(min(1.0, elapsed / 4.0) * 400)
            pygame.draw.rect(screen, rnd_col, (40, H//2 + 10, bar_w, 26))

            # Short boot hint
            hint = f_s.render("booting...", True, FALLOUT_DIM)
            screen.blit(hint, (W//2 - hint.get_width()//2, H//2 + 45))

            if elapsed > 4.0:
                # Einmal versuchen, Art zu laden, sonst Cache
                art_new = fetch_lines(ART_URL, timeout=2)
                if art_new:
                    write_cache(ART_CACHE, art_new)
                    ascii_art = load_ascii_art(art_new)
                state = "HOME"

        # =========================
        # HOME
        # =========================
        elif state == "HOME":
            # Header (Temp)
            pygame.draw.circle(screen, FALLOUT_GREEN, (20, 20), 5)
            temp = get_temp_c()
            col_temp = FALLOUT_GREEN if temp < 60 else ALERT_RED
            screen.blit(f_s.render("%dC" % int(temp), True, col_temp), (35, 12))

            # ASCII Art
            if time.time() - last_col_change > 0.5:
                emoji_color = (random.randint(50, 255), random.randint(100, 255), random.randint(50, 255))
                last_col_change = time.time()

            y_art = 60
            for line in ascii_art[:6]:
                surf = f_mono.render(line, True, emoji_color)
                screen.blit(surf, (W//2 - surf.get_width()//2, y_art))
                y_art += 22

            # Stundenplan Balken (sekundengenau)
            label, remain_sec, prog = get_status_seconds()

            if label != "FREIZEIT":
                bar_col = bar_color_for(label)
                pygame.draw.rect(screen, FALLOUT_DIM, (40, 170, 400, 38))
                pygame.draw.rect(screen, bar_col, (40, 170, int(400 * prog), 38))

                info_txt = f_m.render(label, True, WHITE)
                time_txt = f_m.render("NOCH " + fmt_mmss(remain_sec), True, WHITE)
                screen.blit(info_txt, (50, 178))
                screen.blit(time_txt, (285, 178))
            else:
                msg = f_l.render("FREIZEIT!", True, BLUE_NEON)
                screen.blit(msg, (W//2 - msg.get_width()//2, 175))

            # Navigation Buttons
            draw_button(screen, btn_nav_todo, "TO-DO", f_m, FALLOUT_GREEN)
            draw_button(screen, btn_nav_calc, "NOTEN", f_m, FALLOUT_GREEN)
            draw_button(screen, btn_nav_upd,  "UPDATE", f_m, ALERT_RED)

            if click_pos:
                if btn_nav_todo.collidepoint(click_pos):
                    state = "TODO"
                    # sofort versuchen zu aktualisieren, aber UI bleibt stabil
                    new = fetch_lines(TODO_URL, timeout=2)
                    if new:
                        todos = new
                        write_cache(TODO_CACHE, todos)
                elif btn_nav_calc.collidepoint(click_pos):
                    state = "CALC"
                elif btn_nav_upd.collidepoint(click_pos):
                    state = "UPDATE"

        # =========================
        # TODO
        # =========================
        elif state == "TODO":
            screen.blit(f_l.render("AUFGABEN", True, FALLOUT_GREEN), (20, 18))

            y_off = 70
            # (max 6)
            for i, item in enumerate(todos[:6]):
                box = pygame.Rect(20, y_off, 440, 34)
                pygame.draw.rect(screen, FALLOUT_DIM, box, 1)
                screen.blit(f_m.render(item, True, WHITE), (28, y_off + 6))
                if click_pos and box.collidepoint(click_pos):
                    # lokal löschen
                    try:
                        del todos[i]
                        write_cache(TODO_CACHE, todos)
                    except Exception:
                        pass
                    click_pos = None
                    break
                y_off += 38

            pygame.draw.rect(screen, FALLOUT_DIM, btn_home, 1)
            screen.blit(f_m.render("HOME", True, FALLOUT_GREEN), (btn_home.x+12, btn_home.y+10))
            if click_pos and btn_home.collidepoint(click_pos):
                state = "HOME"

        # =========================
        # UPDATE
        # =========================
        elif state == "UPDATE":
            screen.fill((50, 0, 0))
            msg = f_l.render("UPDATE VON GITHUB?", True, WHITE)
            screen.blit(msg, (W//2 - msg.get_width()//2, 70))

            draw_button(screen, btn_yes, "JA", f_l, BLACK, bg=FALLOUT_GREEN, border=0)
            draw_button(screen, btn_no,  "NEIN", f_l, BLACK, bg=ALERT_RED, border=0)

            if click_pos:
                if btn_no.collidepoint(click_pos):
                    state = "HOME"
                elif btn_yes.collidepoint(click_pos):
                    # Update ausführen
                    screen.fill(BLACK)
                    screen.blit(f_l.render("LADE UPDATE...", True, FALLOUT_GREEN), (80, 140))
                    pygame.display.flip()

                    ok, text = safe_update_self(UPDATE_URL)

                    screen.fill(BLACK)
                    color = FALLOUT_GREEN if ok else ALERT_RED
                    screen.blit(f_m.render(text, True, color), (20, 140))
                    screen.blit(f_s.render("Tippen zum Neustart/Zurueck", True, FALLOUT_DIM), (20, 170))
                    pygame.display.flip()

                    # warten auf Tap
                    waiting = True
                    while waiting:
                        for ev in pygame.event.get():
                            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_q):
                                pygame.quit(); sys.exit()
                            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                                waiting = False
                        clock.tick(20)

                    if ok:
                        # Neustart: Programm beenden, systemd/LXSession startet es ggf neu
                        pygame.quit()
                        sys.exit()
                    else:
                        state = "HOME"

        # =========================
        # CALC (V1: Prozent->Note wie bei dir; später ersetzen wir das durch Punkte/Notentabellen)
        # =========================
        elif state == "CALC":
            screen.blit(f_l.render("NOTEN RECHNER", True, FALLOUT_GREEN), (20, 18))

            pygame.draw.rect(screen, FALLOUT_DIM, (20, 65, 210, 48))
            screen.blit(f_l.render(calc_inp, True, WHITE), (30, 72))

            screen.blit(f_xl.render(calc_res, True, FALLOUT_GREEN), (250, 62))
            screen.blit(f_l.render(calc_face, True, FALLOUT_GREEN), (360, 82))

            pygame.draw.rect(screen, FALLOUT_DIM, btn_home, 1)
            screen.blit(f_m.render("HOME", True, FALLOUT_GREEN), (btn_home.x+12, btn_home.y+10))
            if click_pos and btn_home.collidepoint(click_pos):
                state = "HOME"
                click_pos = None

            # Keys
            for k, kx, ky in keys:
                r = pygame.Rect(kx, ky, KEY_W, KEY_H)
                pygame.draw.rect(screen, FALLOUT_DIM, r)
                pygame.draw.rect(screen, FALLOUT_GREEN, r, 1)
                screen.blit(f_m.render(k, True, WHITE), (kx + 22, ky + 5))

                if click_pos and r.collidepoint(click_pos):
                    if k == "C":
                        calc_inp = ""
                        calc_res = ""
                        calc_face = "( -_-)"
                    elif k == "=":
                        try:
                            # wie in deiner Version: input = Prozent (0..100)
                            p = float(calc_inp)
                            note = 6 - (5 * p / 100.0)
                            calc_res = "%.1f" % note
                            calc_face = "(^o^)" if note < 2 else "(>_<)" if note > 4 else "( -_-)"
                        except Exception:
                            calc_res = "ERR"
                            calc_face = "(x_x)"
                    else:
                        if len(calc_inp) < 3:
                            calc_inp += k
                    click_pos = None
                    break

        pygame.display.flip()

if __name__ == "__main__":
    main()
