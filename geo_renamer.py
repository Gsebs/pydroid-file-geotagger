#!/usr/bin/env python3
"""
geo_renamer.py
--------------
A robust tool to geotag files on Android devices using Pydroid 3.
This script retrieves the current GPS coordinates and appends them to filenames
in a specified directory.

Features:
- Robust GPS acquisition with timeout and fallback.
- Safety checks: Dry-run mode, collision detection, and tag skipping.
- Efficient directory traversal.
- Detailed logging and user feedback.

Usage:
    python geo_renamer.py <directory_path> [--dry-run] [--timeout SECONDS]
"""

import os
import sys
import time
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Attempt to import Android SL4A Library
SERVER_AVAILABLE = False
droid_module = None

try:
    import android
    if hasattr(android, 'Android'):
        droid_module = android
        SERVER_AVAILABLE = True
except ImportError:
    pass

if not SERVER_AVAILABLE:
    try:
        import androidhelper
        droid_module = androidhelper
        SERVER_AVAILABLE = True
    except ImportError:
        pass

if not SERVER_AVAILABLE:
    logger.warning("Android module (SL4A) not found. GPS functionality will be simulated or unavailable.")

class GeoTagger:
    def __init__(self, directory, timeout=60, dry_run=False):
        self.directory = directory
        self.timeout = timeout
        self.dry_run = dry_run
        self.droid = None
        
        if SERVER_AVAILABLE and droid_module:
            try:
                self.droid = droid_module.Android()
            except Exception as e:
                logger.error(f"Failed to initialize Android object: {e}")
                sys.exit(1)

    def get_location(self):
        """
        Acquires available location (Latitude, Longitude).
        Tries Android/SL4A first, then Termux, then Mock if testing.
        """
        # 1. Try SL4A (Pydroid 3)
        if self.droid:
            logger.info("Starting SL4A location service...")
            self.droid.startLocating()
            
            logger.info(f"Waiting up to {self.timeout} seconds for a fix...")
            start_time = time.time()
            
            try:
                while time.time() - start_time < self.timeout:
                    reading = self.droid.readLocation().result
                    if reading:
                        if 'gps' in reading:
                            lat = reading['gps']['latitude']
                            lng = reading['gps']['longitude']
                            self.droid.stopLocating()
                            return f"_Lat_{lat:.5f}_Lng_{lng:.5f}"
                        elif 'network' in reading:
                            # Keep network as fallback but prefer wait for GPS?
                            # For now return immediately if found
                            lat = reading['network']['latitude']
                            lng = reading['network']['longitude']
                            self.droid.stopLocating()
                            return f"_Lat_{lat:.5f}_Lng_{lng:.5f}"
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Error during SL4A location read: {e}")
            finally:
                self.droid.stopLocating()

        # 2. Try Termux (subprocess) if SL4A failed or is missing
        termux_loc = self.get_termux_location()
        if termux_loc:
            return termux_loc

        logger.error("Timed out. Could not retrieve location. Ensure GPS is ON.")
        return None

    def get_termux_location(self):
        """
        Attempts to get location via `termux-location` command.
        """
        import shutil
        import subprocess
        import json

        if not shutil.which("termux-location"):
            return None

        logger.info("SL4A failed/missing. Trying 'termux-location'...")
        try:
            # First, check 'last' known location for speed
            cmd_last = ["termux-location", "-p", "gps", "-r", "last"]
            proc = subprocess.run(cmd_last, capture_output=True, text=True, timeout=3)
            if proc.returncode == 0 and proc.stdout.strip():
                data = json.loads(proc.stdout)
                lat = data.get("latitude")
                lng = data.get("longitude")
                # Ensure data is not too old? For now assume OK.
                if lat and lng:
                    return f"_Lat_{lat:.5f}_Lng_{lng:.5f}"
            
            # If last failed, try a fresh request (blocking)
            # This is critical if the GPS hasn't been used recently
            logger.info("No cached location. Requesting fresh GPS update (this may take 10-20s)...")
            cmd_fresh = ["termux-location", "-p", "gps", "-r", "once"]
            proc = subprocess.run(cmd_fresh, capture_output=True, text=True, timeout=25)
            
            if proc.returncode == 0 and proc.stdout.strip():
                data = json.loads(proc.stdout)
                lat = data.get("latitude")
                lng = data.get("longitude")
                if lat and lng:
                    return f"_Lat_{lat:.5f}_Lng_{lng:.5f}"
            
        except subprocess.TimeoutExpired:
            logger.error("Termux location request timed out.")
        except Exception as e:
            logger.warning(f"Termux location attempt failed: {e}")
        
        return None

    def process_directory(self):
        """
        Main logic to rename files.
        """
        # 1. Validation
        if not os.path.isdir(self.directory):
            logger.error(f"Directory not found: {self.directory}")
            return

        # 2. Get Location
        logger.info("Acquiring GPS lock. Please wait...")
        gps_suffix = self.get_location()

        # For debug on PC without Pydroid, uncomment to test renaming logic:
        # gps_suffix = "_Lat_37.77490_Lng_-122.41940" 

        if not gps_suffix:
            logger.critical("No GPS data. Aborting operation to prevent data loss.")
            sys.exit(1)

        logger.info(f"Location Tag: {gps_suffix}")
        
        if self.dry_run:
            logger.warning("--- DRY RUN MODE: No files will be modified ---")

        # 3. Rename Files
        count = 0
        skipped = 0
        errors = 0
        
        # os.scandir is more efficient for large directories
        try:
            with os.scandir(self.directory) as it:
                for entry in it:
                    if not entry.is_file():
                        continue
                    
                    filename = entry.name
                    
                    # Avoid renaming hidden files if desired (e.g. .DS_Store)
                    if filename.startswith('.'):
                        continue

                    name_body, ext = os.path.splitext(filename)

                    # Safety: Check if already tagged to prevent double tagging
                    # Detect pattern: _Lat_..._Lng_...
                    if "_Lat_" in name_body and "_Lng_" in name_body:
                        # logger.debug(f"Skipping {filename}: Already looks tagged.")
                        skipped += 1
                        continue

                    new_filename = f"{name_body}{gps_suffix}{ext}"
                    old_path = entry.path
                    new_path = os.path.join(self.directory, new_filename)

                    # Check collision
                    if os.path.exists(new_path):
                        logger.warning(f"Skipping {filename}: Target {new_filename} already exists.")
                        skipped += 1
                        continue

                    # Perform Rename
                    if not self.dry_run:
                        try:
                            os.rename(old_path, new_path)
                            logger.info(f"Renamed: {filename} -> {new_filename}")
                            count += 1
                        except OSError as e:
                            logger.error(f"Failed to rename {filename}: {e}")
                            errors += 1
                    else:
                        logger.info(f"[Dry-Run] Would rename: {filename} -> {new_filename}")
                        count += 1

        except OSError as e:
            logger.error(f"Error accessing directory: {e}")

        # Summary
        logger.info("-" * 40)
        logger.info(f"Processing Complete.")
        if self.dry_run:
            logger.info(f"Would Rename: {count}")
        else:
            logger.info(f"Renamed: {count}")
        
        logger.info(f"Skipped: {skipped}")
        if errors > 0:
            logger.info(f"Errors: {errors}")

def main():
    parser = argparse.ArgumentParser(description="Geotag files in a directory using Android GPS.")
    parser.add_argument("directory", help="Path to the directory containing files to tag.")
    parser.add_argument("--timeout", type=int, default=30, help="Seconds to wait for GPS fix (default: 30).")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the process without renaming files.")
    
    args = parser.parse_args()
    
    # Expand user path (e.g. ~/Documents)
    target_dir = os.path.expanduser(args.directory)
    
    # Create the tagger and run
    tagger = GeoTagger(target_dir, timeout=args.timeout, dry_run=args.dry_run)
    tagger.process_directory()

if __name__ == "__main__":
    main()
