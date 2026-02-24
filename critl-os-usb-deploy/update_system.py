#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRITL OS Update System
Manages version checking, downloading, and installing updates
"""

import os
import sys
import json
import time
import random
import socket
from typing import Dict, Optional, Tuple, Callable
import urllib.request
import urllib.error
from urllib import request, error

class UpdateSystem:
    """Manages version checking and updates for CRITL OS"""
    
    def __init__(self, version_file: str = "version.json"):
        self.version_file = version_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load version configuration"""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading version config: {e}")
        
        # Default config
        return {
            "version": "2.1.0",
            "build": "20260213",
            "update_url": "",
            "check_interval": 3600,
            "last_check": 0
        }
    
    def _save_config(self):
        """Save version configuration"""
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving version config: {e}")
    
    def get_current_version(self) -> str:
        """Get current version string"""
        return self.config.get("version", "0.0.0")
    
    def get_build_number(self) -> str:
        """Get current build number"""
        return self.config.get("build", "00000000")
    
    def should_check_for_updates(self) -> bool:
        """Check if enough time has passed since last update check"""
        current_time = time.time()
        last_check = self.config.get("last_check", 0)
        interval = self.config.get("check_interval", 3600)
        
        return (current_time - last_check) >= interval
    
    def check_for_updates(self) -> Optional[Dict]:
        """
        Check for available updates
        Returns update info dict if update available, None otherwise
        """
        if not self.should_check_for_updates():
            return None
        
        # Update last check time
        self.config["last_check"] = time.time()
        self._save_config()
        
        update_url = self.config.get("update_url", "")
        if not update_url:
            return None
        
        try:
            # Try to fetch latest release info from GitHub API
            req = urllib.request.Request(update_url)
            req.add_header('User-Agent', 'CRITL-OS-Updater/2.1')
            
            # Faster timeout for initial connection
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Parse version from tag_name (e.g., "v2.2.0" -> "2.2.0")
                latest_version = data.get('tag_name', '').lstrip('v')
                
                if self._is_newer_version(latest_version):
                    return {
                        'version': latest_version,
                        'name': data.get('name', 'Update'),
                        'description': data.get('body', 'Neue Version verfügbar'),
                        'download_url': data.get('zipball_url', ''),
                        'published_at': data.get('published_at', '')
                    }
        
        except (urllib.error.URLError, socket.timeout, socket.error) as e:
            print(f"Network error checking for updates (Offline mode?): {e}")
        except Exception as e:
            print(f"Error checking for updates: {e}")
        
        return None
    
    def _is_newer_version(self, new_version: str) -> bool:
        """Compare version strings (simple numeric comparison)"""
        try:
            current = tuple(map(int, self.get_current_version().split('.')))
            new = tuple(map(int, new_version.split('.')))
            return new > current
        except:
            return False
    
    def simulate_update_check(self, has_update: bool = False) -> Optional[Dict]:
        """
        Simulate an update check for testing
        Returns fake update info if has_update is True
        """
        self.config["last_check"] = time.time()
        self._save_config()
        
        if has_update:
            return {
                'version': '2.2.0',
                'name': 'CRITL OS v2.2.0 - Quantum Update',
                'description': 'Neue Features:\n- Verbesserte KI\n- Mehr Stories\n- Bug Fixes',
                'download_url': 'https://example.com/update.zip',
                'published_at': '2026-02-13T08:00:00Z',
                'files': [
                    'main.py',
                    'critl_personality.py',
                    'hacking_game.py',
                    'assets/emotions.txt',
                    'assets/stories/new_story.txt'
                ]
            }
        
        return None
    
    def download_update(self, update_info: Dict, progress_callback=None) -> Tuple[bool, str]:
        """
        Download update package
        Returns (success, message)
        """
        # For now, this is a simulation
        # In a real implementation, this would download and verify the update
        
        if progress_callback:
            # Simulate download progress
            total_size = 1024 * 1024 * 5  # 5 MB
            downloaded = 0
            chunk_size = 1024 * 100  # 100 KB chunks
            
            while downloaded < total_size:
                time.sleep(0.1)  # Simulate download time
                downloaded += chunk_size
                if downloaded > total_size:
                    downloaded = total_size
                
                progress = downloaded / total_size
                progress_callback(progress, downloaded, total_size)
        
        return True, "Download erfolgreich"
    
    def install_update(self, update_info: Dict, progress_callback=None) -> Tuple[bool, str]:
        """
        Install downloaded update
        Returns (success, message)
        """
        # Simulation of installation process
        files = update_info.get('files', [])
        
        for i, file in enumerate(files):
            if progress_callback:
                progress = (i + 1) / len(files)
                progress_callback(progress, file)
            
            time.sleep(0.3)  # Simulate installation time
        
        # Update version info
        new_version = update_info.get('version', self.get_current_version())
        self.config['version'] = new_version
        self.config['build'] = time.strftime('%Y%m%d')
        self._save_config()
        
        return True, f"Update auf v{new_version} erfolgreich"


if __name__ == "__main__":
    # Test the update system
    updater = UpdateSystem()
    print(f"Current Version: {updater.get_current_version()}")
    print(f"Build: {updater.get_build_number()}")
    
    # Simulate update check
    update = updater.simulate_update_check(has_update=True)
    if update:
        print(f"\nUpdate verfügbar: {update['name']}")
        print(f"Version: {update['version']}")
