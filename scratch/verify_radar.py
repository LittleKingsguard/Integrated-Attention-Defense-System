import sys
import os

# Add the project root to sys.path
root = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(root)

try:
    print("Checking Radar service imports...")
    from radar.src.main import app
    print("Import main.app successful")
    from radar.src.services.extractor import extractor
    print("Import extractor successful")
    from radar.src.services.notifier import notify_interested_users
    print("Import notifier successful")
    print("\nAll Radar imports successful!")
except Exception as e:
    print(f"\nImport failed: {e}")
    import traceback
    traceback.print_exc()
