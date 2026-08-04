import os
import sys

# Add project root directory to python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import Flask app instance from backend
from backend.app import app

# WSGI application handle for Vercel Serverless Function
app = app
