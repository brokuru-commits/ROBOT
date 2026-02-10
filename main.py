#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import math
import pygame
from datetime import datetime

# --- DISPLAY FIX ---
os.environ["DISPLAY"] = ":0"

# --- KONFIGURATION ---
WIDTH, HEIGHT = 640, 480
COLOR_TOXIC    = (0, 255, 60)
COLOR_SCANLINE = (0, 15, 0)
COLOR_WHITE    = (255, 255, 255)
COLOR_DARK     = (0, 20, 0)

BASE_DIR   = "/home/bot/robot/ui"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
EMOTES_DIR = os.path.join(ASSETS_DIR, "emotes")
BG_FILE    = os.path.join(ASSETS_DIR, "bg.png")
TXT_FILE   = os.path.join(ASSETS_DIR, "emotions.txt")

# --- ZUSTAENDE ---
STATE_HOME = "HOME"
STATE_EVENT = "EVENT"

def load_quotes():
    """Laedt Sprueche aus der Textdatei."""
    q = {}
    if os.path.exists(TXT_FILE):
        try:
            with open(TXT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line:
                        idx, text = line.split("|", 1)
                        q.setdefault(idx.strip(), []).append(text.strip())
        except: 
            pass
    return q

def main():
    pygame.init()
    # Fullscreen-Modus mit 640x480
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
    except:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    # Fonts laden
    try:
        font_huge  = pygame.font.SysFont("monospace", 110, bold=True)
        font_med   = pygame.font.SysFont("monospace", 45, bold=True)
        font_small = pygame.font.SysFont("monospace", 22, bold=True)
    except:
        font_huge = pygame.font.Font(None, 110)
        font_med = pygame.font.Font(None, 45)
        font_small = pygame.font.Font(None, 22)

    # Hintergrund laden
    bg_img = None
    if os.path.exists(BG_FILE):
        try:
            bg_img = pygame.image.load(BG_FILE).convert()
            bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
        except:
            pass

    quotes_data = load_quotes()
    state = STATE_HOME
    event_timer = 0
    next_event_time = time.time() + 30
    
    scan_bar_x = 0
    current_quote = "SYSTEM READY"
    current_id = "1"
    
    # ASCII Gesichter fuer den Retro-Look
    ascii_faces = ["(o_o)", "[O.O]", "(^.^)", "<o.o>", "( -_-)", "[(X)]"]
    last_face_change = 0
    active_face = ascii_faces[0]

    while True:
        now_ts = time.time()
        dt = datetime.now()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: 
                pygame.quit()
                sys.exit()

        # --- EVENT LOGIK ---
        if state == STATE_HOME and now_ts > next_event_time:
            state = STATE_EVENT
            event_type = random.choice(["EMOTE", "NUKE", "GLITCH"])
            event_timer = now_ts + 7 # 7 Sekunden Dauer
            
            if event_type == "EMOTE":
                current_id = str(random.randint(1, 4))
                current_quote = random.choice(quotes_data.get(current_id, ["HELLO VAULT DWELLER"]))
            elif event_type == "NUKE":
                current_quote = "!!! RADIATION LEAK !!!"
            else:
                current_quote = "RECALIBRATING CORE..."

        if state == STATE_EVENT and now_ts > event_timer:
            state = STATE_HOME
            # Naechstes Event in 45 bis 120 Sekunden
            next_event_time = now_ts + random.randint(45, 120)
            current_quote = random.choice(quotes_data.get("1", ["SYSTEM NOMINAL"]))

        # --- ZEICHNEN ---
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(COLOR_DARK)

        if state == STATE_HOME:
            # 1. Uhrzeit & Datum (Linksbuendig)
            time_str = dt.strftime("%H:%M")
            date_str = dt.strftime("%A, %d.%m.")
            
            t_surf = font_huge.render(time_str, True, COLOR_TOXIC)
            d_surf = font_med.render(date_str.upper(), True, COLOR_TOXIC)
            
            screen.blit(t_surf, (30, 40))
            screen.blit(d_surf, (35, 145))

            # 2. ASCII Animation
            if now_ts - last_face_change > 5:
                active_face = random.choice(ascii_faces)
                last_face_change = now_ts
            
            f_surf = font_med.render(active_face, True, COLOR_TOXIC)
            screen.blit(f_surf, (35, 230))
            
            # 3. Spruch (Zentraler Bereich)
            q_surf = font_small.render(current_quote.upper(), True, COLOR_TOXIC)
            screen.blit(q_surf, (35, 300))

            # 4. Pulsierende Icons (Rechts Oben)
            pulse_val = abs(int(math.sin(time.time() * 3) * 100)) + 155 
            pygame.draw.rect(screen, (0, pulse_val, 0), (540, 30, 25, 25), 2)
            pygame.draw.rect(screen, (0, pulse_val, 0), (580, 30, 25, 25))

            # 5. Unterrichts-Balken (Ganz unten)
            pygame.draw.rect(screen, (0, 40, 0), (0, HEIGHT-70, WIDTH, 70))
            pygame.draw.line(screen, COLOR_TOXIC, (0, HEIGHT-70), (WIDTH, HEIGHT-70), 3)
            
            # Beispielhafte Logik fuer Schulzeit
            status_text = "STATUS: LERNEINHEIT LÄUFT" if 8 <= dt.hour < 14 else "STATUS: FREIZEIT AKTIVIERT"
            u_surf = font_small.render(status_text, True, COLOR_TOXIC)
            screen.blit(u_surf, (WIDTH//2 - u_surf.get_width()//2, HEIGHT-45))

        elif state == STATE_EVENT:
            # Shake-Effekt
            off_x = random.randint(-15, 15)
            off_y = random.randint(-15, 15)
            
            if "RADIATION" in current_quote: # Nuke/Alarm Event
                screen.fill((random.randint(150, 255), 0, 0))
                msg = font_huge.render("WARNING", True, COLOR_WHITE)
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2 + off_x, 150 + off_y))
            else: # Emote/Kaefer Event
                img_p = os.path.join(EMOTES_DIR, f"{current_id}.png")
                if os.path.exists(img_p):
                    try:
                        img = pygame.image.load(img_p).convert()
                        img = pygame.transform.scale(img, (300, 300))
                        screen.blit(img, (WIDTH//2 - 150 + off_x, 60 + off_y))
                    except: pass
            
            # Event-Spruch
            ev_surf = font_med.render(current_quote.upper(), True, COLOR_WHITE)
            screen.blit(ev_surf, (WIDTH//2 - ev_surf.get_width()//2, 400))

        # --- OVERLAYS (Immer sichtbar) ---
        # Vertikale Scan-Animation am Rand
        scan_bar_x = (scan_bar_x + 5) % WIDTH
        s_surf = pygame.Surface((10, HEIGHT), pygame.SRCALPHA)
        s_surf.fill((0, 255, 60, 30))
        screen.blit(s_surf, (scan_bar_x, 0))

        # Statisches Scanline-Gitter
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(screen, COLOR_SCANLINE, (0, y), (WIDTH, y))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
