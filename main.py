#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, math, random
from datetime import datetime
import pygame

# --- SETTINGS ---
W, H = 640, 480
FPS = 25
GREEN, GREEN_SOFT, BLACK, WHITE = (80, 255, 80), (120, 255, 120), (0, 0, 0), (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((W,H), pygame.FULLSCREEN | pygame.NOFRAME)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# --- ASSETS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
font_time, font_body, font_small = pygame.font.SysFont("monospace", 75), pygame.font.SysFont("monospace", 32), pygame.font.SysFont("monospace", 22)

# Hamster MASIV auf 400x400 skaliert
critl_imgs = {}
for i in range(1, 5):
    p = os.path.join(ASSET_DIR, f"{i}.png")
    if os.path.exists(p):
        critl_imgs[i] = pygame.transform.smoothscale(pygame.image.load(p).convert_alpha(), (400, 400))

# --- ICONS (JETZT RICHTIG GRÜN) ---
def draw_icons(t):
    start_x, y, r, g, b = W - 110, 20, 80, 255, 80
    # WiFi
    alpha = int(100 + 100 * math.sin(t * 0.8))
    s = pygame.Surface((34,34), pygame.SRCALPHA)
    for i in range(3): pygame.draw.arc(s, (r,g,b,alpha), (5+i*4, 8+i*4, 24-i*8, 24-i*8), 0.7, 2.4, 2)
    screen.blit(s, (start_x, y))
    # Rad
    alpha_r = int(100 + 100 * math.sin(t * 0.5))
    s_r = pygame.Surface((34,34), pygame.SRCALPHA)
    pygame.draw.circle(s_r, (r,g,b,alpha_r), (17,17), 5)
    screen.blit(s_r, (start_x + 35, y))

# --- MAIN LOOP ---
last_face_change, active_face = 0, "(o_o)"

while True:
    t_now = time.time(); clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

    screen.fill(BLACK) # Hier kommt dein bg.png hin
    now = datetime.now()

    # LINKS: Uhrzeit & Datum
    screen.blit(font_time.render(now.strftime("%H:%M"), True, GREEN), (20, 30))
    screen.blit(font_body.render(now.strftime("%d.%m."), True, GREEN_SOFT), (25, 110))

    # LINKS: Smiley mit Glow
    if t_now - last_face_change > 5:
        active_face = random.choice(["(o_o)", "(^.^)", "( -_-)", "(⌐■_■)", "(◕‿◕)"])
        last_face_change = t_now
    screen.blit(font_body.render(active_face, True, (20, 100, 20)), (27, 182)) # Glow
    screen.blit(font_body.render(active_face, True, GREEN), (25, 180))

    # RECHTS: Der Mega-Hamster (400px)
    # Position: Ganz rechts unten in der Ecke
    img = critl_imgs.get(1)
    if img: screen.blit(img, (W - 410, H - 430))

    # OBEN RECHTS: Icons
    draw_icons(t_now)

    pygame.display.flip()
