import os
import sys

# Add parent directory to sys.path so app and other modules can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import app

# Vercel looks for 'app' in api/index.py
# If run directly for local testing
if __name__ == '__main__':
    app.run(port=5000)

