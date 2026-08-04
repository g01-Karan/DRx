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
    """WSGI Middleware to restore original PATH_INFO on Vercel Serverless Functions."""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path.startswith('/api/index') or path == '/api' or path == '/api/':
            real_path = (
                environ.get('HTTP_X_MATCHED_PATH') or
                environ.get('HTTP_X_FORWARDED_URI') or
                environ.get('REQUEST_URI') or
                environ.get('RAW_URI') or
                '/'
            )
            real_path = real_path.split('?')[0]
            if real_path.startswith('/api/index.py'):
                real_path = real_path[13:] or '/'
            elif real_path.startswith('/api/index'):
                real_path = real_path[10:] or '/'

            environ['PATH_INFO'] = real_path if real_path else '/'

        return self.app(environ, start_response)


# Export WSGI application handle for Vercel Serverless Function
app = VercelPathFixer(app)
