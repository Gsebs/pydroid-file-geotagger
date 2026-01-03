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
try:
    import android
    SERVER_AVAILABLE = True
except ImportError:
    try:
        import androidhelper as android
        SERVER_AVAILABLE = True
    except ImportError:
        SERVER_AVAILABLE = False
        logger.warning("Android module not found. GPS functionality will be simulated if not on an Android device.")

class GeoTagger:
    def __init__(self, directory, timeout=60, dry_run=False):
        self.directory = directory
        self.timeout = timeout
        self.dry_run = dry_run
        self.droid = None
        
        if SERVER_AVAILABLE:
            try:
                self.droid = android.Android()
            except Exception as e:
                logger.error(f"Failed to initialize Android object: {e}")
                sys.exit(1)

    def get_location(self):
        """
        Acquires the current location (Latitude, Longitude).
        Returns a formatted string suffix: '_Lat_XX.XXXXX_Lng_YY.YYYYY'
        """
        if not self.droid:
            logger.error("Android service not available. Cannot retrieve real GPS data.")
            return None

        logger.info("Starting location service...")
        self.droid.startLocating()
        
        logger.info(f"Waiting up to {self.timeout} seconds for a fix...")
        start_time = time.time()
        location = None
        
        try:
            while time.time() - start_time < self.timeout:
                # readLocation().result returns {'gps': {...}, 'network': {...}}
                reading = self.droid.readLocation().result
                
                if reading:
                    if 'gps' in reading:
                        location = reading['gps']
                        logger.info("GPS provider fix acquired.")
                        break
                    elif 'network' in reading:
                        location = reading['network']
                        # We continue loop briefly to see if GPS comes in, 
                        # but store this as fallback. 
                        # For speed over precision, we can break here if preferred.
                        # Here we will break for network to be responsive.
                        logger.info("Network provider fix acquired.")
                        break
                
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error during location read: {e}")
        finally:
            self.droid.stopLocating()
            logger.info("Location service stopped.")

        if location:
            try:
                lat = location['latitude']
                lng = location['longitude']
                # Create a safe string. 
                # User requested: File.txt -> File[GPS].txt
                # Format: _Lat_34.12345_Lng_-118.12345
                return f"_Lat_{lat:.5f}_Lng_{lng:.5f}"
            except KeyError:
                logger.error("Location data malformed.")
                return None
        else:
            logger.error("Timed out. Could not retrieve location. Ensure GPS is ON.")
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
