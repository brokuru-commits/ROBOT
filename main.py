#!/usr/bin/env python3
import os, sys, time, random
from datetime import datetime
import pygame

# --- KONFIGURATION ---
WIDTH, HEIGHT = 480, 320
COLOR_BG       = (0, 5, 0)
COLOR_TOXIC    = (0, 255, 60)
COLOR_SCANLINE = (0, 15, 0)

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
EMOTES_DIR = os.path.join(ASSETS_DIR, "emotes")
TXT_FILE   = os.path.join(ASSETS_DIR, "emotions.txt")

def load_quotes():
    quotes_map = {}
    if os.path.exists(TXT_FILE):
        try:
            with open(TXT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line:
                        idx, text = line.split("|", 1)
                        quotes_map.setdefault(idx.strip(), []).append(text.strip())
        except: pass
    return quotes_map

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    # Schriften
    try:
        font_big = pygame.font.SysFont("monospace", 85, bold=True)
        font_msg = pygame.font.SysFont("monospace", 20, bold=True)
    except:
        font_big = pygame.font.Font(None, 85)
        font_msg = pygame.font.Font(None, 20)

    quotes_data = load_quotes()
    last_update = 0
    current_id = "1"
    current_quote = "BOOTING..."
    
    # Effekt-Variablen
    scan_y = 0
    glitch_offset = 0
    glitch_timer = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Logik-Update alle 12 Sek
        if time.time() - last_update > 12:
            hour = datetime.now().hour
            current_id = "2" if 8 <= hour < 14 else ("4" if hour >= 20 else "1")
            if random.random() < 0.1: current_id = "3" # Zufalls-Panik 10%
            current_quote = random.choice(quotes_data.get(current_id, ["CORE ONLINE"]))
            last_update = time.time()

        # --- EFFEKT-LOGIK ---
        # 1. Scan-Balken Bewegung
        scan_y = (scan_y + 3) % HEIGHT
        
        # 2. Zufälliger Glitch (alle paar Sekunden für 3 Frames)
        if glitch_timer > 0:
            glitch_timer -= 1
            glitch_offset = random.randint(-5, 5)
        else:
            if random.random() < 0.02: # 2% Chance pro Frame
                glitch_timer = 3
            glitch_offset = 0

        # --- ZEICHNEN ---
        screen.fill(COLOR_BG)
        now = datetime.now()

        # Uhrzeit mit Glitch-Versatz
        t_surf = font_big.render(now.strftime("%H:%M"), True, COLOR_TOXIC)
        screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2 + glitch_offset, 20))

        # Käfer-Bild
        img_file = os.path.join(EMOTES_DIR, f"{current_id}.png")
        if os.path.exists(img_file):
            try:
                img = pygame.image.load(img_file).convert()
                img = pygame.transform.scale(img, (200, 200))
                # Bild zeichnen (mit Glitch)
                screen.blit(img, (WIDTH//2 - 100 + (glitch_offset*2), 120))
            except: pass

        # 3. Radar-Scan-Linie (Ein heller Strich der durchläuft)
        if 120 < scan_y < 320: # Nur im unteren Bereich
             s = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
             s.fill((0, 255, 60, 100)) # Transparentes Grün
             screen.blit(s, (0, scan_y))

        # 4. Statische Scanlines (Das Gitter)
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(screen, COLOR_SCANLINE, (0, y), (WIDTH, y))

        # Spruch unten
        msg_surf = font_msg.render(current_quote.upper(), True, (200, 255, 200))
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT-30))

        # 5. Rand-Vignette (macht die Ecken dunkler für Röhren-Look)
        pygame.draw.rect(screen, COLOR_TOXIC, (0,0,WIDTH,HEIGHT), 2) # Grüner Rahmen

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
