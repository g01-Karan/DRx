"""
==============================================================================
Vercel Serverless Entry Point — WSGI Application Handler
==============================================================================
Provides standard WSGI application instance with URL path normalization
for Vercel Serverless Functions.
==============================================================================
"""

import os
import sys
from urllib.parse import parse_qs

# Add project root directory to python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app


class VercelPathFixer:
    """WSGI Middleware to restore original PATH_INFO on Vercel Serverless Functions."""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        qs_string = environ.get('QUERY_STRING', '')
        qs = parse_qs(qs_string)
        if '__path' in qs:
            path = qs['__path'][0]
            if not path.startswith('/'):
                path = '/' + path
            environ['PATH_INFO'] = path
        return self.app(environ, start_response)


# Export WSGI application handle for Vercel Serverless Function
app = VercelPathFixer(app)
