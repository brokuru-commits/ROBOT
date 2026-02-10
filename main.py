#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, pygame
from datetime import datetime

# --- DISPLAY FIX ---
os.environ["DISPLAY"] = ":0"

# --- KONFIGURATION ---
WIDTH, HEIGHT = 640, 480
COLOR_BG       = (0, 5, 0)
COLOR_TOXIC    = (0, 255, 60)
COLOR_ALARM    = (255, 50, 0) # Rot fuer Alarm
COLOR_SCANLINE = (0, 20, 0)

BASE_DIR   = "/home/bot/robot/ui"
EMOTES_DIR = os.path.join(BASE_DIR, "assets", "emotes")
TXT_FILE   = os.path.join(BASE_DIR, "assets", "emotions.txt")

# --- LOGIK-WERTE ---
STATE_HOME  = "HOME"
STATE_EMOTE = "EMOTE"
STATE_ALARM = "ALARM"

# Beispiel-Stundenplan (Anpassen!)
LESSONS = [
    ("08:00", "09:30"), ("09:45", "11:15"), ("11:30", "13:00")
]

def load_quotes():
    quotes = {}
    if os.path.exists(TXT_FILE):
        try:
            with open(TXT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line:
                        idx, text = line.split("|", 1)
                        quotes.setdefault(idx.strip(), []).append(text.strip())
        except: pass
    return quotes

def get_lesson_progress():
    now = datetime.now().strftime("%H:%M")
    for start, end in LESSONS:
        if start <= now <= end:
            return True, f"UNTERRICHT BIS {end}"
    return False, "PAUSE / FREIZEIT"

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    # Fonts
    font_big  = pygame.font.SysFont("monospace", 100, bold=True)
    font_med  = pygame.font.SysFont("monospace", 35, bold=True)
    font_small = pygame.font.SysFont("monospace", 22, bold=True)

    quotes_data = load_quotes()
    state = STATE_HOME
    state_timer = 0
    next_emote_time = time.time() + random.randint(120, 300) # Alle 2-5 Min
    
    current_id = "1"
    current_quote = "SYSTEM READY"
    pulse = 0
    pulse_dir = 1

    while True:
        now_ts = time.time()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return

        # --- ZUSTANDS-MASCHINE ---
        if state == STATE_HOME:
            if now_ts > next_emote_time:
                state = STATE_EMOTE
                state_timer = now_ts + 7
                current_id = str(random.randint(1, 4))
                current_quote = random.choice(quotes_data.get(current_id, ["HELLO"]))
            elif random.random() < 0.001: # Zufalls-Alarm
                state = STATE_ALARM
                state_timer = now_ts + 4
                current_quote = "NUCLEAR ALERT!"

        elif state in [STATE_EMOTE, STATE_ALARM]:
            if now_ts > state_timer:
                state = STATE_HOME
                next_emote_time = now_ts + random.randint(180, 400)

        # --- ZEICHNEN ---
        screen.fill(COLOR_BG)
        dt = datetime.now()
        
        # Pulsieren fuer Icons
        pulse += 2 * pulse_dir
        if pulse >= 100 or pulse <= 0: pulse_dir *= -1

        if state == STATE_HOME:
            # 1. Uhrzeit & Datum
            t_surf = font_big.render(dt.strftime("%H:%M"), True, COLOR_TOXIC)
            screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 50))
            
            d_str = dt.strftime("%d.%m.%Y")
            d_surf = font_med.render(d_str, True, COLOR_TOXIC)
            screen.blit(d_surf, (WIDTH//2 - d_surf.get_width()//2, 160))

            # 2. Unterrichts-Balken
            in_lesson, lesson_text = get_lesson_progress()
            pygame.draw.rect(screen, (0, 40, 0), (50, 240, 540, 50)) # Hintergrund
            if in_lesson:
                pygame.draw.rect(screen, COLOR_TOXIC, (55, 245, 530, 40), 2)
            l_surf = font_small.render(lesson_text, True, COLOR_TOXIC)
            screen.blit(l_surf, (WIDTH//2 - l_surf.get_width()//2, 252))

            # 3. Pulsierende Icons (Rechts Oben)
            for i in range(3):
                alpha_color = (0, pulse + 155, 0)
                pygame.draw.circle(screen, alpha_color, (550 + (i*25), 40), 8, 2)
            
            # 4. Spruch
            q_surf = font_small.render(current_quote.upper(), True, COLOR_TOXIC)
            screen.blit(q_surf, (WIDTH//2 - q_surf.get_width()//2, 350))

        elif state == STATE_EMOTE:
            # Beetle erscheint mit Scan-Effekt
            img_path = os.path.join(EMOTES_DIR, f"{current_id}.png")
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert()
                img = pygame.transform.scale(img, (350, 350))
                screen.blit(img, (WIDTH//2 - 175, 40))
            q_surf = font_med.render(current_quote.upper(), True, COLOR_TOXIC)
            screen.blit(q_surf, (WIDTH//2 - q_surf.get_width()//2, 410))

        elif state == STATE_ALARM:
            # Nuklearer Wackler (Bunt & Shake)
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            rnd_color = (random.randint(100, 255), random.randint(0, 50), 0)
            screen.fill(rnd_color)
            a_surf = font_big.render("WARNING", True, (255, 255, 255))
            screen.blit(a_surf, (WIDTH//2 - a_surf.get_width()//2 + offset_x, 150 + offset_y))

        # 5. Dezente Scanline unten
        pygame.draw.line(screen, COLOR_TOXIC, (0, HEIGHT-10), (WIDTH, HEIGHT-10), 1)
        # Globales Flimmern
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(screen, COLOR_SCANLINE, (0, y), (WIDTH, y))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
