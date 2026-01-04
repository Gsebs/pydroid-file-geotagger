try:
    import android
except ImportError:
    try:
        import androidhelper as android
    except ImportError:
        print("Error: Neither 'android' nor 'androidhelper' modules found.")
        print("Make sure you are running this in Pydroid 3 with the Repository Plugin installed.")
        import sys
        sys.exit(1)

droid = android.Android()

print("Attempting to request permissions...")
# This often forces the dialog to appear in Pydroid 3
droid.makeToast("Requesting Permissions...")

# Request specific permissions
permissions = [
    'android.permission.READ_EXTERNAL_STORAGE',
    'android.permission.WRITE_EXTERNAL_STORAGE',
    'android.permission.ACCESS_FINE_LOCATION',
    'android.permission.ACCESS_COARSE_LOCATION'
]

# Note: Pydroid 3 specific API for permissions might vary, 
# but usually initializing the droid object and accessing a sensor 
# triggers the prompt if the Repo Plugin is installed.

try:
    # Try to start locating, which usually forces the Location prompt
    droid.startLocating()
    print("Location service started (Permission check).")
except Exception as e:
    print(f"Error starting location: {e}")

print("Please check your screen for a permission dialog and click 'Allow'.")
input("Press Enter to continue...")
