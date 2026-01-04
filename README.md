# Android File Geotagger

This tool allows you to automatically append the current GPS coordinates of your Android device to all files in a specific directory. It is designed to run within **Pydroid 3**.

## Features
- **Accurate Geotagging**: Captures Latitude and Longitude using the device's GPS.
- **Safe naming**: Converts coordinates to a filename-safe format (e.g., `_Lat_34.123_Lng_-118.987`).
- **Safety First**:
    - Includes a `--dry-run` mode to preview changes.
    - Skips files that are already geotagged.
    - Fails gracefully if GPS is unavailable.

---

## How to Run on Android (Step-by-Step)

### Phase 1: Preparation (Do this once)
1.  **Install the "Pydroid Permissions Plugin"**
    *   Go to the Google Play Store.
    *   Search for "Pydroid Permissions Plugin".
    *   Install it. (This is mandatory for accessing the GPS hardware and the File System).

2.  **Configure Pydroid Permissions**
    *   Open the **Pydroid 3** app.
    *   Android will likely ask for permissions immediately. **Allow everything** (especially "Files/Storage" and "Location").
    *   *Double check*: Go to your phone's **Settings > Apps > Pydroid 3 > Permissions**. Ensure **Location** is set to "**Allow only while using the app**" (or "Always allow" if available).

### Phase 2: Get the Code onto the Device
Since typing git commands and handling authentication keys on a mobile touchscreen is often painful, the "Download ZIP" method is usually faster for mobile.

1.  **Download the Repo**
    *   Open Chrome (or any browser) on your Android device.
    *   Go to your GitHub repository URL.
    *   Tap the **Green Code button** -> **Download ZIP**.
    *   Once downloaded, open your "Files" app (e.g., "Google Files" or "My Files").
    *   Find the ZIP in your Downloads folder and **Extract it**. You should now have a folder named `geotag-script-main` (or similar) in your Downloads.

2.  **Create your "Target" Directory**
    *   While you are in your Files app, create a folder where you want to test this.
    *   Let's call it: `Internal Storage > Documents > GPS_Test_Folder`

### Phase 3: Dependencies
*   **Note**: This specific script (`geo_renamer.py`) only uses built-in libraries, so you generally *do not* need to install anything via Pip.
*   However, if you wish to verify your environment:
    1.  Open Pydroid 3.
    2.  Tap the Menu icon (top left, three lines) -> **Pip**.
    3.  You can verify `watchdog` is not needed for this version, but `androidhelper` should clearly work out of the box.

### Phase 4: Run the Script
Now we use the Pydroid Terminal to run the script.

1.  **Open the Terminal**
    *   In Pydroid, tap **Menu > Terminal**.

2.  **Navigate to your Code**
    *   Type the following commands (assuming you extracted the zip to Downloads):
    ```bash
    cd /sdcard/Download/geotag-script-main
    ```
    *   *Tip*: You can type `ls` to list files and make sure `geo_renamer.py` is there.

3.  **Execute the Script**
    *   Run the script and point it to your test folder:
    ```bash
    python geo_renamer.py /sdcard/Documents/GPS_Test_Folder
    ```

---

## How to Run on Chromebook

Chromebooks can run this script using the **Pydroid 3 app** from the Play Store, just like a phone.

1.  **Install Pydroid 3**: Open the Play Store on your Chromebook and install **Pydroid 3**.
2.  **Install Permissions Plugin**: Search for and install **Pydroid Permissions Plugin**.
3.  **Check Location**:
    *   Most Chromebooks do **not** have a GPS chip.
    *   They rely on Wi-Fi for location.
    *   This script is smart enough to use "Network" location if "GPS" is missing, but you MUST ensure **Location** is enabled in your Chromebook settings and permissions are granted to Pydroid 3.
4.  **Run**: Follow the same "Run on Android" steps above.

*Alternative*: If you use **Linux (Beta)** on your Chromebook, you can use the `mac_renamer.py` script instead, which uses IP-based location.

---

## How to Run on Mac (for Testing)
If you want to test the renaming logic on your computer (using simulated IP-based location):

1.  **Run the Mac wrapper**:
    ```bash
    python3 mac_renamer.py /path/to/test/folder --dry-run
    ```

## Troubleshooting
*   **"Android module not found"**: Ensure you are running this inside Pydroid 3.
*   **"Timed out"**: Make sure your Location/GPS is turned ON in Android settings. Move outdoors for a better signal.
*   **Permission Denied**: Check Android Settings -> Apps -> Pydroid 3 -> Permissions. Enable **Files and Media** (or Storage) and **Location**.

### "I cannot see/change permissions!"
If your device settings are greyed out or missing:
1.  Run the `fix_permissions.py` script included in this folder.
2.  It attempts to force the system to show the "Allow" dialogs.
3.  On **Chromebooks**, you often need to go to:
    *   Settings -> Apps -> **Manage Google Play preferences** -> Android Settings -> Apps -> Pydroid 3.
    *   (You cannot just use the normal ChromeOS settings menu).
