import os
import sys

# Ensure root directory is in sys.path so backend modules are imported cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Initialize database tables on serverless cold start if needed
try:
    from backend.app.init_db import init_database
    init_database()
except Exception as e:
    print(f"DB Init Note: {e}")

from backend.app.main import app
