import sys
import os

# Add app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.main import app
    print("SUCCESS: FastAPI App imported cleanly!")
    print(f"Project Title: {app.title}")
    print(f"Version: {app.version}")
except Exception as e:
    print("ERROR during import:", e)
