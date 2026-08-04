"""
Root Application Launcher
Delegates execution to backend/app.py for clean project folder organization.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

from backend.app import app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
