
## Industrial / Restricted Devices (No Play Store)

If you are using a "Package Scanner" or robust Android device that does not have the Google Play Store, **Pydroid 3** might be difficult to set up because its plugins require Play Store license verification.

**The Recommended Solution:** Use **Termux**.

**Termux** is a free, open-source terminal emulator that works great on restricted devices and does not rely on Play Services.

### 1. Install Termux & API
Download the following two APKs from **F-Droid** (a trustworthy open-source app store) or their GitHub releases, and side-load (install) them on your scanner:
1.  **Termux** (The terminal app).
2.  **Termux:API** (The bridge to hardware).

### 2. Setup Termux
Open the **Termux** app and type these commands:
```bash
pkg update
pkg install python
pkg install termux-api
```

### 3. Run the Script
Move `geo_renamer.py` to your device (e.g. Downloads), then in Termux:
```bash
termux-setup-storage  # Allow file access
cd /sdcard/Download/geotag-script-main
python geo_renamer.py /sdcard/Documents/TargetFolder
```

The script has been updated to **automatically detect** if it is running in Termux and use `termux-location` if the Pydroid libraries are missing.
