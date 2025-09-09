import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import json
import base64

# Load environment variables
load_dotenv()

class Config:
    """Application configuration with dynamic credential management."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './sessions'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # Security Settings
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Base URL Configuration (set dynamically via command line or environment)
    BASE_URL = 'http://localhost:5000'  # Default value, can be overridden
    
    # OAuth URLs (static)
    GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'
    
    LINKEDIN_AUTH_URL = 'https://www.linkedin.com/oauth/v2/authorization'
    LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
    LINKEDIN_USER_INFO_URL = 'https://api.linkedin.com/v2/userinfo'
    
    # Default redirect URIs
    @classmethod
    def get_google_redirect_uri(cls):
        # Use runtime base URL if available (for development), otherwise use BASE_URL
        base_url = getattr(cls, 'RUNTIME_BASE_URL', cls.BASE_URL)
        return f"{base_url}/auth/google/callback"
    
    @classmethod
    def get_linkedin_redirect_uri(cls):
        # Use runtime base URL if available (for development), otherwise use BASE_URL
        base_url = getattr(cls, 'RUNTIME_BASE_URL', cls.BASE_URL)
        return f"{base_url}/auth/linkedin/callback"
    
    @classmethod
    def get_oauth_config(cls, provider):
        """Get OAuth configuration for a specific provider from session."""
        # This will be called with session data containing user-provided credentials
        return {
            'google': {
                'client_id': None,  # Will be set from session
                'client_secret': None,  # Will be set from session
                'redirect_uri': cls.get_google_redirect_uri(),
                'auth_url': cls.GOOGLE_AUTH_URL,
                'token_url': cls.GOOGLE_TOKEN_URL,
                'user_info_url': cls.GOOGLE_USER_INFO_URL
            },
            'linkedin': {
                'client_id': None,  # Will be set from session
                'client_secret': None,  # Will be set from session
                'redirect_uri': cls.get_linkedin_redirect_uri(),
                'auth_url': cls.LINKEDIN_AUTH_URL,
                'token_url': cls.LINKEDIN_TOKEN_URL,
                'user_info_url': cls.LINKEDIN_USER_INFO_URL
            }
        }.get(provider, {})
    
    @classmethod
    def validate_oauth_credentials(cls, provider, client_id, client_secret):
        """Validate OAuth credentials format."""
        if not client_id or not client_secret:
            return False, "Client ID and Client Secret are required"
        
        # Provider-specific validation
        if provider == 'google':
            if len(client_id.strip()) < 10:
                return False, "Client ID appears to be too short"
            if len(client_secret.strip()) < 10:
                return False, "Client Secret appears to be too short"
            if not client_id.endswith('.apps.googleusercontent.com'):
                return False, "Google Client ID should end with '.apps.googleusercontent.com'"
        elif provider == 'linkedin':
            # LinkedIn credentials can be shorter than Google credentials
            if len(client_id.strip()) < 8:
                return False, "LinkedIn Client ID appears to be too short"
            if len(client_secret.strip()) < 8:
                return False, "LinkedIn Client Secret appears to be too short"
        else:
            # Default validation for unknown providers
            if len(client_id.strip()) < 8:
                return False, "Client ID appears to be too short"
            if len(client_secret.strip()) < 8:
                return False, "Client Secret appears to be too short"
        
        return True, "Credentials appear valid"
