#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, pygame
from datetime import datetime

# --- DISPLAY FIX ---
os.environ["DISPLAY"] = ":0"

# --- KONFIGURATION ---
WIDTH, HEIGHT = 640, 480
COLOR_TOXIC    = (0, 255, 60)
COLOR_SCANLINE = (0, 15, 0)
COLOR_WHITE    = (255, 255, 255)

BASE_DIR   = "/home/bot/robot/ui"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
EMOTES_DIR = os.path.join(ASSETS_DIR, "emotes")
BG_FILE    = os.path.join(ASSETS_DIR, "bg.png")
TXT_FILE   = os.path.join(ASSETS_DIR, "emotions.txt")

# --- ZUSTAENDE ---
STATE_HOME = "HOME"
STATE_EVENT = "EVENT"

def load_quotes():
    q = {}
    if os.path.exists(TXT_FILE):
        try:
            with open(TXT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line:
                        idx, text = line.split("|", 1)
                        q.setdefault(idx.strip(), []).append(text.strip())
        except: pass
    return q

def main():
    pygame.init()
    # Fullscreen-Modus
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    # Fonts (Fallout-Style: Monospace & Bold)
    try:
        font_huge  = pygame.font.SysFont("monospace", 120, bold=True)
        font_med   = pygame.font.SysFont("monospace", 45, bold=True)
        font_small = pygame.font.SysFont("monospace", 24, bold=True)
    except:
        font_huge = font_med = font_small = pygame.font.Font(None, 30)

    # Hintergrund laden
    bg_img = None
    if os.path.exists(BG_FILE):
        bg_img = pygame.image.load(BG_FILE).convert()
        bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

    quotes_data = load_quotes()
    state = STATE_HOME
    event_timer = 0
    next_event_time = time.time() + 30
    
    scan_bar_x = 0
    current_quote = "INITIALIZING..."
    current_id = "1"
    
    # ASCII Gesichter
    ascii_faces = ["(o_o)", "[O.O]", "(^.^)", "<o.o>", "( -_-)", "[(X)]"]

    while True:
        now_ts = time.time()
        dt = datetime.now()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return

        # --- EVENT LOGIK ---
        if state == STATE_HOME and now_ts > next_event_time:
            state = STATE_EVENT
            event_type = random.choice(["EMOTE", "NUKE", "GLITCH"])
            event_timer = now_ts + 7
            
            if event_type == "EMOTE":
                current_id = str(random.randint(1, 4))
                current_quote = random.choice(quotes_data.get(current_id, ["HELLO WORLD"]))
            elif event_type == "NUKE":
                current_quote = "!!! CRITICAL RADIATION !!!"
            else:
                current_quote = "SYSTEM REBOOT..."

        if state == STATE_EVENT and now_ts > event_timer:
            state = STATE_HOME
            next_event_time = now_ts + random.randint(45, 120)

        # --- ZEICHNEN ---
        # 1. Background
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill((0, 20, 0))

        if state == STATE_HOME:
            # Uhrzeit & Datum (Linksbündig)
            time_str = dt.strftime("%H:%M")
            date_str = dt.strftime("%d.%m.%y")
            
            t_surf = font_huge.render(time_str, True, COLOR_TOXIC)
            d_surf = font_med.render(date_str, True, COLOR_TOXIC)
            
            screen.blit(t_surf, (40, 40))
            screen.blit(d_surf, (45, 140))

            # ASCII Emote & Spruch
            face = random.choice(ascii_faces) if dt.second % 10 == 0 else ascii_faces[0]
            f_surf = font_med.render(face, True, COLOR_TOXIC)
            screen.blit(f_surf, (40, 220))
            
            q_surf = font_small.render(current_quote[:35].upper(), True, COLOR_TOXIC)
            screen.blit(q_surf, (40, 280))

            # Icons Oben Rechts (Pulsierend)
            p = abs(int(math.sin(time.time() * 3) * 100)) + 155 if 'math' in sys.modules else 255
            import math # Sicherstellen dass math da ist
            pygame.draw.rect(screen, (0, p, 0), (550, 30, 20, 20), 2)
            pygame.draw.rect(screen, (0, p, 0), (580, 30, 20, 20))

            # Unterrichts-Balken (Ganz unten)
            pygame.draw.rect(screen, (0, 40, 0), (0, HEIGHT-60, WIDTH, 60))
            pygame.draw.line(screen, COLOR_TOXIC, (0, HEIGHT-60), (WIDTH, HEIGHT-60), 2)
            u_str = "STATUS: LERNEINHEIT AKTIV" if 8 <= dt.hour < 14 else "STATUS: FREIZEIT / ÖDLAND"
            u_surf = font_small.render(u_str, True, COLOR_TOXIC)
            screen.blit(u_surf, (WIDTH//2 - u_surf.get_width()//2, HEIGHT-40))

        elif state == STATE_EVENT:
            # Zufallseffekte: Bunt, Wackeln, Bilder
            off_x = random.randint(-10, 10)
            off_y = random.randint(-10, 10)
            
            if "CRITICAL" in current_quote: # Nuke Event
                screen.fill((random.randint(150, 255), 0, 0))
                msg = font_huge.render("WARNING", True, COLOR_WHITE)
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2 + off_x, 150 + off_y))
            else: # Emote Event
                img_p = os.path.join(EMOTES_DIR, f"{current_id}.png")
                if os.path.exists(img_p):
                    img = pygame.image.load(img_p).convert()
                    img = pygame.transform.scale(img, (320, 320))
                    screen.blit(img, (WIDTH//2 - 160 + off_x, 60 + off_y))
            
            q_surf = font_med.render(current_quote.upper(), True, COLOR_WHITE)
            screen.blit(q_surf, (WIDTH//2 - q_surf.get_width()//2, 400))

        # --- OVERLAYS (Immer sichtbar) ---
        # Vertikale Scan-Bar am Rand
        scan_bar_x = (scan_bar_x + 4) % WIDTH
        s_rect = pygame.Surface((5, HEIGHT), pygame.SRCALPHA)
        s_rect.fill((0, 255, 60, 40))
        screen.blit(s_rect, (scan_bar_x, 0))

        # Scanlines Gitter
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(screen, COLOR_SCANLINE, (0, y), (WIDTH, y))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
