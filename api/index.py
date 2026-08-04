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

# Add project root directory to python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app


class VercelPathFixer:
    """WSGI Middleware to normalize PATH_INFO when rewritten by Vercel."""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path in ['/api/index.py', '/api/index', '/api']:
            forwarded_uri = environ.get('HTTP_X_FORWARDED_URI') or environ.get('HTTP_X_MATCHED_PATH')
            if forwarded_uri and not forwarded_uri.startswith('/api/index'):
                environ['PATH_INFO'] = forwarded_uri.split('?')[0]
            else:
                environ['PATH_INFO'] = '/'
        return self.app(environ, start_response)


# Export WSGI application handle for Vercel Serverless Function
app = VercelPathFixer(app)
