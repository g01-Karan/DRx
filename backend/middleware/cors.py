"""
==============================================================================
CORS & Response Headers Middleware
==============================================================================
Ensures proper HTTP security headers, CORS headers, and asset caching headers.
==============================================================================
"""

def init_cors_middleware(app):
    """Register response header hooks for CORS and security."""
    @app.after_request
    def add_security_and_cors_headers(response):
        # Cross-Origin Resource Sharing
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-User-ID'
        
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
