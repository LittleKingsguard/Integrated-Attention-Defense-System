import sys
import os

# Add the project root to sys.path
root = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(root)

try:
    from registry.src import crud
    print("Import registry.src.crud successful")
    from registry.src.db.core import init_db
    print("Import registry.src.db.core successful")
except Exception as e:
    print(f"Import failed: {e}")
