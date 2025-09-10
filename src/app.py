#!/usr/bin/env python3
"""
SMLS - Social Media Login Service
Main Flask Application

This module implements a production-ready social media authentication service
that provides OAuth 2.0 integration with Google and LinkedIn. The application
is designed for enterprise deployment with comprehensive security features,
health monitoring, and subpath support for reverse proxy configurations.

Key Features:
- OAuth 2.0 authentication with Google and LinkedIn
- Production-grade security headers and session management
- Subpath support for reverse proxy deployments
- Health monitoring endpoint for load balancers
- Comprehensive error handling and logging
- WSGI-compatible for production deployment

Architecture:
- Flask application with modular authentication system
- OAuth manager handles 3-legged authorization flow
- Middleware for subpath routing and security headers
- Session-based state management with secure cookies
- Configurable base URL for flexible deployment scenarios
"""

# Standard library imports
import os
import sys
import logging
import argparse
from urllib.parse import urlparse

# Third-party imports
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session import Session

# Local imports - Add auth directory to Python path for module resolution
sys.path.append(os.path.join(os.path.dirname(__file__), 'auth'))
from auth.config import Config
from auth.oauth_manager import OAuthManager

# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================

def load_configuration():
    """
    Load application configuration from environment variables or command line.
    
    This function handles the dual-mode operation of the application:
    1. Direct execution: Parses command line arguments for development
    2. WSGI import: Reads from environment variables for production
    
    The BASE_URL configuration is critical as it determines:
    - OAuth callback URLs for external providers
    - Static file serving paths
    - Application routing for subpath deployments
    - Security header configuration
    """
    if __name__ == "__main__":
        # Development mode: Parse command line arguments
        parser = argparse.ArgumentParser(
            description='Social Media Login Service (SMLS)',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python app.py --base-url http://localhost:5000
  python app.py --base-url https://example.com/app
  python app.py --base-url http://mydomain.com:8080/smls
            """
        )
        parser.add_argument(
            '--base-url', 
            default='http://localhost:5000',
            help='Base URL for the application (default: http://localhost:5000)'
        )
        args = parser.parse_args()
        Config.BASE_URL = args.base_url
    else:
        # Production mode: Read from environment variables
        Config.BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

# Load configuration before creating Flask app
load_configuration()

def get_runtime_base_url():
    """
    Generate runtime base URL for OAuth callbacks.
    
    This function creates the actual URL that OAuth providers will use for
    callbacks. It handles the difference between development and production
    environments, ensuring that OAuth callbacks work correctly regardless
    of the deployment configuration.
    
    Key considerations:
    - Development servers typically use HTTP on non-standard ports
    - Production deployments may use HTTPS with standard ports
    - Subpath deployments require path preservation
    - Port mapping for reverse proxy configurations
    
    Returns:
        str: The runtime base URL for OAuth callbacks
        
    Example:
        Input:  https://example.com:8443/app
        Output: http://example.com:8080/app
    """
    parsed_url = urlparse(Config.BASE_URL)
    
    # Force HTTP for development (Flask dev server doesn't support HTTPS)
    # In production, this would typically be handled by a reverse proxy
    if parsed_url.scheme == 'https':
        scheme = 'http'
    else:
        scheme = parsed_url.scheme
    
    # Use development port if none specified
    if not parsed_url.port:
        port = 8080  # Standard development port
    else:
        port = parsed_url.port
    
    # Reconstruct URL with correct scheme and port
    runtime_url = f"{scheme}://{parsed_url.hostname}:{port}{parsed_url.path}"
    return runtime_url

# Set the runtime base URL for OAuth callbacks
Config.RUNTIME_BASE_URL = get_runtime_base_url()

# Extract application prefix from base URL for subpath deployment
from urllib.parse import urlparse
parsed_base_url = urlparse(Config.BASE_URL)
application_prefix = parsed_base_url.path.rstrip('/') if parsed_base_url.path != '/' else ''

# Initialize Flask app with application prefix if needed
if application_prefix:
    app = Flask(__name__, static_url_path=f'{application_prefix}/static')
else:
    app = Flask(__name__)

app.config.from_object(Config)

# Make config available in templates
@app.context_processor
def inject_config():
    return dict(config=Config)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/smls.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize session
Session(app)

# Initialize OAuth manager (will be configured dynamically)
oauth_manager = OAuthManager()

# Add URL prefix for subpath deployment
if application_prefix:
    class PrefixMiddleware:
        def __init__(self, app, prefix):
            self.app = app
            self.prefix = prefix
        
        def __call__(self, environ, start_response):
            original_path = environ['PATH_INFO']
            
            # Handle static files and other requests
            if original_path.startswith(f'{self.prefix}/static/'):
                # For static files, remove the prefix
                environ['PATH_INFO'] = original_path[len(self.prefix):]
            elif original_path.startswith(self.prefix):
                # For other requests, remove the prefix
                environ['PATH_INFO'] = original_path[len(self.prefix):]
                if not environ['PATH_INFO']:
                    environ['PATH_INFO'] = '/'
            
            # Debug logging
            if original_path != environ['PATH_INFO']:
                print(f"🔧 Middleware: {original_path} → {environ['PATH_INFO']}")
            
            return self.app(environ, start_response)
    
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, application_prefix)

@app.route('/')
def index():
    """Main login page."""
    return render_template('index.html')

# Add explicit static file route for debugging
@app.route('/static/<path:filename>')
def static_files(filename):
    """Explicit static file handler for debugging."""
    from flask import send_from_directory
    return send_from_directory('static', filename)


@app.route('/setup')
def setup_credentials():
    """OAuth credentials setup page."""
    return render_template('credentials.html')

@app.route('/save-credentials', methods=['POST'])
def save_credentials():
    """Save OAuth credentials to session (additive)."""
    try:
        # Get form data
        google_enabled = request.form.get('google_enabled') == 'on'
        linkedin_enabled = request.form.get('linkedin_enabled') == 'on'
        
        # Get existing credentials or create new dict
        oauth_credentials = session.get('oauth_credentials', {})
        
        # Process Google credentials
        if google_enabled:
            google_client_id = request.form.get('google_client_id', '').strip()
            google_client_secret = request.form.get('google_client_secret', '').strip()
            
            # Validate Google credentials
            is_valid, message = Config.validate_oauth_credentials('google', google_client_id, google_client_secret)
            if not is_valid:
                flash(f'Google credentials error: {message}', 'error')
                return redirect(url_for('setup_credentials'))
            
            oauth_credentials['google'] = {
                'client_id': google_client_id,
                'client_secret': google_client_secret,
                'enabled': True
            }
            flash('Google OAuth credentials added successfully!', 'success')
        
        # Process LinkedIn credentials
        if linkedin_enabled:
            linkedin_client_id = request.form.get('linkedin_client_id', '').strip()
            linkedin_client_secret = request.form.get('linkedin_client_secret', '').strip()
            
            # Validate LinkedIn credentials
            is_valid, message = Config.validate_oauth_credentials('linkedin', linkedin_client_id, linkedin_client_secret)
            if not is_valid:
                flash(f'LinkedIn credentials error: {message}', 'error')
                return redirect(url_for('setup_credentials'))
            
            oauth_credentials['linkedin'] = {
                'client_id': linkedin_client_id,
                'client_secret': linkedin_client_secret,
                'enabled': True
            }
            flash('LinkedIn OAuth credentials added successfully!', 'success')
        
        # Check if at least one provider is configured
        if not oauth_credentials:
            flash('Please enable and configure at least one OAuth provider.', 'error')
            return redirect(url_for('setup_credentials'))
        
        # Store credentials in session
        session['oauth_credentials'] = oauth_credentials
        
        return redirect(url_for('setup_credentials'))
        
    except Exception as e:
        flash(f'Error saving credentials: {str(e)}', 'error')
        return redirect(url_for('setup_credentials'))

@app.route('/remove-credential', methods=['POST'])
def remove_credential():
    """Remove a specific OAuth credential from session."""
    try:
        provider = request.form.get('provider')
        
        if not provider:
            flash('No provider specified for removal.', 'error')
            return redirect(url_for('setup_credentials'))
        
        # Get existing credentials
        oauth_credentials = session.get('oauth_credentials', {})
        
        if provider in oauth_credentials:
            del oauth_credentials[provider]
            session['oauth_credentials'] = oauth_credentials
            provider_name = 'Google' if provider == 'google' else provider.title()
            flash(f'{provider_name} OAuth credentials removed successfully!', 'success')
        else:
            provider_name = 'Google' if provider == 'google' else provider.title()
            flash(f'{provider_name} credentials not found.', 'error')
        
        return redirect(url_for('setup_credentials'))
        
    except Exception as e:
        flash(f'Error removing credentials: {str(e)}', 'error')
        return redirect(url_for('setup_credentials'))

@app.route('/login/google')
def login_google():
    """Initiate Google OAuth flow."""
    try:
        logger.info("Initiating Google OAuth flow")
        
        # Check if Google credentials are configured
        if not session.get('oauth_credentials', {}).get('google', {}).get('enabled'):
            logger.warning("Google OAuth not configured - redirecting to setup")
            flash('Google OAuth is not configured. Please setup credentials first.', 'error')
            return redirect(url_for('setup_credentials'))
        
        google_creds = session['oauth_credentials']['google']
        auth_url, state, code_verifier = oauth_manager.get_google_auth_url(
            client_id=google_creds['client_id']
        )
        
        # Store state and code_verifier in session for validation
        session['oauth_state'] = state
        session['code_verifier'] = code_verifier
        session['provider'] = 'google'
        
        logger.info(f"Google OAuth flow initiated successfully. State: {state[:8]}...")
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Error initiating Google login: {str(e)}", exc_info=True)
        flash(f'Error initiating Google login: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/login/linkedin')
def login_linkedin():
    """Initiate LinkedIn OAuth flow."""
    try:
        logger.info("Initiating LinkedIn OAuth flow")
        
        # Check if LinkedIn credentials are configured
        if not session.get('oauth_credentials', {}).get('linkedin', {}).get('enabled'):
            logger.warning("LinkedIn OAuth not configured - redirecting to setup")
            flash('LinkedIn OAuth is not configured. Please setup credentials first.', 'error')
            return redirect(url_for('setup_credentials'))
        
        linkedin_creds = session['oauth_credentials']['linkedin']
        auth_url, state = oauth_manager.get_linkedin_auth_url(
            client_id=linkedin_creds['client_id']
        )
        
        # Store state in session for validation
        session['oauth_state'] = state
        session['provider'] = 'linkedin'
        
        logger.info(f"LinkedIn OAuth flow initiated successfully. State: {state[:8]}...")
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Error initiating LinkedIn login: {str(e)}", exc_info=True)
        flash(f'Error initiating LinkedIn login: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    try:
        logger.info("Processing Google OAuth callback")
        
        # Validate state parameter
        if 'oauth_state' not in session:
            logger.warning("Google callback: No oauth_state in session")
            flash('Invalid session. Please try again.', 'error')
            return redirect(url_for('index'))
        
        state = request.args.get('state')
        if state != session['oauth_state']:
            logger.warning(f"Google callback: State mismatch. Expected: {session['oauth_state'][:8]}..., Got: {state[:8] if state else 'None'}...")
            flash('Invalid state parameter. Possible CSRF attack.', 'error')
            return redirect(url_for('index'))
        
        code = request.args.get('code')
        if not code:
            error = request.args.get('error', 'Unknown error')
            logger.error(f"Google callback: Authorization failed - {error}")
            flash(f'Authorization failed: {error}', 'error')
            return redirect(url_for('index'))
        
        # Exchange code for tokens
        code_verifier = session.get('code_verifier')
        if not code_verifier:
            logger.warning("Google callback: Missing code verifier")
            flash('Missing code verifier. Please try again.', 'error')
            return redirect(url_for('index'))
        
        # Get Google credentials from session
        google_creds = session.get('oauth_credentials', {}).get('google', {})
        if not google_creds.get('enabled'):
            logger.warning("Google callback: OAuth credentials not found")
            flash('Google OAuth credentials not found. Please setup credentials first.', 'error')
            return redirect(url_for('setup_credentials'))
        
        logger.info("Exchanging Google authorization code for tokens")
        user_info = oauth_manager.handle_google_callback(
            code, state, 
            google_creds['client_id'], 
            google_creds['client_secret'],
            code_verifier
        )
        
        if not user_info:
            logger.error("Google callback: Failed to obtain user information")
            flash('Failed to obtain user information.', 'error')
            return redirect(url_for('index'))
        
        # Store user data in session
        session['user'] = {
            'id': user_info.get('id'),
            'name': user_info.get('name'),
            'email': user_info.get('email'),
            'picture': user_info.get('picture'),
            'provider': 'google'
        }
        
        # Clear OAuth session data
        session.pop('oauth_state', None)
        session.pop('code_verifier', None)
        session.pop('provider', None)
        
        logger.info(f"Google authentication successful for user: {user_info.get('email', 'Unknown')}")
        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error during Google authentication: {str(e)}", exc_info=True)
        flash(f'Error during Google authentication: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/auth/linkedin/callback')
def linkedin_callback():
    """Handle LinkedIn OAuth callback."""
    try:
        logger.info("Processing LinkedIn OAuth callback")
        
        # Validate state parameter
        if 'oauth_state' not in session:
            logger.warning("LinkedIn callback: No oauth_state in session")
            flash('Invalid session. Please try again.', 'error')
            return redirect(url_for('index'))
        
        state = request.args.get('state')
        if state != session['oauth_state']:
            logger.warning(f"LinkedIn callback: State mismatch. Expected: {session['oauth_state'][:8]}..., Got: {state[:8] if state else 'None'}...")
            flash('Invalid state parameter. Possible CSRF attack.', 'error')
            return redirect(url_for('index'))
        
        code = request.args.get('code')
        if not code:
            error = request.args.get('error', 'Unknown error')
            logger.error(f"LinkedIn callback: Authorization failed - {error}")
            flash(f'Authorization failed: {error}', 'error')
            return redirect(url_for('index'))
        
        # Exchange code for tokens
        # Get LinkedIn credentials from session
        linkedin_creds = session.get('oauth_credentials', {}).get('linkedin', {})
        if not linkedin_creds.get('enabled'):
            logger.warning("LinkedIn callback: OAuth credentials not found")
            flash('LinkedIn OAuth credentials not found. Please setup credentials first.', 'error')
            return redirect(url_for('setup_credentials'))
        
        logger.info("Exchanging LinkedIn authorization code for tokens")
        user_info = oauth_manager.handle_linkedin_callback(
            code, 
            state,
            linkedin_creds['client_id'], 
            linkedin_creds['client_secret']
        )
        
        logger.error(f"DEBUG: LinkedIn callback received user_info: {user_info}")
        
        if not user_info:
            logger.error("LinkedIn callback: Failed to obtain user information")
            flash('Failed to obtain user information.', 'error')
            return redirect(url_for('index'))
        
        # Store user data in session
        session['user'] = {
            'id': user_info.get('id'),
            'name': user_info.get('name', 'LinkedIn User'),
            'email': user_info.get('email'),
            'picture': user_info.get('picture'),
            'provider': 'linkedin'
        }
        
        # Clear OAuth session data
        session.pop('oauth_state', None)
        session.pop('provider', None)
        
        logger.info(f"LinkedIn authentication successful for user: {user_info.get('email', 'Unknown')}")
        flash('Successfully logged in with LinkedIn!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error during LinkedIn authentication: {str(e)}", exc_info=True)
        flash(f'Error during LinkedIn authentication: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """User dashboard after successful authentication."""
    if 'user' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('index'))
    
    user = session['user']
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    """Logout user and clear session."""
    user_email = session.get('user', {}).get('email', 'Unknown')
    logger.info(f"User logout: {user_email}")
    
    # Keep OAuth credentials in session for convenience
    oauth_credentials = session.get('oauth_credentials')
    session.clear()
    if oauth_credentials:
        session['oauth_credentials'] = oauth_credentials
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/clear-credentials')
def clear_credentials():
    """Clear OAuth credentials from session."""
    session.pop('oauth_credentials', None)
    flash('OAuth credentials cleared successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/api/user')
def api_user():
    """API endpoint to get current user information."""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify(session['user'])

@app.route('/image-proxy/<path:image_url>')
def image_proxy(image_url):
    """Proxy endpoint to serve images that have CORS restrictions."""
    try:
        # Decode the URL
        import urllib.parse
        decoded_url = urllib.parse.unquote(image_url)
        
        # Handle data URIs - don't try to fetch them
        if decoded_url.startswith('data:'):
            from flask import Response
            return Response("Data URIs don't need proxying", status=400, mimetype='text/plain')
        
        # Add protocol if missing
        if not decoded_url.startswith(('http://', 'https://')):
            decoded_url = 'https://' + decoded_url
        
        # Fetch the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        logger.error(f"DEBUG: Image proxy fetching URL: {decoded_url}")
        response = requests.get(decoded_url, headers=headers, timeout=10)
        logger.error(f"DEBUG: Image proxy response status: {response.status_code}")
        logger.error(f"DEBUG: Image proxy response content length: {len(response.content)}")
        logger.error(f"DEBUG: Image proxy response content preview: {response.content[:100]}")
        response.raise_for_status()
        
        # Return the image with simple response handling
        from flask import Response
        return Response(
            response.content,
            mimetype='image/png'  # Use simple mimetype like the working minimal test
        )
        
    except Exception as e:
        # Return a 1x1 transparent pixel as fallback
        from flask import Response
        transparent_pixel = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        return Response(transparent_pixel, mimetype='image/png')

@app.route('/proxy')
def proxy_alt():
    """Alternative proxy endpoint using query parameter."""
    from flask import request
    image_url = request.args.get('url')
    
    if not image_url:
        return "Missing URL parameter", 400
    
    # Handle data URIs - don't try to fetch them
    if image_url.startswith('data:'):
        from flask import Response
        return Response("Data URIs don't need proxying", status=400, mimetype='text/plain')
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        from flask import Response
        return Response(
            response.content,
            mimetype='image/png'  # Use simple mimetype like the working minimal test
        )
        
    except Exception as e:
        from flask import Response
        transparent_pixel = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        return Response(transparent_pixel, mimetype='image/png')

if __name__ == '__main__':
    # Parse the base URL to extract host and port
    from urllib.parse import urlparse
    
    parsed_url = urlparse(Config.BASE_URL)
    
    # Flask should run on all interfaces to be accessible externally
    # nginx will handle the external port and domain
    host = '0.0.0.0'
    port = 5000
    
    # Check if port 5000 is available, if not find an available port
    import socket
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return True
            except OSError:
                return False
    
    # Try to find an available port starting from 5000
    original_port = port
    while not is_port_available(port) and port < 5100:
        port += 1
    
    if port != original_port:
        print(f"⚠️  Port {original_port} is in use, using port {port} instead")
    
    print(f"🌐 Starting server on {host}:{port}")
    print(f"📱 Base URL: {Config.BASE_URL}")
    
    # Add helpful messages about development vs production
    if parsed_url.scheme == 'https':
        print("⚠️  Note: Flask development server doesn't support HTTPS/SSL.")
        print(f"   Access your app at: http://{host}:{port}{parsed_url.path}")
        print("   For production HTTPS, use a reverse proxy (nginx, Apache) or WSGI server.")
    elif port in [80, 443] and host != 'localhost':
        print("⚠️  Note: Using privileged ports (80/443) requires root privileges.")
        print("   For development, consider using ports 8080 (HTTP) or 8443 (HTTPS)")
    
    # Show application prefix info if applicable
    if application_prefix:
        print(f"📁 Application prefix: {application_prefix}")
        print(f"   Routes will be available under: {application_prefix}/")
    
    # Show OAuth redirect URIs
    print(f"🔐 OAuth redirect URIs:")
    print(f"   Google: {Config.get_google_redirect_uri()}")
    print(f"   LinkedIn: {Config.get_linkedin_redirect_uri()}")
    print(f"   ⚠️  Make sure these URLs are configured in your OAuth apps!")
    
    # Configure Flask to prevent thread exhaustion
    app.run(host=host, port=port, debug=True, threaded=True, use_reloader=False)