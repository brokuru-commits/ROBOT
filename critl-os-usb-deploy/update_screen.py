#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import math
import pygame
from typing import Optional, Callable

class UpdateScreen:
    """Update installation screen for CRITL OS"""
    
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
        self.RED = (255, 50, 50)
        
        # Load fonts
        self._load_fonts()
        
        # Animation state
        self.hex_scroll_offset = 0
        
    def _load_fonts(self):
        """Load fonts for update screen"""
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
    
    def _draw_progress_bar(self, x: int, y: int, width: int, progress: float, 
                          label: str = "", color=None):
        """Draw retro-style progress bar"""
        if color is None:
            color = self.GREEN
            
        height = 25
        
        # Border
        pygame.draw.rect(self.screen, color, (x, y, width, height), 2)
        
        # Fill
        fill_width = int((width - 4) * progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.DIM_GREEN, (x + 2, y + 2, fill_width, height - 4))
            
            # Animated fill pattern
            for i in range(0, fill_width, 10):
                if (i // 10) % 2 == 0:
                    pygame.draw.rect(self.screen, color, (x + 2 + i, y + 2, 8, height - 4))
        
        # Label
        if label:
            label_surf = self.font_tiny.render(label, True, self.GREEN_SOFT)
            self.screen.blit(label_surf, (x, y - 20))
        
        # Percentage
        percent_text = f"{int(progress * 100)}%"
        percent_surf = self.font_small.render(percent_text, True, color)
        self.screen.blit(percent_surf, (x + width + 10, y + 3))
    
    def _draw_hex_dump(self, x: int, y: int, width: int, height: int):
        """Draw scrolling hex dump animation"""
        # Generate fake hex data
        lines = []
        for i in range(20):
            offset = (i + self.hex_scroll_offset) * 16
            hex_values = " ".join([f"{random.randint(0, 255):02X}" for _ in range(16)])
            line = f"0x{offset:04X}  {hex_values}"
            lines.append(line)
        
        # Draw lines
        line_height = 18
        for i, line in enumerate(lines):
            y_pos = y + (i * line_height) - (self.hex_scroll_offset % 1) * line_height
            
            if y_pos < y or y_pos > y + height:
                continue
            
            text = self.font_tiny.render(line, True, self.DIM_GREEN)
            self.screen.blit(text, (x, int(y_pos)))
        
        # Increment scroll
        self.hex_scroll_offset += 0.3
    
    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} TB"
    
    def run_download_phase(self, update_info: dict, 
                          download_callback: Optional[Callable] = None) -> bool:
        """
        Run download phase with progress animation
        Returns True if successful, False if interrupted
        """
        clock = pygame.time.Clock()
        
        # Simulate download
        total_size = 1024 * 1024 * 5  # 5 MB
        downloaded = 0
        chunk_size = 1024 * 150  # 150 KB per frame
        
        start_time = time.time()
        
        while downloaded < total_size:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False
            
            self.screen.fill(self.BLACK)
            
            # Header
            header = self.font_medium.render("UPDATE DOWNLOAD", True, self.AMBER)
            self.screen.blit(header, (30, 30))
            pygame.draw.line(self.screen, self.AMBER, (30, 60), (300, 60), 2)
            
            # Update info
            y_pos = 80
            version_text = f"Version: {update_info.get('version', 'N/A')}"
            name_text = f"Name: {update_info.get('name', 'Update')}"
            
            self.screen.blit(self.font_small.render(version_text, True, self.GREEN), (40, y_pos))
            self.screen.blit(self.font_small.render(name_text, True, self.GREEN), (40, y_pos + 25))
            
            # Download stats
            y_pos = 150
            elapsed = time.time() - start_time
            speed = downloaded / elapsed if elapsed > 0 else 0
            
            stats = [
                f"Heruntergeladen: {self._format_bytes(downloaded)} / {self._format_bytes(total_size)}",
                f"Geschwindigkeit: {self._format_bytes(int(speed))}/s",
                f"Verstrichene Zeit: {int(elapsed)}s"
            ]
            
            for stat in stats:
                text = self.font_tiny.render(stat, True, self.GREEN_SOFT)
                self.screen.blit(text, (40, y_pos))
                y_pos += 20
            
            # Progress bar
            progress = downloaded / total_size
            self._draw_progress_bar(40, 250, 560, progress, "DOWNLOAD FORTSCHRITT", self.AMBER)
            
            # Hex dump animation
            pygame.draw.rect(self.screen, self.DIM_GREEN, (40, 300, 560, 140))
            pygame.draw.rect(self.screen, self.GREEN, (40, 300, 560, 140), 1)
            self._draw_hex_dump(45, 305, 550, 130)
            
            self._draw_scanlines()
            pygame.display.flip()
            
            # Increment download
            downloaded += chunk_size
            if downloaded > total_size:
                downloaded = total_size
            
            # Call callback if provided
            if download_callback:
                download_callback(progress, downloaded, total_size)
            
            clock.tick(30)
        
        # Download complete message
        time.sleep(0.5)
        return True
    
    def run_installation_phase(self, update_info: dict,
                               install_callback: Optional[Callable] = None) -> bool:
        """
        Run installation phase with file-by-file animation
        Returns True if successful, False if interrupted
        """
        clock = pygame.time.Clock()
        
        # Get files to install
        files = update_info.get('files', [
            'main.py',
            'critl_personality.py',
            'hacking_game.py',
            'update_system.py',
            'boot_screen.py',
            'assets/emotions.txt',
            'assets/art.txt',
            'assets/boot_messages.txt'
        ])
        
        for i, file in enumerate(files):
            file_progress = 0.0
            
            while file_progress < 1.0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return False
                
                self.screen.fill(self.BLACK)
                
                # Header
                header = self.font_medium.render("UPDATE INSTALLATION", True, self.GREEN)
                self.screen.blit(header, (30, 30))
                pygame.draw.line(self.screen, self.GREEN, (30, 60), (320, 60), 2)
                
                # Overall progress
                overall_progress = (i + file_progress) / len(files)
                y_pos = 80
                
                overall_text = f"Gesamtfortschritt: {i + 1} / {len(files)} Dateien"
                self.screen.blit(self.font_small.render(overall_text, True, self.GREEN_SOFT), (40, y_pos))
                self._draw_progress_bar(40, y_pos + 30, 560, overall_progress, "GESAMT")
                
                # Current file
                y_pos = 170
                current_text = f"Installiere: {file}"
                self.screen.blit(self.font_small.render(current_text, True, self.GREEN), (40, y_pos))
                self._draw_progress_bar(40, y_pos + 30, 560, file_progress, "DATEI")
                
                # File list
                y_pos = 260
                list_header = self.font_tiny.render("DATEIEN:", True, self.GREEN_SOFT)
                self.screen.blit(list_header, (40, y_pos))
                
                y_pos += 25
                for j, f in enumerate(files[:8]):  # Show max 8 files
                    if j < i:
                        status = "[OK]"
                        color = self.GREEN
                    elif j == i:
                        status = "[>>]"
                        color = self.GREEN_SOFT
                    else:
                        status = "[ ]"
                        color = self.DIM_GREEN
                    
                    file_text = f"{status} {f}"
                    text = self.font_tiny.render(file_text, True, color)
                    self.screen.blit(text, (50, y_pos))
                    y_pos += 18
                
                self._draw_scanlines()
                pygame.display.flip()
                
                # Increment file progress
                file_progress += random.uniform(0.1, 0.25)
                if file_progress > 1.0:
                    file_progress = 1.0
                
                # Call callback if provided
                if install_callback:
                    install_callback(overall_progress, file)
                
                clock.tick(30)
        
        time.sleep(0.3)
        return True
    
    def show_success_screen(self, new_version: str) -> bool:
        """Show installation success screen"""
        clock = pygame.time.Clock()
        start_time = time.time()
        duration = 3.0
        
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    return True  # Skip on any key
            
            self.screen.fill(self.BLACK)
            
            # Success message
            success_text = "UPDATE ERFOLGREICH"
            success = self.font_large.render(success_text, True, self.GREEN)
            x = (self.width - success.get_width()) // 2
            y = 150
            self.screen.blit(success, (x, y))
            
            # Version info
            version_text = f"CRITL OS v{new_version}"
            version = self.font_medium.render(version_text, True, self.GREEN_SOFT)
            self.screen.blit(version, ((self.width - version.get_width()) // 2, y + 60))
            
            # Reboot message
            reboot_text = "System wird neu gestartet..."
            reboot = self.font_small.render(reboot_text, True, self.GREEN)
            self.screen.blit(reboot, ((self.width - reboot.get_width()) // 2, y + 120))
            
            # Blinking cursor
            self._draw_blinking_cursor((self.width - reboot.get_width()) // 2, y + 150)
            
            self._draw_border()
            self._draw_scanlines()
            pygame.display.flip()
            clock.tick(30)
        
        return True
    
    def show_error_screen(self, error_message: str) -> bool:
        """Show installation error screen"""
        clock = pygame.time.Clock()
        start_time = time.time()
        duration = 5.0
        
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    return True  # Skip on any key
            
            self.screen.fill(self.BLACK)
            
            # Error header
            error_header = "UPDATE FEHLER"
            header = self.font_large.render(error_header, True, self.RED)
            x = (self.width - header.get_width()) // 2
            y = 150
            self.screen.blit(header, (x, y))
            
            # Error message
            error = self.font_small.render(error_message, True, self.RED)
            self.screen.blit(error, ((self.width - error.get_width()) // 2, y + 60))
            
            # Continue message
            continue_text = "Drücke eine Taste zum Fortfahren..."
            cont = self.font_tiny.render(continue_text, True, self.GREEN)
            self.screen.blit(cont, ((self.width - cont.get_width()) // 2, y + 120))
            
            # Blinking cursor
            self._draw_blinking_cursor((self.width - cont.get_width()) // 2, y + 145)
            
            # Draw border with red tint
            pygame.draw.rect(self.screen, self.RED, (10, 10, self.width-20, self.height-20), 2)
            
            self._draw_scanlines()
            pygame.display.flip()
            clock.tick(30)
        
        return True
    
    def run_full_update(self, update_info: dict) -> bool:
        """
        Run complete update process (download + install + success)
        Returns True if successful, False if interrupted
        """
        # Download phase
        if not self.run_download_phase(update_info):
            return False
        
        # Installation phase
        if not self.run_installation_phase(update_info):
            return False
        
        # Success screen
        new_version = update_info.get('version', '2.2.0')
        if not self.show_success_screen(new_version):
            return False
        
        return True


if __name__ == "__main__":
    # Test update screen
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("CRITL OS Update")
    
    update_screen = UpdateScreen(screen)
    
    # Simulate update info
    update_info = {
        'version': '2.2.0',
        'name': 'CRITL OS v2.2.0 - Quantum Update',
        'files': [
            'main.py',
            'critl_personality.py',
            'hacking_game.py',
            'update_system.py',
            'boot_screen.py'
        ]
    }
    
    if update_screen.run_full_update(update_info):
        print("Update completed successfully")
    else:
        print("Update interrupted")
    
    pygame.quit()
