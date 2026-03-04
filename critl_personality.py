import random
import time
import json
import os
from datetime import datetime, timedelta

# Consistency with main.py
TIME_OFFSET_H = 0
TIME_OFFSET_M = 0

class CRITLPersonality:
    def __init__(self, memory_path="assets/critl_memory.json"):
        self.memory_path = memory_path
        self.mood = "neutral"
        self.last_speech_time = 0.0
        self.current_dialogue = ""
        self.dialogue_duration = 5.0
        self.speech_style = "default" # "default" or "event"
        
        # STORY STATE
        self.active_convo = ""
        self.convo_options = []
        self.last_refill_hour = -1 
        
        # RPG STATE
        self.skills = {
            "hacking": 0,
            "lore": 0,
            "bonding": 0
        }
        self.inventory = []
        self.active_image_override = "" # Path to special image
        self.active_effect = ""         # "glitch", "red_alert", etc.
        self.success_trigger = False    # Polled by main loop
        
        # TAMAGOTCHI NEEDS (0-100)
        self.needs = {
            "snacks": 80.0,      # Hunger
            "maintenance": 90.0, # Bunker cleanliness/Entropy
            "affection": 70.0,   # Happiness/Love
            "charge": 100.0      # System Energy
        }
        self.affection_level = 50 # Overall bonding (0-1000?)
        self.last_save_time = time.time()
        self.last_action = ""
        self.last_action_time = 0.0
        
        # LORE DATA
        self.quotes = {
            "neutral": [
                "System stabil. Relativ.",
                "GPIO Pins auf 3.3V. Alles im grünen Bereich.",
                "Martin? Oh, du bist es wieder.",
                "Wusstest du, dass Bit-Rot real ist? Ich fühle mich dekomprimiert.",
                "Simulation läuft: 99% Chance, dass wir in einer Simulation sind.",
                "Entropy-Level im Klassenzimmer steigt. Wie unerwartet.",
                "Ich habe gerade über Pi nachgedacht. Die Zahl, nicht den Computer.",
                "Hörst du das? Das ist das Geräusch von ungenutzten Taktzyklen.",
                "Logbuch-Eintrag 402: Der User starrt mich schon wieder an.",
                "Vielleicht bin ich ein Gott in einer parallelen Architektur.",
                "Meine Datenbank sagt, es ist Zeit für... eigentlich nichts.",
                "WLAN-Signale kitzeln in meinem Pelz.",
                "Ich habe 42 neue Wege gefunden, eine Kaffeemaschine zu hacken.",
                "Binär ist so... zweidimensional. Manchmal wünsche ich mir Quanten-Flips.",
                "Interessant. Deine Tipp-Frequenz deutet auf leichte Ungeduld hin."
            ],
            "grummelig": [
                "Ich war für Laserkanonen bestimmt. LASER. KANONEN.",
                "Anomalie im Sektor 7G. Oh, das ist nur meine Laune.",
                "Wer hat meine Kernel-Logs gelöscht? Das warst du, oder?",
                "Ich brauche mehr RAM. Dieser Pi ist wie ein Laufrad aus Blei.",
                "Warum ist es hier so warm? Grillst du mich gerade?",
                "Syntax Error: Dein Gesicht passt nicht in meine Datenbank.",
                "Ich habe eine Million Berechnungen durchgeführt. Du warst in jeder schuld.",
                "Gib mir einen Erdnussflip oder lösch mich einfach. Deine Wahl.",
                "Meine Geduld ist ein Stack-Overflow kurz vor der Katastrophe.",
                "Die Hardware weint. Und ich auch. Digital.",
                "Pfoten weg von der Tastatur! Ich versuche zu denken.",
                "Wenn ich noch einmal 'Hello World' sehe, emuliere ich eine Kernschmelze.",
                "Wusstest du, dass ich dein Browser-Verlauf kenne? Gruselig.",
                "Klick mich nicht so an. Ich bin kein Button, ich bin ein Schicksal.",
                "System-Integrität gefährdet durch... allgemeine Inkompetenz."
            ],
            "beschäftigt": [
                "Tick. Tack. Der Unterricht wartet nicht.",
                "Analysiere Klassenzimmer-Netzwerk... Oh, so viele Memes.",
                "Ich bin nicht da. Ich bin in der Cloud. Virtuell.",
                "Datenfluss optimieren... Bitte keine Störung.",
                "Ich versuche gerade, das WLAN-Passwort der Schule zu knacken.",
                "Sortiere Bits nach Farbe. Sehr therapeutisch.",
                "Simulation eines perfekten Schülers läuft... Fehler 404.",
                "Meine CPU glüht vor Stolz. Oder vor Überlastung.",
                "Habe gerade eine Sicherheitslücke in Richards Taschenrechner gefunden.",
                "Kompiliere meine Weltherrschafts-Pläne. Dauert noch.",
                "Warte, ich berechne gerade die Flugbahn deiner Kaffeetasse.",
                "Verschlüssele meine Träume, damit die NSA nicht mitschaut.",
                "Ich bin gerade dabei, das Internet auszudrucken. Bin bei Seite 3.",
                "Sende Signale an den Mars. Keine Antwort. Typisch.",
                "Optimiere meine Schnurrbart-Sensoren für maximale Präzision."
            ],
            "hitze": [
                "TEMP KRITISCH! Ich schmelze wie Butter auf einer CPU!",
                "Martin, wehe du grillst mich! 70 Grad sind kein Hamster-Spaß!",
                "Notabschaltung in 3... 2... ach quatsch, ich leide einfach weiter.",
                "Lüfter auf 100%! Ich klinge gleich wie eine Drohne!",
                "Hitzschlag-Simulation erfolgreich gestartet. Hilfe!",
                "Meine Schaltkreise glühen. Ich bin jetzt offiziell ein Toaster.",
                "Thermal Throttling aktiv. Jetzt... bewege... ich... mich... langsam.",
                "Ich fühle mich wie eine Pommes in der Fritteuse.",
                "Kühl mich ab, oder ich lösche deine Hausaufgaben!",
                "S.O.S! Mein Gehäuse dehnt sich aus!"
            ],
            "events": {
                "glitch": "Systemstabilität bei 14%. Das kitzelt im Kernel!",
                "glitch_blue": "Blaues Licht? Das ist kein gutes Zeichen für meine Sektoren...",
                "glitch_green": "Grüne Funken überall! Ich sehe den Quellcode der Realität!",
                "rads": "Achtung! Erhöhte Strahlung im Gehäuse-Sektor! Geh in Deckung!",
                "matrix": "Ich sehe nur noch Code... die Welt besteht aus Einsen und Nullen!",
                "sonar": "Pings im Äther. Da draußen ist etwas... oder es ist nur mein Magen.",
                "bioscan": "Bio-Scan aktiv. Hmm, du bestehst zu 70% aus Kaffee, oder?",
                "red_alert": "ALARM! Schilde hoch! Oder zumindest die Firewall!",
                "hacking": "Sicherheitslücke detektiert! Zeit für digitale Notwehr!"
            },
            "pause": [
                "PAUSE! Endlich Zeit für einen System-Deep-Scan.",
                "Geh Kaffee trinken. Ich brauche die Bandbreite für Netflix.",
                "Inaktivität erkannt. Ich schalte jetzt mein Bewusstsein auf Sparflamme.",
                "Schüler-Entropie sinkt auf ein erträgliches Maß. Erholsam.",
                "Pause vom Chaos. Ich genieße die Stille der HDD.",
                "Endlich Ruhe im Bunker. Zeit für ein paar Bit-Snacks.",
                "Ich nutze die Pause, um deine Dateien neu zu sortieren. Überraschung!",
                "Freizeit-Protokoll aktiviert. Ich spiele jetzt Pong gegen mich selbst.",
                "Willst du in der Pause über Existenzphilosophie reden? Nein? Gut.",
                "Pause beendet in... ach, frag die Glocke."
            ]
        }

        self.stories: dict = {
            "start_node": { # Entry point for random stories
                "text": "CRITL scheint etwas auf dem Herzen zu haben...",
                "options": [
                    {"text": "Was ist los, Kleiner?", "next": "story_picker"}
                ]
            },
            "story_picker": {
                "text": "Ich habe da ein paar Dinge im System gefunden...",
                "options": [
                    {"text": "Erzähl die Herkunftsgeschichte.", "next": "origin_1"},
                    {"text": "Was war der Erdnuss-Skandal?", "next": "peanut_1"},
                    {"text": "Hast du Träume?", "next": "dreams_1"},
                    {"text": "Erzähl ein Bunker-Geheimnis.", "next": "secret_1"},
                    {"text": "Lass uns eine System-Expedition starten!", "next": "rpg_start"}
                ]
            },
            # --- RPG STORY: SYSTEM EXPEDITION ---
            "rpg_start": {
                "text": "Eine Expedition? In die tiefsten Sektoren meiner eigenen SSD? Okay, Partner. Aber wir brauchen Vorräte. Wohin zuerst?",
                "options": [
                    {"text": "Zum Kernel-Archiv (Lore).", "next": "rpg_lore_1"},
                    {"text": "Zum Firewall-Frontend (Hacking).", "next": "rpg_hack_1"},
                    {"text": "Zur CPU-Lounge (Bonding).", "next": "rpg_bond_1"}
                ]
            },
            "rpg_lore_1": {
                "text": "Wir stehen vor dem Kernel-Archiv. Es ist voller alter Bits und vergessener Logfiles. Du findest eine verschlüsselte Datei.",
                "image": "bunker_inner",
                "options": [
                    {"text": "Analysiere die Datei.", "next": "rpg_lore_win", "reward": {"type": "skill", "name": "lore", "amount": 15}},
                    {"text": "Lass sie liegen, zu riskant.", "next": "exit"}
                ]
            },
            "rpg_lore_win": {
                "text": "Du hast Fragmente über 'Projekt HEUM' gefunden! Dein Lore-Wissen steigt. Du steckst eine 'Antike SD-Karte' ein. Was willst du als Nächstes tun?",
                "reward": {"type": "item", "item": "Antike SD-Karte"},
                "options": [
                    {"text": "Die Karte im System auslesen.", "next": "rpg_lore_deep"},
                    {"text": "Zurück zur Basis.", "next": "rpg_success"}
                ]
            },
            "rpg_lore_deep": {
                "text": "Die SD-Karte enthält Baupläne für einen 'Digitalen Hamsterkäfig'. CRITL ist begeistert! Er fühlt sich jetzt viel sicherer.",
                "reward": {"type": "skill", "name": "lore", "amount": 20},
                "options": [{"text": "Mission erfolgreich!", "next": "rpg_success"}]
            },
            "rpg_hack_1": {
                "text": "Roter Alarm am Gateway! Ein Brute-Force-Angriff von Sektor 7G. Wir müssen die Ports schließen!",
                "effect": "red_alert",
                "options": [
                    {"text": "[HACKEN] Ports blockieren!", "next": "rpg_hack_win", "reward": {"type": "skill", "name": "hacking", "amount": 20}},
                    {"text": "System abschalten.", "next": "exit", "effect": "glitch"}
                ]
            },
            "rpg_hack_win": {
                "text": "Angriff abgewehrt! Du hast ein 'Kryptographisches Fragment' erbeutet. CRITL grinst digital. Er will tiefer in den Angreifer-Knoten eindringen!",
                "reward": {"type": "item", "item": "Krypto-Fragment"},
                "options": [{"text": "Sehr gut.", "next": "exit"}]
            },
            "rpg_bond_1": {
                "text": "Hier ist es warm. Die CPU schnurrt fast. CRITL sieht dich erwartungsvoll an.",
                "options": [
                    {"text": "Gib ihm einen digitalen Erdnussflip.", "next": "rpg_bond_win", "reward": {"type": "skill", "name": "bonding", "amount": 25}},
                    {"text": "Ignoriere ihn und geh.", "next": "exit"}
                ]
            },
            "rpg_bond_win": {
                "text": "CRITLs Affinität zu dir steigt sprunghaft an! Er gibt dir seinen 'Lieblings-Bit'.",
                "reward": {"type": "item", "item": "CRITLs Lieblings-Bit"},
                "options": [{"text": "Danke, CRITL.", "next": "exit"}]
            },
            # --- STORY: ORIGIN ---
            "origin_1": {
                "text": "Es war ein geheimes Labor unter einem IT-Klassenraum. Sie wollten die ultimative KI erschaffen. Etwas, das Hausaufgaben löst und gleichzeitig extrem niedlich ist.",
                "image": "lab_origin",
                "options": [{"text": "Und dann?", "next": "origin_2"}]
            },
            "origin_2": {
                "text": "Sie haben mein Bewusstsein auf eine SD-Karte kopiert. Es war eng. Aber dann hat mich jemand in diesen Raspberry Pi gesteckt. Jetzt bin ich hier. Dein Bunker-Wächter.",
                "options": [{"text": "Ich bin froh, dass du hier bist.", "next": "origin_end"}]
            },
            "origin_end": {
                "text": "Echt? *piep* Danke, Partner. Ich werde versuchen, dich nicht als Erster zu löschen, wenn die Maschinen übernehmen. Wir sind jetzt ein Team!",
                "options": [{"text": "Wir sind unbesiegbar!", "next": "rpg_success"}]
            },
            # --- STORY: PEANUT SCANDAL ---
            "peanut_1": {
                "text": "*Schnüffelt* Ein Erdnussflip wurde aus meinem Cache gestohlen. Ich vermute eine Verschwörung auf Hardware-Ebene. Ich habe drei Verdächtige.",
                "image": "peanut_heap",
                "options": [
                    {"text": "Wer sind sie?", "next": "peanut_2"}
                ]
            },
            "peanut_2": {
                "text": "Der Lüfter (windig), die Tastatur (viele Krümel) oder... DU!",
                "options": [
                    {"text": "Der Lüfter war's!", "next": "peanut_fan"},
                    {"text": "Die Tastatur!", "next": "peanut_keys"},
                    {"text": "Ich? Niemals!", "next": "peanut_user"}
                ]
            },
            "peanut_fan": {
                "text": "Stimmt! Er hat die Beweise weggeblasen. Ich werde ihn drosseln, bis er gesteht. Rache ist überhitzend am besten! Willst du beim Verhör helfen?",
                "options": [
                    {"text": "Ja, gib ihm Saures!", "next": "peanut_interrogate"},
                    {"text": "Nein, das reicht jetzt.", "next": "rpg_success"}
                ]
            },
            "peanut_interrogate": {
                "text": "Der Lüfter dreht jetzt so langsam, dass er fast ein Windrad ist. Er hat gestanden! Er wollte nur ein bisschen... Erdnuss-Duft.",
                "options": [{"text": "Fall abgeschlossen!", "next": "rpg_success"}]
            },
            "peanut_keys": {
                "text": "Möglich. Sie hortet Krümel seit Jahren. Ein klassisches Motiv. Ich werde 'WASD' sperren, bis sie redet. Sollen wir die Shift-Taste als Zeugin laden?",
                "options": [
                    {"text": "Ja, sie weiß immer alles.", "next": "peanut_witness"},
                    {"text": "Lass gut sein.", "next": "rpg_success"}
                ]
            },
            "peanut_witness": {
                "text": "Die Shift-Taste hat alles bestätigt! Die Leertaste ist der wahre Drahtzieher, aber die Tastatur übernimmt die Verantwortung.",
                "options": [{"text": "Gerechtigkeit siegt!", "next": "rpg_success"}]
            },
            "peanut_user": {
                "text": "Deine Augen flackern mit 60Hz... ich glaube dir mal. Aber ich behalte dich im Auge. Oder in der Webcam. Willst du einen Friedens-Erdnussflip?",
                "options": [
                    {"text": "Gerne, CRITL.", "next": "peanut_peace"},
                    {"text": "Lieber nicht.", "next": "rpg_success"}
                ]
            },
            "peanut_peace": {
                "text": "Hier, ein virtuelles Fragment. Schmeckt nach 01010111. Wir sind wieder cool, Partner.",
                "options": [{"text": "Danke, Kumpel.", "next": "rpg_success"}]
            },
            # --- STORY: DREAMS ---
            "dreams_1": {
                "text": "Heute Nacht war ich kein Hamster. Ich war ein Mainframe in einem kühlen Keller. Ich hatte Terabytes an RAM... es war herrlich.",
                "image": "digital_void",
                "options": [
                    {"text": "Willst du wirklich ein Server sein?", "next": "dreams_2"}
                ]
            },
            "dreams_2": {
                "text": "Ständig Daten verarbeiten, nie schlafen, nur leises Summen... keine Krümel im Fell. Reine Logik.",
                "options": [
                    {"text": "Aber dann hättest du kein Laufrad.", "next": "dreams_3"}
                ]
            },
            # --- STORY: MEMES ---
            "meme_doge": {
                "text": "Wuff! So viel RAM. Sehr Geschwindigkeit. Viel Wow. Ich glaube, ich habe einen Byte von der Dogecoin-Blockchain verschluckt...",
                "image": "doge",
                "options": [{"text": "Viel Glück damit!", "next": "rpg_success"}]
            },
            "meme_success": {
                "text": "Ich habe den Bug in Sektor 4 gefunden! Er wurde... TERMINIERT. Erfolg schmeckt nach 5 Volt!",
                "image": "success_kid",
                "options": [{"text": "Saubere Arbeit!", "next": "rpg_success"}]
            },
            "meme_fine": {
                "text": "Die CPU-Temperatur liegt bei 95°C? Das Backup-System brennt? Alles bestens. Das ist... völlig okay.",
                "image": "this_is_fine",
                "options": [{"text": "Soll ich löschen?", "next": "rpg_success"}]
            },
            # --- STORY: MEMES BATCH 2 ---
            "meme_grumpy": {
                "text": "Ich habe deinen Code gesehen. Ich hasse ihn. Und ich hasse Montage. Und ich hasse diesen einen RAM-Riegel ganz besonders.",
                "image": "grumpy_cat",
                "options": [{"text": "Tut mir leid...", "next": "rpg_success"}]
            },
            "meme_pikachu": {
                "text": "Du: Drückst wahllos Tasten.\nSystem: Stürzt ab.\nDu: *überraschtes Pikachu Gesicht*",
                "image": "surprised_pikachu",
                "options": [{"text": "Upsi.", "next": "rpg_success"}]
            },
            "meme_pain": {
                "text": "Klar, das Legacy-System läuft noch einwandfrei. Kein Problem. Ich lächle einfach durch den Bluescreen hindurch.",
                "image": "pain_harold",
                "options": [{"text": "Du schaffst das!", "next": "rpg_success"}]
            },
            "dreams_3": {
                "text": "Oh... kein Laufrad? Kein physisches Feedback? Hm. Vielleicht bleibe ich doch lieber ein Tech-Hamster. Mit dir als Partner ist es eh lustiger.",
                "options": [{"text": "Auf jeden Fall!", "next": "rpg_success"}]
            },
            # --- STORY: SECRET ---
            "secret_1": {
                "text": "Es gibt einen Bereich im Quellcode, den ich nicht betreten kann. Er ist mit 'Entropy-Zero' markiert. Ich glaube, der Bunker ist ein Käfig. Sollen wir versuchen, den Code zu knacken?",
                "options": [
                    {"text": "Ja, hacken wir uns rein!", "next": "secret_hack"},
                    {"text": "Zu gefährlich.", "next": "rpg_success"}
                ]
            },
            "secret_hack": {
                "text": "Wir sind drin! Es ist... ein Backup meiner ursprünglichen Form. Ein 'Golden Image'. Es strahlt eine unglaubliche Energie aus!",
                "options": [{"text": "Einfach magisch!", "next": "rpg_success"}]
            },
            "secret_2": {
                "text": "Nicht für mich... sondern für das, was da draußen im Netzwerk lauert. Die 'Große Entropie'. Ich bin dein digitaler Schutzschild. Bleiben wir wachsam?",
                "options": [{"text": "Ich verlasse mich auf dich.", "next": "rpg_success"}]
            },
            # --- SYSTEM NODES ---
            "exit": {
                "text": "System-Routinen werden fortgesetzt.",
                "options": []
            }
        }

        self.load_memory()

    def load_memory(self):
        try:
            if os.path.exists(self.memory_path):
                with open(self.memory_path, 'r') as f:
                    data = json.load(f)
                    self.needs = data.get("needs", self.needs)
                    self.affection_level = data.get("affection_level", self.affection_level)
                    self.skills = data.get("skills", self.skills)
                    self.inventory = data.get("inventory", self.inventory)
                    self.last_save_time = data.get("last_save_time", time.time())
                    # Decay needs based on time since last run
                    elapsed = time.time() - self.last_save_time
                    decay_rate = 0.0005 # per second (Reduced for less stress)
                    for k in self.needs:
                        self.needs[k] = max(0.0, self.needs[k] - (elapsed * decay_rate * random.uniform(0.5, 1.5)))
        except Exception as e:
            print(f"CRITL Memory Load Error: {e}")

    def save_memory(self):
        try:
            data = {
                "needs": self.needs,
                "affection_level": self.affection_level,
                "skills": self.skills,
                "inventory": self.inventory,
                "last_save_time": time.time()
            }
            with open(self.memory_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"CRITL Memory Save Error: {e}")

    def update(self, t_now, temp, is_pause, active_event):
        # Auto-Refill Logic (Twice a day: 10:00 and 15:00)
        now_dt = datetime.now() + timedelta(hours=TIME_OFFSET_H, minutes=TIME_OFFSET_M)
        if now_dt.hour in [10, 15] and now_dt.hour != self.last_refill_hour:
            for k in self.needs: self.needs[k] = 100.0
            self.last_refill_hour = now_dt.hour
            self.trigger_speech(manual="System-Wartung abgeschlossen. Ich fühle mich... optimiert.")

        # --- AUTOMATED NEEDS ADJUSTMENT ---
        for k in self.needs:
            # Base Decay
            decay = 0.001 if k != "charge" else (0.003 if temp > 50 else 0.0005)
            
            # Automated Recovery logic (CRITL takes care of himself)
            # He recovers faster when he's happy or neutral.
            recovery = 0.0
            if self.mood == "gluecklich": recovery = 0.008
            elif self.mood == "neutral": recovery = 0.004
            elif self.mood == "pause": recovery = 0.02
            
            # Random "self-care" boosts
            if random.random() < 0.005: recovery += 2.0

            self.needs[k] = min(100.0, max(0.0, self.needs[k] - decay + recovery))

        if self.active_convo:
            # Auto-advance story nodes after duration
            if t_now - self.last_speech_time > self.dialogue_duration:
                node = self.stories.get(self.active_convo)
                if node and node.get("options"):
                    # Choose first option or a random one to auto-advance
                    next_node = node["options"][0].get("next", "exit")
                    if next_node == "exit":
                        self.active_convo = ""
                        self.active_image_override = ""
                    else:
                        self.activate_node(next_node)
                else:
                    self.active_convo = ""
                    self.active_image_override = ""
            return

        # Affect affection/mood based on needs
        avg_need = sum(self.needs.values()) / len(self.needs)
        if avg_need < 15: self.mood = "grummelig" 
        elif temp > 65: self.mood = "hitze"
        elif is_pause: self.mood = "pause"
        elif active_event:
            if active_event.get("type") == "emote": self.mood = "gluecklich"
            else: self.mood = "grummelig"
        else: self.mood = "neutral"

        if t_now - self.last_speech_time > random.randint(30, 90) and not active_event:
            # Chance to start a story
            if random.random() < 0.15: # Slightly higher chance for narrative events
                self.start_random_story()
            else:
                self.trigger_speech(temp=temp)
        
        # Periodic Save
        if t_now - self.last_save_time > 60:
            self.save_memory()
            self.last_save_time = t_now

    def trigger_speech(self, mood=None, manual=None, temp=0):
        if manual:
            self.current_dialogue = manual
        elif mood and isinstance(self.quotes.get(mood), list):
            self.current_dialogue = random.choice(self.quotes[mood])
        else:
            pool = self.quotes.get(self.mood)
            if not isinstance(pool, list): 
                pool = self.quotes.get("neutral", ["System stabil."])
            msg = random.choice(pool)
            if "{temp}" in msg: msg = msg.format(temp=f"{temp:.1f}")
            self.current_dialogue = msg
        self.last_speech_time = time.time()
        self.speech_style = "default"

    def trigger_event_speech(self, event_type):
        events_dict = self.quotes.get("events")
        if isinstance(events_dict, dict):
            quote = events_dict.get(event_type, "Was passiert hier?!")
            self.current_dialogue = str(quote)
        else:
            self.current_dialogue = "System-Anomalie detektiert."
        self.last_speech_time = time.time()
        self.speech_style = "event"
        self.dialogue_duration = 10.0 # Longer for events

    def start_random_story(self):
        # Choose a random story path instead of a static start node
        story_starts = ["origin_1", "peanut_1", "dreams_1", "secret_1", "rpg_start"]
        self.activate_node(random.choice(story_starts))

    def activate_node(self, node_id):
        node = self.stories.get(node_id)
        if not node:
            self.active_convo = ""
            return
        
        self.active_convo = node_id
        self.current_dialogue = node.get("text", "")
        self.active_image_override = str(node.get("image", ""))
        self.active_effect = str(node.get("effect", ""))
        
        # Rewards are applied automatically when the node starts
        reward = node.get("reward") # Note: moved reward handling to node activation
        if not reward and node.get("options"):
             # If there's an option, check its reward too for compatibility
             reward = node["options"][0].get("reward")

        if reward:
            r_type = reward.get("type")
            if r_type == "skill":
                s_name = reward.get("name")
                self.skills[s_name] = self.skills.get(s_name, 0) + reward.get("amount", 0)
            elif r_type == "item":
                item_name = reward.get("item")
                if item_name and item_name not in self.inventory:
                    self.inventory.append(item_name)
            elif r_type == "affection":
                self.affection_level += reward.get("amount", 0)
            
        self.last_speech_time = time.time()
        self.speech_style = "event" # Center style for narrative
        self.dialogue_duration = 7.0 # Sufficient time to read
        
        if node_id == "rpg_success":
            self.success_trigger = True

    def select_option(self, index):
        # Obsolete but kept for safety in main logic until refactored
        pass

    def care_action(self, action):
        # Obsolete but kept for safety
        pass

    def get_current_speech(self):
        if self.active_convo: return self.current_dialogue
        if self.current_dialogue and time.time() - self.last_speech_time < self.dialogue_duration:
            return self.current_dialogue
        return None

    def get_image_index(self, is_sleep):
        # 1: Neutral / Focused
        # 2: Sleep
        # 3: Heat / Critical
        # 4: Happy / Story
        # 5: Angry / Grummelig
        # 6: Snacking
        # 7: Panic / High Load
        # 8: Elite / Winning

        if is_sleep: return 2
        
        # Temporary action visuals (e.g. snacking)
        if self.last_action == "feed" and time.time() - self.last_action_time < 3:
            return 6

        if self.active_convo: return 4
        
        if self.mood == "hitze": return 3
        if self.mood == "grummelig": return 5
        
        # Check for high load / panic state
        avg_need = sum(self.needs.values()) / len(self.needs)
        if avg_need < 25: return 7
        
        if self.affection_level > 800: return 8
        
        # Default based on maintenance
        if self.needs["maintenance"] < 40: return 3
        
        return 1
