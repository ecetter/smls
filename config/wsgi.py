#!/usr/bin/env python3
"""
WSGI Entry Point for SMLS Production Deployment

This module serves as the WSGI application entry point for production
deployment with Gunicorn. It initializes the Flask application with
production-specific configuration, security settings, and middleware.

Key Responsibilities:
- Application Initialization: Sets up Flask app with production config
- Security Configuration: Applies production security headers and settings
- Environment Management: Handles environment variables and configuration
- Health Monitoring: Provides health check endpoint for load balancers
- Error Handling: Implements production-grade error handling

Production Features:
- Comprehensive security headers for all responses
- Health check endpoint for monitoring and load balancing
- Production-optimized Flask configuration
- Environment variable management
- WSGI-compatible application object

Usage:
    gunicorn -c gunicorn.conf.py wsgi:application

Author: SMLS Development Team
Version: 1.0.0
License: MIT
"""

import os
import sys
from pathlib import Path

# =============================================================================
# PYTHON PATH CONFIGURATION
# =============================================================================

# Add the src directory to Python path for module resolution
# This ensures that the Flask application can import its modules correctly
# when running in the WSGI environment
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

# Set production environment variables
# These variables configure Flask for production deployment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

# Load environment variables from .env file if present
# This allows for flexible configuration management in production
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available - continue without it
    pass

# =============================================================================
# APPLICATION IMPORT AND INITIALIZATION
# =============================================================================

# Import the Flask application from the main app module
# This imports the configured Flask app with all routes and middleware
from app import app

# =============================================================================
# PRODUCTION CONFIGURATION
# =============================================================================

# Apply production-specific configuration to the Flask app
# These settings optimize the application for production deployment
app.config.update(
    # Disable debug mode for production
    DEBUG=False,
    
    # Disable testing mode
    TESTING=False,
    
    # Secret key for session signing and CSRF protection
    # Should be set via environment variable in production
    SECRET_KEY=os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production'),
    
    # Session security configuration
    SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true',  # Only send cookies over HTTPS in production
    SESSION_COOKIE_HTTPONLY=True,    # Prevent XSS attacks on cookies
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
    
    # Session timeout configuration
    PERMANENT_SESSION_LIFETIME=3600,  # 1 hour session timeout
    
    # Request size limits for security
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload size
)

# =============================================================================
# SECURITY HEADERS MIDDLEWARE
# =============================================================================

@app.after_request
def add_security_headers(response):
    """
    Add comprehensive security headers to all responses.
    
    This middleware implements defense-in-depth security by adding multiple
    layers of protection against common web vulnerabilities. The headers
    are applied to every response from the application.
    
    Security Headers Applied:
    - X-Content-Type-Options: Prevents MIME type sniffing attacks
    - X-Frame-Options: Prevents clickjacking attacks
    - X-XSS-Protection: Enables browser XSS filtering
    - Strict-Transport-Security: Enforces HTTPS in production
    - Referrer-Policy: Controls referrer information leakage
    - Content-Security-Policy: Prevents XSS and injection attacks
    
    Args:
        response: Flask response object
        
    Returns:
        Flask response object with security headers added
    """
    # Prevent MIME type sniffing attacks
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Prevent clickjacking attacks
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Enable XSS protection in browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Enforce HTTPS in production (1 year max-age)
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Control referrer information leakage
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Content Security Policy to prevent XSS and injection attacks
    # This policy allows:
    # - Resources from same origin ('self')
    # - External CDNs for fonts and icons (Google Fonts, Font Awesome)
    # - Inline scripts and styles (required for some functionality)
    # - Images from same origin, data URLs, and HTTPS sources
    # - Connections to same origin only
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'"
    )
    
    return response

# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@app.route('/health')
def health_check():
    """
    Health check endpoint for monitoring and load balancing.
    
    This endpoint provides a simple health check that can be used by:
    - Load balancers to determine server health
    - Monitoring systems to verify application availability
    - Orchestration platforms for health checks
    - CI/CD pipelines for deployment verification
    
    The endpoint returns a simple JSON response indicating the service
    is healthy and operational. This is sufficient for most monitoring
    systems and load balancers.
    
    Returns:
        JSON response with application status and version information
    """
    return {
        'status': 'healthy',
        'service': 'smls',
        'version': '1.0.0'
    }, 200

# =============================================================================
# WSGI APPLICATION OBJECT
# =============================================================================

# Create the WSGI application object for Gunicorn
# This is the object that Gunicorn will use to serve the application
application = app

# =============================================================================
# DEVELOPMENT MODE CHECK
# =============================================================================

if __name__ == "__main__":
    """
    Development mode check and warning.
    
    This section runs when the WSGI module is executed directly,
    which should not happen in production. It provides a warning
    and usage instructions for proper deployment.
    """
    print("This is a WSGI application. Use Gunicorn to run it in production.")
    print("Example: gunicorn -c gunicorn.conf.py wsgi:application")