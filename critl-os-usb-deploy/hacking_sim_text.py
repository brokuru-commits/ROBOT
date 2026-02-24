#!/usr/bin/env python3
import random

# Simplified text-based version of HackingGame logic
class TextHackingGame:
    def __init__(self):
        self.words = ["VAULT", "NUCLEAR", "ATOMIC", "RADS", "PIPBOY", "STIMPAK", "MUTANT", "GHOUL", "WASTELAND", "POWER", "ARMOR", "LASER", "PLASMA", "DEATH", "CLAW", "ROBOT", "SYSTEM", "HACK", "ACCESS", "DENIED", "GRANT", "USER", "ADMIN", "ROOT"]
        self.word_length = 5
        self.attempts = 4
        self.grid_width = 12
        self.grid_height = 16
        self.reset_game()

    def reset_game(self):
        self.attempts = 4
        self.locked_out = False
        self.won = False
        self.history = []
        
        self.current_words = [w for w in self.words if abs(len(w) - self.word_length) <= 1]
        if len(self.current_words) < 10: self.current_words = self.words
        chosen_len = len(random.choice(self.current_words))
        self.game_words = [w for w in self.current_words if len(w) == chosen_len]
        if len(self.game_words) > 15: self.game_words = random.sample(self.game_words, 15)
            
        self.password = random.choice(self.game_words)
        self.word_len = len(self.password)
        
        # Build logical grid for display simulation
        total_chars = self.grid_width * self.grid_height * 2
        garbage = "!@#$%^&*()_+-=[]{}|;':,./<>?"
        self.grid_data = [] 
        occupied_indices = set()
        self.placed_words = []
        
        for w in self.game_words:
            for _ in range(100):
                idx = random.randint(0, total_chars - len(w))
                collision = False
                for i in range(len(w)):
                    if (idx + i) in occupied_indices:
                        collision = True; break
                if not collision:
                    for i in range(len(w)): occupied_indices.add(idx + i)
                    self.placed_words.append({'word': w, 'start': idx})
                    break
        
        # Sort so we can print somewhat in order
        self.placed_words.sort(key=lambda x: x['start'])

    def get_likeness(self, word):
        count = 0
        for i in range(min(len(word), len(self.password))):
            if word[i] == self.password[i]: count += 1
        return count

    def play(self):
        print(f"\n--- ROBCO INDUSTRIES (TM) TERMLINK PROTOCOL ---")
        print(f"PASSWORD REQUIRED. ATTEMPTS LEFT: {self.attempts}")
        print(f"POSSIBLE PASWORDS: {', '.join(sorted([w['word'] for w in self.placed_words]))}")
        print("(In the real GUI version, these are hidden in a hex grid of characters!)")
        
        while not self.won and not self.locked_out:
            guess = input(f"\n> ENTER PASSWORD ({self.attempts} left): ").upper().strip()
            
            valid_guess = False
            for pw in self.placed_words:
                if pw['word'] == guess:
                    valid_guess = True
                    break
            
            if not valid_guess:
                print("ERROR: Word not in memory dump.")
                continue
                
            likeness = self.get_likeness(guess)
            print(f"> {guess} : LIKENESS={likeness}/{self.word_len}")
            
            if guess == self.password:
                self.won = True
                print("\n!! LOGIN SUCCESS - ACCESS GRANTED !!")
            else:
                self.attempts -= 1
                if self.attempts <= 0:
                    self.locked_out = True
                    print("\n!! TERMINAL LOCKED - CONTACT ADMIN !!")

if __name__ == "__main__":
    game = TextHackingGame()
    game.play()
