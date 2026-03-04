#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import pygame
from typing import List, Tuple

class BootScreen:
    """Retro terminal boot screen for CRITL OS"""
    
    def __init__(self, screen, width=640, height=480):
        self.screen = screen
        self.width = width
        self.height = height
        
        # Colors (Fallout green terminal)
        self.GREEN = (55, 200, 55)
        self.GREEN_SOFT = (100, 230, 100)
        self.DIM_GREEN = (10, 40, 10)
        self.BLACK = (0, 0, 0)
        self.AMBER = (255, 180, 0)
        
        # Load fonts
        self._load_fonts()
        
        # Load boot messages
        self.messages = self._load_boot_messages()
        
        # Boot sequence state
        self.boot_complete = False
        self.current_step = 0
        
    def _load_fonts(self):
        """Load fonts for boot screen"""
        font_path = os.path.join("assets", "Monofonto.ttf")
        
        try:
            self.font_large = pygame.font.Font(font_path, 36)
            self.font_medium = pygame.font.Font(font_path, 24)
            self.font_small = pygame.font.Font(font_path, 18)
            self.font_tiny = pygame.font.Font(font_path, 14)
        except:
            # Fallback to system monospace
            self.font_large = pygame.font.SysFont("monospace", 36)
            self.font_medium = pygame.font.SysFont("monospace", 24)
            self.font_small = pygame.font.SysFont("monospace", 18)
            self.font_tiny = pygame.font.SysFont("monospace", 14)
    
    def _load_boot_messages(self) -> dict:
        """Load boot messages from file"""
        messages = {
            'header': ['ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM', 'ROBOT OS VERSION 2.1.0'],
            'check': ['Initialisiere System...', 'Lade Module...', 'Prüfe Integrität...'],
            'success': ['OK', 'BEREIT', 'GELADEN'],
            'component': ['ROBOT CORE', 'PERSONALITY MODULE', 'TAMAGOTCHI ENGINE']
        }
        
        boot_file = os.path.join("assets", "boot_messages.txt")
        if os.path.exists(boot_file):
            try:
                temp_messages = {'header': [], 'check': [], 'success': [], 'component': []}
                with open(boot_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        if ':' in line:
                            category, message = line.split(':', 1)
                            category = category.strip()
                            message = message.strip()
                            
                            if category in temp_messages:
                                temp_messages[category].append(message)
                
                # Only use loaded messages if we got some
                for key in temp_messages:
                    if temp_messages[key]:
                        messages[key] = temp_messages[key]
            except Exception as e:
                print(f"Error loading boot messages: {e}")
        
        return messages
    
    def _draw_scanlines(self):
        """Draw CRT scanline effect"""
        scanline_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, 3):
            pygame.draw.line(scanline_surface, (0, 20, 0, 30), (0, y), (self.width, y), 1)
        self.screen.blit(scanline_surface, (0, 0))
    
    def _draw_border(self):
        """Draw retro terminal border"""
        pygame.draw.rect(self.screen, self.GREEN, (10, 10, self.width-20, self.height-20), 2)
        pygame.draw.rect(self.screen, self.DIM_GREEN, (12, 12, self.width-24, self.height-24), 1)
    
    def _draw_blinking_cursor(self, x: int, y: int, blink_speed: float = 2.0):
        """Draw blinking cursor"""
        if int(time.time() * blink_speed) % 2 == 0:
            cursor = self.font_medium.render("_", True, self.GREEN)
            self.screen.blit(cursor, (x, y))
    
    def _draw_progress_bar(self, x: int, y: int, width: int, progress: float, label: str = ""):
        """Draw retro-style progress bar"""
        height = 20
        
        # Border
        pygame.draw.rect(self.screen, self.GREEN, (x, y, width, height), 2)
        
        # Fill
        fill_width = int((width - 4) * progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.DIM_GREEN, (x + 2, y + 2, fill_width, height - 4))
            
            # Animated fill pattern
            for i in range(0, fill_width, 10):
                if (i // 10) % 2 == 0:
                    pygame.draw.rect(self.screen, self.GREEN, (x + 2 + i, y + 2, 8, height - 4))
        
        # Label
        if label:
            label_surf = self.font_tiny.render(label, True, self.GREEN_SOFT)
            self.screen.blit(label_surf, (x, y - 20))
        
        # Percentage
        percent_text = f"{int(progress * 100)}%"
        percent_surf = self.font_tiny.render(percent_text, True, self.GREEN)
        self.screen.blit(percent_surf, (x + width + 10, y + 2))
    
    def run_boot_sequence(self, update_info=None) -> bool:
        """
        Run the complete boot sequence
        Returns True when boot is complete, False if interrupted
        """
        clock = pygame.time.Clock()
        
        # Phase 1: BIOS Header
        if not self._phase_bios_header(clock):
            return False
        
        # Phase 2: POST (Power-On Self Test)
        if not self._phase_post(clock):
            return False
        
        # Phase 3: Component Loading
        if not self._phase_component_loading(clock):
            return False
        
        # Phase 4: Update Check (if update info provided)
        if update_info:
            if not self._phase_update_check(clock, update_info):
                return False
        
        # Phase 5: Boot Complete
        if not self._phase_boot_complete(clock):
            return False
        
        return True
    
    def _phase_bios_header(self, clock) -> bool:
        """Phase 1: Display BIOS-style header"""
        start_time = time.time()
        duration = 2.0
        
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False
            
            self.screen.fill(self.BLACK)
            
            # Header
            y_pos = 40
            for header in self.messages['header'][:2]:
                text = self.font_medium.render(header, True, self.GREEN)
                self.screen.blit(text, (30, y_pos))
                y_pos += 35
            
            # Copyright
            copyright_text = "COPYRIGHT 2075-2077 ROBCO INDUSTRIES - ROBOT DIVISION"
            copyright = self.font_tiny.render(copyright_text, True, self.DIM_GREEN)
            self.screen.blit(copyright, (30, y_pos + 20))
            
            # Blinking cursor
            self._draw_blinking_cursor(30, y_pos + 60)
            
            self._draw_scanlines()
            pygame.display.flip()
            clock.tick(30)
        
        return True
    
    def _phase_post(self, clock) -> bool:
        """Phase 2: Power-On Self Test"""
        checks = [
            ("CPU", "Intel Quantum Core i9-9900K", 0.3),
            ("RAM", "32768 MB OK", 0.4),
            ("STORAGE", "SSD 512 GB", 0.3),
            ("GRAPHICS", "Pip-Boy Display Adapter", 0.4),
            ("AUDIO", "RobCo Sound System", 0.3),
        ]
        
        y_pos = 150
        
        for check_name, check_result, delay in checks:
            start_time = time.time()
            
            while time.time() - start_time < delay:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return False
                
                self.screen.fill(self.BLACK)
                
                # Redraw header
                header = self.font_small.render("SYSTEM POST", True, self.GREEN_SOFT)
                self.screen.blit(header, (30, 30))
                pygame.draw.line(self.screen, self.GREEN, (30, 55), (250, 55), 1)
                
                # Draw completed checks
                temp_y = 80
                for prev_name, prev_result, _ in checks[:checks.index((check_name, check_result, delay))]:
                    name_text = self.font_tiny.render(f"{prev_name}:", True, self.GREEN)
                    result_text = self.font_tiny.render(prev_result, True, self.GREEN_SOFT)
                    ok_text = self.font_tiny.render("[OK]", True, self.GREEN)
                    
                    self.screen.blit(name_text, (50, temp_y))
                    self.screen.blit(result_text, (200, temp_y))
                    self.screen.blit(ok_text, (500, temp_y))
                    temp_y += 25
                
                # Draw current check with blinking cursor
                name_text = self.font_tiny.render(f"{check_name}:", True, self.GREEN)
                self.screen.blit(name_text, (50, temp_y))
                self._draw_blinking_cursor(200, temp_y)
                
                self._draw_scanlines()
                pygame.display.flip()
                clock.tick(30)
            
            # Show result
            for _ in range(10):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                
                self.screen.fill(self.BLACK)
                header = self.font_small.render("SYSTEM POST", True, self.GREEN_SOFT)
                self.screen.blit(header, (30, 30))
                pygame.draw.line(self.screen, self.GREEN, (30, 55), (250, 55), 1)
                
                temp_y = 80
                for prev_name, prev_result, _ in checks[:checks.index((check_name, check_result, delay)) + 1]:
                    name_text = self.font_tiny.render(f"{prev_name}:", True, self.GREEN)
                    result_text = self.font_tiny.render(prev_result, True, self.GREEN_SOFT)
                    ok_text = self.font_tiny.render("[OK]", True, self.GREEN)
                    
                    self.screen.blit(name_text, (50, temp_y))
                    self.screen.blit(result_text, (200, temp_y))
                    self.screen.blit(ok_text, (500, temp_y))
                    temp_y += 25
                
                self._draw_scanlines()
                pygame.display.flip()
                clock.tick(30)
        
        time.sleep(0.5)
        return True
    
    def _phase_component_loading(self, clock) -> bool:
        """Phase 3: Load ROBOT components"""
        components = self.messages['component'][:6]
        
        for i, component in enumerate(components):
            progress = 0.0
            
            while progress < 1.0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return False
                
                self.screen.fill(self.BLACK)
                
                # Header
                header = self.font_small.render("LADE ROBOT KOMPONENTEN", True, self.GREEN_SOFT)
                self.screen.blit(header, (30, 30))
                pygame.draw.line(self.screen, self.GREEN, (30, 55), (350, 55), 1)
                
                # Component list
                y_pos = 80
                for j, comp in enumerate(components):
                    if j < i:
                        # Completed
                        text = self.font_tiny.render(f"[OK] {comp}", True, self.GREEN)
                    elif j == i:
                        # Current
                        text = self.font_tiny.render(f"[>>] {comp}", True, self.GREEN_SOFT)
                    else:
                        # Pending
                        text = self.font_tiny.render(f"[ ] {comp}", True, self.DIM_GREEN)
                    
                    self.screen.blit(text, (50, y_pos))
                    y_pos += 30
                
                # Progress bar for current component
                self._draw_progress_bar(50, y_pos + 20, 500, progress, "FORTSCHRITT")
                
                self._draw_scanlines()
                pygame.display.flip()
                
                # Increment progress (random speed for realism)
                progress += random.uniform(0.05, 0.15)
                if progress > 1.0:
                    progress = 1.0
                
                clock.tick(30)
        
        time.sleep(0.3)
        return True
    
    def _phase_update_check(self, clock, update_info) -> bool:
        """Phase 4: Check for updates"""
        start_time = time.time()
        duration = 2.0
        
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False
            
            self.screen.fill(self.BLACK)
            
            # Header
            header = self.font_small.render("UPDATE CHECK", True, self.AMBER)
            self.screen.blit(header, (30, 30))
            pygame.draw.line(self.screen, self.AMBER, (30, 55), (220, 55), 1)
            
            # Update info
            y_pos = 80
            if update_info:
                lines = [
                    f"Neue Version verfügbar: v{update_info.get('version', 'N/A')}",
                    f"Name: {update_info.get('name', 'Update')}",
                    "",
                    "Update wird später installiert..."
                ]
            else:
                lines = [
                    "Prüfe auf Updates...",
                    "",
                    "Keine Updates verfügbar.",
                    "System ist aktuell."
                ]
            
            for line in lines:
                text = self.font_tiny.render(line, True, self.GREEN)
                self.screen.blit(text, (50, y_pos))
                y_pos += 25
            
            self._draw_blinking_cursor(50, y_pos)
            self._draw_scanlines()
            pygame.display.flip()
            clock.tick(30)
        
        return True
    
    def _phase_boot_complete(self, clock) -> bool:
        """Phase 5: Boot complete message"""
        start_time = time.time()
        duration = 1.5
        
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False
            
            self.screen.fill(self.BLACK)
            
            # Success message
            success_text = "BOOT ERFOLGREICH"
            success = self.font_large.render(success_text, True, self.GREEN)
            x = (self.width - success.get_width()) // 2
            y = (self.height - success.get_height()) // 2
            self.screen.blit(success, (x, y))
            
            # Starting message
            starting = self.font_small.render("Starte ROBOT OS...", True, self.GREEN_SOFT)
            self.screen.blit(starting, (x, y + 60))
            
            self._draw_border()
            self._draw_scanlines()
            pygame.display.flip()
            clock.tick(30)
        
        return True


if __name__ == "__main__":
    # Test boot screen
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("ROBOT OS Boot")
    
    boot = BootScreen(screen)
    
    # Simulate update info
    update_info = {
        'version': '2.2.0',
        'name': 'Quantum Update'
    }
    
    if boot.run_boot_sequence(update_info=None):
        print("Boot sequence completed successfully")
    else:
        print("Boot sequence interrupted")
    
    pygame.quit()
