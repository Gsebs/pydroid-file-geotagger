# Deploying to Zebra Scanners (and other Industrial Android Devices)

Zebra scanners typically do not have the Google Play Store, so "Pydroid 3" plugins will not work.
Instead, we use **Termux**, which is the industry standard for on-device scripting.

## Step 1: Install the Environment
Since you cannot use the Play Store, you will "sideload" the apps from **F-Droid** (a trusted open-source app repository).

1.  **Open Chrome** (or the browser) on your Zebra device.
2.  **Download Termux**:
    *   Go to: `https://f-droid.org/en/packages/com.termux/`
    *   Scroll down to "Download APK" and download it.
    *   Open the file and install. (You may need to allow "Install from unknown sources").
3.  **Download Termux:API**:
    *   Go to: `https://f-droid.org/en/packages/com.termux.api/`
    *   Download and install the APK.
    *   **Crucial**: This app acts as the bridge to the Zebra hardware (GPS).

## Step 2: Configure Termux
1.  Open the **Termux** app you just installed.
2.  Type the following commands (press Enter after each):
    ```bash
    pkg update -y
    pkg install python termux-api -y
    termux-setup-storage
    ```
    *   When you run `termux-setup-storage`, a popup will appear asking for **"File/Storage Permissions"**. Tap **Allow**.

## Step 3: Get the Script
1.  Download the `geo_renamer.py` file to your device (e.g., in your Downloads folder).
2.  In Termux, navigate to that folder:
    ```bash
    cd /sdcard/Download
    ```

## Step 4: Run It
Run the script exactly as you would on a computer. The script has been updated to automatically detect Termux and use it for GPS.

```bash
python geo_renamer.py /sdcard/Documents/TargetFolder
```

**Note**: When you first run it, it might ask for **Location Permissions** (via the Termux:API). **Allow** it (select "Allow all the time" or "Allow while using app").
