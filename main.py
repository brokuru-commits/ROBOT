#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, socket, urllib.request
from datetime import datetime
import pygame

# --- CONFIG ---
os.environ["SDL_VIDEODRIVER"] = "x11"
# Falls der Touch nicht geht, diese Zeilen aktivieren:
# os.environ["SDL_MOUSEDRV"] = "TSLIB"
# os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"

W, H = 480, 320
FPS = 30

# Farben
FALLOUT_GREEN = (50, 255, 50)
FALLOUT_DIM   = (10, 80, 10)
BLACK         = (0, 0, 0)
WHITE         = (255, 255, 255)
ALERT_RED     = (255, 50, 50)
BLUE_NEON     = (0, 200, 255)

# Pfade
BASE_DIR = os.path.expanduser("~/robot/ui/assets")
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
BG_PATH = os.path.join(BASE_DIR, "bg.png")

# GitHub Links
REPO_URL = "https://raw.githubusercontent.com/brokuru-commits/HEUM-tec/main/"
UPDATE_URL = REPO_URL + "main.py"
TODO_URL   = REPO_URL + "todo.txt"
ART_URL    = REPO_URL + "art.txt"

# --- DEIN STUNDENPLAN ---
# Format: (StundeStart, MinStart, StundeEnde, MinEnde, "Typ")
PLAN = [
    (7, 30, 8, 0, "ANKUNFT/PAUSE"),
    (8, 0, 8, 45, "UNTERRICHT 1"),
    (8, 45, 8, 50, "PAUSE (5min)"),
    (8, 50, 9, 35, "UNTERRICHT 2"),
    (9, 35, 9, 55, "PAUSE (20min)"),
    (9, 55, 10, 40, "UNTERRICHT 3"),
    (10, 40, 10, 45, "PAUSE (5min)"),
    (10, 45, 11, 30, "UNTERRICHT 4"),
    (11, 30, 11, 50, "PAUSE (20min)"),
    (11, 50, 12, 35, "UNTERRICHT 5"),
    (12, 35, 12, 40, "PAUSE (5min)"),
    (12, 40, 13, 25, "UNTERRICHT 6"),
    (13, 25, 13, 35, "PAUSE (10min)"),
    (13, 35, 14, 20, "UNTERRICHT 7"),
    (14, 20, 14, 25, "PAUSE (5min)"),
    (14, 25, 15, 10, "UNTERRICHT 8"),
    (15, 10, 15, 15, "PAUSE (5min)"),
    (15, 15, 16, 0, "UNTERRICHT 9"),
    (16, 0, 17, 0, "FEIERABEND")
]

# --- HELFER ---
def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read())/1000
    except: return 0.0

def fetch_data(url):
    try:
        r = urllib.request.urlopen(url, timeout=2)
        return [l.strip() for l in r.read().decode('utf-8').splitlines() if l.strip()]
    except: return []

def get_status():
    """Prüft genau, in welchem Block wir sind"""
    now = datetime.now()
    cur_min = now.hour * 60 + now.minute
    
    for (sh, sm, eh, em, label) in PLAN:
        start = sh * 60 + sm
        end = eh * 60 + em
        if start <= cur_min < end:
            # Wir sind mittendrin!
            total_duration = end - start
            passed = cur_min - start
            progress = passed / total_duration if total_duration > 0 else 0
            rest = end - cur_min
            return label, rest, progress
            
    return "FREIZEIT", 0, 0.0

# --- HAUPTPROGRAMM ---
def main():
    pygame.
