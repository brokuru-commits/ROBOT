import pygame
import time
import os
import sys

# Add current dir to path to import main
sys.path.append(os.getcwd())

import main
from critl_personality import CRITLPersonality

def capture_localized_rpg():
    pygame.init()
    # Mock some data
    main.critl = CRITLPersonality()
    main.critl.skills["hacking"] = 42
    main.critl.skills["lore"] = 15
    main.critl.skills["bonding"] = 88
    main.critl.inventory = ["Krypto-Fragment", "SD-Karte", "Erdnussflip"]
    main.show_rpg = True
    
    # Draw
    main.screen.fill((0, 0, 0))
    main.draw_rpg_overlay()
    
    # Save
    path = "/home/martin/.gemini/antigravity/brain/765987d2-00ff-4f1e-bbeb-a8231335e6bd/screenshot_rpg_de_v1.png"
    pygame.image.save(main.screen, path)
    print(f"Saved to {path}")
    pygame.quit()

if __name__ == "__main__":
    capture_localized_rpg()
