#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, socket, urllib.request
from datetime import datetime, date
import pygame

# --- CONFIG ---
os.environ["SDL_VIDEODRIVER"] = "x11"
W, H = 480, 320
FPS = 30
GREEN_BRIGHT = (100, 255, 100)
GREEN_DIM = (20, 80, 20)
BLACK = (0, 0, 0)
VERSION = "V 1.4" 

# Pfade
BASE_DIR = os.path.expanduser("~/robot/ui/assets")
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
BG_PATH = os.path.join(BASE_DIR, "bg.png")

# GitHub Links
UPDATE_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/main.py"
TODO_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/todo.txt"
QUOTES_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/quotes.txt"
ART_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/art.txt"

# --- HELFER-FUNKTIONEN ---
def get_sys():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read())/1000
    except: return 0.0

def fetch_data(url, default=["Fehler"]):
    try:
        response = urllib.request.urlopen(url, timeout=3)
        return response.read().decode('utf-8').splitlines()
    except: return default

def get_random_art():
    """Lädt art.txt und gibt ein zufälliges Bild (getrennt durch ---) zurück"""
    lines = fetch_data(ART_URL, ["(o.o)"])
    full_text = "\n".join(lines)
    arts = full_text.split("---")
    return random.choice(arts).strip().split("\n")

class Button:
    def __init__(self, x, y, w, h, text, color=GREEN_DIM):
        self.rect = pygame.Rect(x,y,w,h); self.text = text; self.color = color; self.act = 0
    def draw(self, screen, font):
        c = GREEN_BRIGHT if time.time()-self.act < 0.15 else self.color
        pygame.draw.rect(screen, c, self.rect); pygame.draw.rect(screen, GREEN_BRIGHT, self.rect, 1)
        t = font.render(self.text, True, BLACK if c==GREEN_BRIGHT else GREEN_BRIGHT)
        screen.blit(t, t.get_rect(center=self.rect.center))

# --- BOOT SCREEN MIT ZUFALLS-KUNST ---
def run_boot_screen(screen, f_b, f_m, f_s):
    start_t = time.time()
    boot_quotes = fetch_data(QUOTES_URL, ["LADE SYSTEM...", "HEUM-TEC ONLINE."])
    random_art = get_random_art()
    
    while time.time() - start_t < 4:
        screen.fill(BLACK)
        prog = int(((time.time()-start_t)/4)*100)
        
        # ASCII Art zeichnen (zentriert)
        for i, line in enumerate(random_art):
            art_surf = f_s.render(line, True, GREEN_BRIGHT)
            screen.blit(art_surf, (W//2 - art_surf.get_width()//2, 180 + (i*15)))

        # Header & Ladebalken
        txt = f_b.render("HEUM-TEC SYSTEMS", True, GREEN_BRIGHT)
        screen.blit(txt, (W//2-txt.get_width()//2, 30))
        pygame.draw.rect(screen, GREEN_BRIGHT, (90, 100, 300, 20), 1)
        pygame.draw.rect(screen, GREEN_BRIGHT, (93, 103, int(294*(min(prog,100)/100)), 14))
        
        # Zitat
        q_idx = min(int((prog/101)*len(boot_quotes)), len(boot_quotes)-1)
        quote_surf = f_m.render(boot_quotes[q_idx], True, GREEN_DIM)
        screen.blit(quote_surf, (W//2-quote_surf.get_width()//2, 130))
        
        pygame.display.flip()

def main():
    pygame.init()
    pygame.mouse.set_visible(True)
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    
    try:
        f_h = pygame.font.Font(FONT_PATH, 70); f_b = pygame.font.Font(FONT_PATH, 28)
        f_m = pygame.font.Font(FONT_PATH, 18); f_s = pygame.font.Font(FONT_PATH, 14)
    except:
        f_h = pygame.font.SysFont(None, 70); f_b = pygame.font.SysFont(None, 30); f_m = f_s = pygame.font.SysFont(None, 20)

    # Initiales Booten & To-Do
    run_boot_screen(screen, f_b, f_m, f_s)
    todo_list = fetch_data(TODO_URL, ["KEIN SYNC"])[:5]
    
    btn_start = Button(270, 225, 190, 65, "START")
    btn_update = Button(445, 5, 30, 30, "!", (40,40,40))
    p_x, p_dir = 0, 1

    while True:
        screen.fill(BLACK)
        now = datetime.now()
        
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_update.rect.collidepoint(e.pos):
                    # Update Animation & Download
                    try: urllib.request.urlretrieve(UPDATE_URL, "/home/bot/robot/ui/main.py")
                    except: pass
                    sys.exit()
                if btn_start.rect.collidepoint(e.pos):
                    btn_start.act = time.time()
                    todo_list = fetch_data(TODO_URL, ["KEIN SYNC"])[:5]

        # UI Elemente
        screen.blit(f_h.render(now.strftime("%H:%M"), True, GREEN_BRIGHT), (20, 10))
        screen.blit(f_b.render(now.strftime("%d.%m.%Y"), True, GREEN_DIM), (25, 80))
        screen.blit(f_m.render("TO-DO LISTE:", True, GREEN_BRIGHT), (25, 130))
        for i, item in enumerate(todo_list):
            screen.blit(f_s.render(f"> {item}", True, GREEN_DIM), (35, 160 + (i*25)))
        
        screen.blit(f_s.render(f"TEMP: {get_sys():.1f}C", True, GREEN_DIM), (300, 140))
        screen.blit(f_s.render(VERSION, True, (50, 50, 50)), (5, 305))
        
        btn_start.draw(screen, f_b)
        btn_update.draw(screen, f_m)
        
        # Lauflicht
        p_x += 3 * p_dir
        if p_x > 430 or p_x < 0: p_dir *= -1
        pygame.draw.rect(screen, GREEN_BRIGHT, (25+p_x, 314, 15, 2))
        
        pygame.display.flip(); clock.tick(FPS)

if __name__ == "__main__": main()
