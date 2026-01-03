#!/usr/bin/env python3
"""
mac_renamer.py
--------------
A wrapper around geo_renamer.py to allow testing on macOS/Linux.
Since standard computers don't have the 'android' module or (usually) a GPS,
this script simulates the location by looking up your public IP address.

It reuses the EXACT logic from geo_renamer.py for renaming,
ensuring that what you test here is what runs on the phone.
"""

import sys
import json
import logging
import urllib.request
from geo_renamer import GeoTagger, main as original_main

# Configure logging (reuse basic config if possible, or set it up)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MAC-TEST] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class MacGeoTagger(GeoTagger):
    """
    Subclass that overrides ONLY the get_location method.
    """
    def __init__(self, directory, timeout=60, dry_run=False):
        # Initialize parent without checking for Android module availability
        self.directory = directory
        self.timeout = timeout
        self.dry_run = dry_run
        # We don't need self.droid

    def get_location(self):
        """
        Overrides the Android GPS call with an IP-Geolocator.
        """
        logger.info("Simulating GPS fix using IP Geolocation...")
        
        try:
            with urllib.request.urlopen("http://ip-api.com/json/") as url:
                data = json.loads(url.read().decode())
                
            if data['status'] == 'success':
                lat = data['lat']
                lon = data['lon']
                logger.info(f"IP Location found: {data['city']}, {data['country']}")
                return f"_Lat_{lat:.5f}_Lng_{lon:.5f}"
            else:
                logger.error("IP Lookup failed.")
                return None
        except Exception as e:
            logger.error(f"Network error during IP lookup: {e}")
            logger.warning("Falling back to dummy coordinates for testing.")
            # Fallback so user can still test renaming logic offline
            return "_Lat_51.50740_Lng_-0.12780"

# Monkey-patch the class in the original module so if there are other internal references, they work
# (Though here we are just instantiating our subclass directly)

def main():
    # We will basically run the same logic as the original main, 
    # but instantiate MacGeoTagger instead.
    
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="[MAC/TEST] Geotag files using IP location.")
    parser.add_argument("directory", help="Path to the directory containing files to tag.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the process without renaming files.")
    # Timeout is less relevant here but kept for API compatibility
    
    args = parser.parse_args()
    target_dir = os.path.expanduser(args.directory)
    
    # Use our Mac-compatible class
    tagger = MacGeoTagger(target_dir, dry_run=args.dry_run)
    tagger.process_directory()

if __name__ == "__main__":
    main()
