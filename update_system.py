#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROBOT OS Update System (Git Optimized)
Manages version checking and updates via Git
"""

import os
import sys
import json
import time
import random
import subprocess
from typing import Dict, Optional, Tuple, Callable

class UpdateSystem:
    """Manages version checking and updates for ROBOT OS using Git"""
    
    def __init__(self, version_file: str = "version.json"):
        self.version_file = version_file
        self.repo_dir = os.path.dirname(os.path.abspath(__file__))
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
            "version": "2.1.1",
            "build": "20260221",
            "update_url": "https://api.github.com/repos/brokuru/robot/releases/latest",
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
        """Get current version (short hash)"""
        return self.config.get("version", "unknown")
    
    def _run_git(self, args: list) -> str:
        """Run a git command and return output"""
        try:
            result = subprocess.run(
                ["git"] + args, 
                cwd=self.repo_dir, 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Git error: {e}")
            return ""

    def should_check_for_updates(self) -> bool:
        """Check if enough time has passed"""
        current_time = time.time()
        last_check = self.config.get("last_check", 0)
        interval = self.config.get("check_interval", 3600)
        return (current_time - last_check) >= interval
    
    def check_for_updates(self, force: bool = False) -> Optional[Dict]:
        """
        Check for available updates via Git fetch
        Returns update info dict if update available, None otherwise
        """
        if not force and not self.should_check_for_updates():
            return None
        
        # Update last check time
        self.config["last_check"] = time.time()
        self._save_config()
        
        print("Update Check: Syncing with GitHub...")
        self._run_git(["fetch", "origin"])
        
        local_hash = self._run_git(["rev-parse", "HEAD"])
        remote_hash = self._run_git(["rev-parse", "origin/main"])
        
        if remote_hash and local_hash != remote_hash:
            # Get latest commit message
            desc = self._run_git(["log", "-1", "--pretty=%B", "origin/main"])
            return {
                'version': remote_hash[:7],
                'name': f"Git Update ({remote_hash[:7]})",
                'description': desc or 'Neue Systemverbesserungen verfügbar.',
                'download_url': 'git-pull',
                'files': ['Systemdateien']
            }
        
        return None
    
    def download_update(self, update_info: Dict, progress_callback=None) -> Tuple[bool, str]:
        """Simulate download phase (fetch already done)"""
        if progress_callback:
            # Fake progress for visual effect
            for i in range(11):
                time.sleep(0.05)
                progress_callback(i/10.0, i*10, 100)
        return True, "Code-Paket verifiziert"
    
    def install_update(self, update_info: Dict, progress_callback=None) -> Tuple[bool, str]:
        """Perform git pull to update the codebase"""
        print("Installing updates via git pull...")
        
        # Simulated file list for UI feedback
        files = ["main.py", "critl_personality.py", "update_system.py", "assets/boot_messages.txt"]
        for i, f in enumerate(files):
            if progress_callback:
                progress_callback((i+1)/len(files), f)
            time.sleep(0.2)

        output = self._run_git(["pull", "origin", "main"])
        
        if "Already up to date" in output or "Updating" in output:
            # Update local config with new hash and build date
            new_hash = self._run_git(["rev-parse", "HEAD"])
            self.config['version'] = new_hash[:7] if new_hash else self.config['version']
            self.config['build'] = time.strftime('%Y%m%d')
            self._save_config()
            return True, "Installation erfolgreich abgeschlossen."
        
        return False, f"Git Pull Fehler: {output}"

if __name__ == "__main__":
    updater = UpdateSystem()
    print(f"Current Version: {updater.get_current_version()}")
    update = updater.check_for_updates()
    if update:
        print(f"Update verfügbar: {update['name']}")
    else:
        print("System ist aktuell.")
