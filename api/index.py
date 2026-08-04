"""
==============================================================================
Vercel Serverless Entry Point — WSGI Application Handler
==============================================================================
Provides standard WSGI application instance for Vercel Serverless Functions.
==============================================================================
"""

import os
import sys

# Add project root directory to python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app

# Export app instance for Vercel WSGI environment
app = app
