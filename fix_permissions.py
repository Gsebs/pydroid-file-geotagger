import sys

# DEBUG: Check what we actually imported
try:
    import android
    # Check if this is the REAL android module (SL4A) or a fake/PyPI one
    if not hasattr(android, 'Android'):
        print("Warning: Imported 'android' module but it has no 'Android' class.")
        print("You likely installed the wrong package via 'pip install android'.")
        print("Attempting to uninstall it automatically could be dangerous, so we will try falling back to androidhelper.")
        del android
        raise ImportError("Wrong android module")
except ImportError:
    android = None

if not android:
    try:
        import androidhelper as android
    except ImportError:
        print("Error: Neither 'android' nor 'androidhelper' (SL4A) modules found.")
        print("FIX:")
        print("1. If you ran 'pip install android', run 'pip uninstall android' in Terminal.")
        print("2. Install 'Pydroid Repository Plugin' from the Play Store.")
        sys.exit(1)

try:
    droid = android.Android()
except AttributeError:
    print("Critical Error: The android module loaded does not have .Android().")
    sys.exit(1)

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
