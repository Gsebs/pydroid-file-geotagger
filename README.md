# Android File Geotagger

This tool allows you to automatically append the current GPS coordinates of your Android device to all files in a specific directory. It is designed to run within **Pydroid 3**.

## Features
- **Accurate Geotagging**: Captures Latitude and Longitude using the device's GPS.
- **Safe naming**: Converts coordinates to a filename-safe format (e.g., `_Lat_34.123_Lng_-118.987`).
- **Safety First**:
    - Includes a `--dry-run` mode to preview changes.
    - Skips files that are already geotagged.
    - Fails gracefully if GPS is unavailable.

## Prerequisites
1.  **Pydroid 3** app installed on your Android device.
2.  **Pydroid Repository Plugin** (usually needed to install libraries, though `androidhelper` is built-in or easily added).
3.  **Permissions**: Pydroid 3 must have **Location** and **Storage** permissions allowed in Android Settings.

## Installation
1.  Save the `geo_renamer.py` script to your device (e.g., in `/storage/emulated/0/Documents/Scripts/`).

## Usage

Open Pydroid 3, go to **Terminal**, and navigate to where you saved the script.

### Basic Usage
To geotag all files in a folder:

```bash
python geo_renamer.py /storage/emulated/0/Documents/MyPhotos
```

### Dry Run (Test Mode)
To see what *would* happen without actually changing any filenames:

```bash
python geo_renamer.py /storage/emulated/0/Documents/MyPhotos --dry-run
```

### Adjust Timeout
If getting a GPS lock takes too long (default 30s), increase the timeout:

```bash
python geo_renamer.py /storage/emulated/0/Documents/MyPhotos --timeout 60
```

## Troubleshooting
*   **"Android module not found"**: Ensure you are running this inside Pydroid 3.
*   **"Timed out"**: Make sure your Location/GPS is turned ON in Android settings. Move outdoors for a better signal.
*   **Permission Denied**: Check Android Settings -> Apps -> Pydroid 3 -> Permissions. Enable **Files and Media** (or Storage) and **Location**.
