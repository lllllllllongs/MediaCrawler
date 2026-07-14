# -*- coding: utf-8 -*-
"""Apply CCTV platform patches to MediaCrawler.
Run this script from the project root to apply all modifications.
Usage: python _apply_patches.py
"""
import json
import os
import shutil
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PATCH_FILE = os.path.join(BASE, "_apply_patches.json")

def main():
    if not os.path.exists(PATCH_FILE):
        print(f"ERROR: Patch file not found: {PATCH_FILE}")
        print("Make sure _apply_patches.json is in the same directory.")
        return

    with open(PATCH_FILE, "r", encoding="utf-8") as f:
        patches = json.load(f)

    # Create backup directory for existing files
    backup_dir = os.path.join(BASE, f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    for filepath, new_content in patches.items():
        rel_path = os.path.relpath(filepath, BASE)
        target_dir = os.path.dirname(filepath)

        # Ensure target directory exists
        os.makedirs(target_dir, exist_ok=True)

        if os.path.exists(filepath):
            # Backup existing file
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, rel_path)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(filepath, backup_path)
            print(f"Backed up: {rel_path}")

        # Write patched/new content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        status = "Patched" if os.path.exists(os.path.join(backup_dir, rel_path)) else "Created"
        print(f"{status}: {rel_path}")

    print(f"\nAll {len(patches)} files applied successfully!")
    if os.path.exists(backup_dir):
        print(f"Backups saved to: {backup_dir}")
        print(f"To revert, copy files from backup directory back to original locations.")
    print("\nYou can now start the WebUI: .\start-webui.ps1")

if __name__ == "__main__":
    main()
