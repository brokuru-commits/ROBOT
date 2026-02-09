#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, socket, urllib.request
from datetime import datetime, date
import pygame

# --- CONFIG & TOUCH-FIX ---
os.environ["SDL_VIDEODRIVER"] = "x11"
# Falls der Touch am Display klemmt, diese Zeilen im Terminal nutzen:
# export SDL_MOUSEDRV=TSLIB && export SDL_MOUSEDEV=/dev/input/touchscreen

W, H = 480, 320
FPS = 30
GREEN_BRIGHT = (100, 255, 100)
GREEN_DIM = (20, 80, 20)
BLACK = (0, 0, 0)
VERSION = "V 1.2" 

# Pfade (Stelle sicher, dass der Ordner existiert)
BASE_DIR = os.path.expanduser("~/robot/ui/assets")
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
BG_PATH = os.path.join(BASE_DIR, "bg.png")

# --- DEINE CLOUD-LINKS ---
UPDATE_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/main.py"
TODO_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/todo.txt"

# --- SYSTEM-FUNKTIONEN ---
def get_sys():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read())/1000
        return temp
    except: return 0.0

def get_todo():
    """Lädt die To-Do Liste von GitHub"""
    try:
        response = urllib.request.urlopen(TODO_URL, timeout=5)
        lines = response.read().decode('utf-8').splitlines()
        # Nur die ersten 5 Zeilen nehmen, damit es auf den Screen passt
        return [line.strip() for line in lines if line.strip()][:5]
    except:
        return ["KEINE VERBINDUNG", "ZUM SERVER"]

class Button:
    def __init__(self, x, y, w, h, text, color=GREEN_DIM):
        self.rect = pygame.Rect(x,y,w,h); self.text = text; self.color = color; self.act = 0
    def draw(self, screen, font):
        c = GREEN_BRIGHT if time.time()-self.act < 0.15 else self.color
        pygame.draw.rect(screen, c, self.rect); pygame.draw.rect(screen, GREEN_BRIGHT, self.rect, 1)
        t = font.render(self.text, True, BLACK if c==GREEN_BRIGHT else GREEN_BRIGHT)
        screen.blit(t, t.get_rect(center=self.rect.center))

def main():
    pygame.init()
    pygame.mouse.set_visible(True) # Cursor anzeigen für Touch-Check
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    
    # Fonts laden
    try:
        f_h = pygame.font.Font(FONT_PATH, 70) # Uhr
        f_b = pygame.font.Font(FONT_PATH, 28) # Datum / Button
        f_m = pygame.font.Font(FONT_PATH, 18) # To-Do Titel
        f_s = pygame.font.Font(FONT_PATH, 15) # To-Do Items / Version
    except:
        print("Font nicht gefunden, nutze Systemfont")
        f_h = pygame.font.SysFont(None, 70); f_b = pygame.font.SysFont(None, 30)
        f_m = f_s = pygame.font.SysFont(None, 20)

    # Initiales Laden der To-Do Liste
    todo_list = get_todo()
    
    btn_start = Button(270, 225, 190, 65, "START")
    btn_update = Button(445, 5, 30, 30, "!", (40,40,40))
    
    p_x, p_dir = 0, 1 # Für das Lauflicht

    while True:
        screen.fill(BLACK)
        now = datetime.now()
        
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                # 1. UPDATE BUTTON (Das !)
                if btn_update.rect.collidepoint(e.pos):
                    st_t = time.time()
                    while time.time()-st_t < 1.0: # Meltdown Animation
                        screen.fill((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
                        pygame.display.flip(); time.sleep(0.05)
                    try:
                        urllib.request.urlretrieve(UPDATE_URL, "/home/bot/robot/ui/main.py")
                    except: pass
                    sys.exit() # Beenden für Neustart
                
                # 2. START BUTTON (Aktualisiert auch die To-Dos)
                if btn_start.rect.collidepoint(e.pos):
                    btn_start.act = time.time()
                    # Sofortiger Sync mit GitHub beim Klick:
                    todo_list = get_todo()

        # --- ZEICHNEN ---
        # Uhr & Datum
        screen.blit(f_h.render(now.strftime("%H:%M"), True, GREEN_BRIGHT), (20, 10))
        screen.blit(f_b.render(now.strftime("%d.%m.%Y"), True, GREEN_DIM), (25, 80))
        
        # To-Do Liste Anzeige
        screen.blit(f_m.render("PROJEKTE / TO-DO:", True, GREEN_BRIGHT), (25, 130))
        y_off = 160
        for item in todo_list:
            # Kleiner Punkt vor dem Item
            pygame.draw.circle(screen, GREEN_DIM, (35, y_off + 10), 3)
            screen.blit(f_s.render(item, True, GREEN_DIM), (45, y_off))
            y_off += 25

        # System Status (Rechts oben/mitte)
        temp = get_sys()
        screen.blit(f_s.render(f"CPU TEMP: {temp:.1f}C", True, GREEN_DIM), (280, 140))
        
        # Versionsnummer ganz unten links
        screen.blit(f_s.render(VERSION, True, (60, 60, 60)), (5, 305))

        # Buttons zeichnen
        btn_start.draw(screen, f_b)
        btn_update.draw(screen, f_m)

        # Das HEUM-Tec Lauflicht (unten)
        p_x += 3 * p_dir
        if p_x > 430 or p_x < 0: p_dir *= -1
        pygame.draw.rect(screen, GREEN_BRIGHT, (25+p_x, 314, 15, 2))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
