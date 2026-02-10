#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, random, urllib.request, py_compile
from datetime import datetime
import pygame

# =========================
# SYSTEM CONFIG
# =========================
os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"

W, H = 480, 320
FPS = 30
VERSION = "V 3.4 SAFE"

# =========================
# PFADE (Sicherer Fix für Autostart)
# =========================
# Wir ermitteln den Pfad, wo das Skript liegt, damit es immer die Bilder findet
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

FONT_PATH = os.path.join(ASSETS_DIR, "font.ttf")
BG_PATH   = os.path.join(ASSETS_DIR, "bg.png")
QUOTES_PATH = os.path.join(ASSETS_DIR, "quotes.txt")

# =========================
# DATEN
# =========================
COLOR_MODES = [
    (50, 255, 50),   # Green
    (255, 180, 0),   # Amber
    (0, 200, 255),   # Blue
    (255, 50, 50)    # Red
]

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --- SICHERE EMOJIS (Keine Sonderzeichen!) ---
# Wir nutzen nur Zeichen, die JEDE Schriftart kann.
EMOJIS = [
    "( ^_^ )", 
    "( o_o )", 
    "( O_O )", 
    "( -_- )", 
    "( ^.^ )", 
    "[ 0_0 ]", 
    "( >_< )",
    "( $_$ )"
]

DEFAULT_QUOTES = ["SYSTEMS OPTIMAL.", "LERNEN...", "WARTE AUF EINGABE", "RAD-LEVEL NORMAL."]

SCALE_GYM = [95, 80, 65, 50, 25, 0]
SCALE_RS  = [90, 75, 60, 45, 20, 0]

PLAN = [
    (7,30,8,0,"PAUSE"),(8,0,8,45,"1. STUNDE"),(8,45,8,50,"PAUSE"),
    (8,50,9,35,"2. STUNDE"),(9,35,9,55,"HOFPAUSE"),(9,55,10,40,"3. STUNDE"),
    (10,40,10,45,"PAUSE"),(10,45,11,30,"4. STUNDE"),(11,30,11,50,"ESSEN"),
    (11,50,12,35,"5. STUNDE"),(12,35,12,40,"PAUSE"),(12,40,13,25,"6. STUNDE"),
    (13,25,13,35,"PAUSE"),(13,35,14,20,"7. STUNDE"),(14,20,14,25,"PAUSE"),
    (14,25,15,10,"8. STUNDE"),(15,10,15,15,"PAUSE"),(15,15,16,0,"9. STUNDE"),
    (16,0,17,0,"ENDE")
]

# =========================
# HILFSFUNKTIONEN
# =========================

def load_quotes():
    q = []
    if os.path.exists(QUOTES_PATH):
        try:
            with open(QUOTES_PATH, "r", encoding="utf-8") as f:
                q = [line.strip() for line in f if line.strip()]
        except: pass
    return q if q else DEFAULT_QUOTES

def get_status_data():
    now = datetime.now()
    cur = now.hour * 3600 + now.minute * 60 + now.second
    for (sh, sm, eh, em, label) in PLAN:
        start = sh * 3600 + sm * 60
        end   = eh * 3600 + em * 60
        if start <= cur < end:
            total = max(1, end - start)
            return label, f"{sh:02d}:{sm:02d}-{eh:02d}:{
