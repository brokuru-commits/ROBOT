#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import pygame
from datetime import datetime

# --- DISPLAY FIX ---
os.environ["DISPLAY"] = ":0"

# --- KONFIGURATION ---
WIDTH, HEIGHT = 640, 480
COLOR_TOXIC    = (0, 255, 60)
COLOR_SCANLINE = (0, 15, 0)
COLOR_WHITE    = (255, 255, 255)
COLOR_DARK     = (0, 15, 0)

BASE_DIR   = "/home/bot/robot/ui"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
EMOTES_DIR = os.path.join(ASSETS_DIR, "emotes")
BG_FILE    = os.path.join(ASSETS_DIR, "bg.png")
TXT_FILE   = os.path.join(ASSETS_DIR, "emotions.txt")

# --- STUNDENPLAN DATEN ---
# Format: (Startzeit, Endzeit, Name/Typ)
SCHEDULE = [
    ("07:30", "08:00", "VORBEREITUNG"),
    ("08:00", "08:45", "1. STUNDE"),
    ("08:45", "08:50", "PAUSE (5M)"),
    ("08:50", "09:35", "2. STUNDE"),
    ("09:35", "09:55", "GR. PAUSE (20M)"),
    ("09:55", "10:40", "3. STUNDE"),
    ("10:40", "10:45", "PAUSE (5M)"),
    ("10:45", "11:30", "4. STUNDE"),
    ("11:30", "11:50", "GR. PAUSE (20M)"),
    ("11:50", "12:35", "5. STUNDE"),
    ("12:35", "12:40", "PAUSE (5M)"),
    ("12:40", "13:25", "6. STUNDE"),
    ("13:25", "13:35", "PAUSE (10M)"),
    ("13:35", "14:20", "7. STUNDE"),
    ("14:20", "14:25", "PAUSE (5M)"),
    ("14:25", "15:10", "8. STUNDE"),
    ("15:10", "15:15", "PAUSE (5M)"),
    ("15:15", "16:00", "9. STUNDE")
]

def get_current_status():
    now = datetime.now()
    now_str = now.strftime("%H:%M")
    
    for start, end, label in SCHEDULE:
        if start <= now_str < end:
            # Berechnung der verbleibenden Minuten
            end_time = datetime.strptime(end, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
            remaining = int((end_time - now).total_seconds() / 60)
            
            # Fortschritt berechnen (0.0 bis 1.0)
            start_time = datetime.strptime(start, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
            total_duration = (end_time - start_time).total_seconds()
            elapsed = (now - start_time).total_seconds()
            progress = elapsed / total_duration if total_duration > 0 else 0
            
            return label, remaining, progress
            
    return "FEIERABEND", 0, 1.0

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
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
    except:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    font_huge  = pygame.font.SysFont("monospace", 110, bold=True)
    font_med   = pygame.font.SysFont("monospace", 40, bold=True)
    font_small = pygame.font.SysFont("monospace", 18, bold=True)

    bg_img = None
    if os.path.exists(BG_FILE):
        try:
            bg_img = pygame.image.load(BG_FILE).convert()
            bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
        except: pass

    quotes_data = load_quotes()
    state = "HOME"
    event_timer = 0
    next_event_time = time.time() + 30
    
    bottom_scan_x = 0
    current_quote = "SYSTEM BEREIT"
    current_id = "1"
    active_face = "(o_o)"
    last_face_change = 0
    ascii_faces = ["(o_o)", "[O.O]", "(^.^)", "<o.o>", "( -_-)", "[(X)]"]
    
    pulse_val, pulse_dir = 155, 4

    while True:
        now_ts = time.time()
        dt = datetime.now()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: 
                pygame.quit(); sys.exit()

        # --- EVENT LOGIK ---
        if state == "HOME" and now_ts > next_event_time:
            state = "EVENT"
            event_type = random.choice(["EMOTE", "WARNUNG", "FEHLER"])
            event_timer = now_ts + 5
            if event_type == "EMOTE":
                current_id = str(random.randint(1, 4))
                current_quote = random.choice(quotes_data.get(current_id, ["SYSTEM AKTIV"]))
            elif event_type == "WARNUNG": current_quote = "!!! RAD-ALARM !!!"
            else: current_quote = "REKALIBRIERE KERN..."

        if state == "EVENT" and now_ts > event_timer:
            state = "HOME"
            next_event_time = now_ts + random.randint(45, 120)

        # --- RENDERING ---
        if bg_img: screen.blit(bg_img, (0, 0))
        else: screen.fill(COLOR_DARK)

        if state == "HOME":
            # Uhr & Datum
            screen.blit(font_huge.render(dt.strftime("%H:%M"), True, COLOR_TOXIC), (30, 40))
            
            # Wochentage auf Deutsch mappen
            wd_map = {"Monday":"MONTAG", "Tuesday":"DIENSTAG", "Wednesday":"MITTWOCH", "Thursday":"DONNERSTAG", "Friday":"FREITAG", "Saturday":"SAMSTAG", "Sunday":"SONNTAG"}
            day_str = wd_map.get(dt.strftime("%A"), dt.strftime("%A").upper())
            screen.blit(font_med.render(f"{day_str}, {dt.strftime('%d.%m.')}", True, COLOR_TOXIC), (35, 145))

            # ASCII Gesicht
            if now_ts - last_face_change > 5:
                active_face = random.choice(ascii_faces); last_face_change = now_ts
            screen.blit(font_med.render(active_face, True, COLOR_TOXIC), (35, 230))
            
            # Spruch
            screen.blit(font_small.render(current_quote.upper(), True, COLOR_TOXIC), (35, 300))

            # Icons Oben Rechts
            pulse_val += pulse_dir
            if pulse_val >= 250 or pulse_val <= 150: pulse_dir *= -1
            for i, char in enumerate([">", "#", "!"]):
                screen.blit(font_small.render(f"[{char}]", True, (0, pulse_val, 0)), (520 + (i*40), 30))

            # --- ASCII FORTSCHRITTSBALKEN (STRENG NACH DEINEM PLAN) ---
            label, rem, prog = get_current_status()
            bar_len = 30
            filled = int(prog * bar_len)
            bar_str = "[" + "|" * filled + " " * (bar_len - filled) + "]"
            
            info_str = f"{bar_str} {label}: NOCH {rem} MIN" if label != "FEIERABEND" else f"{bar_str} {label}"
            b_surf = font_small.render(info_str, True, COLOR_TOXIC)
            screen.blit(b_surf, (WIDTH//2 - b_surf.get_width()//2, HEIGHT-40))

        elif state == "EVENT":
            if "RAD-ALARM" in current_quote:
                screen.fill((200, 0, 0))
                msg = font_huge.render("WARNUNG", True, COLOR_WHITE)
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 150))
            else:
                img_p = os.path.join(EMOTES_DIR, f"{current_id}.png")
                if os.path.exists(img_p):
                    img = pygame.image.load(img_p).convert()
                    img = pygame.transform.scale(img, (WIDTH, HEIGHT))
                    screen.blit(img, (0, 0))
            screen.blit(font_med.render(current_quote.upper(), True, COLOR_WHITE), (WIDTH//2 - 150, 400))

        # Untere Scan-Linie (Dünn, Farbe wechselnd)
        import math
        bottom_scan_x = (bottom_scan_x + 6) % WIDTH
        c_val = int(math.sin(now_ts * 2) * 127 + 128)
        pygame.draw.line(screen, (0, 255, c_val), (bottom_scan_x, HEIGHT-10), (bottom_scan_x + 30, HEIGHT-10), 2)

        # Scanlines Gitter
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(screen, COLOR_SCANLINE, (0, y), (WIDTH, y))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
