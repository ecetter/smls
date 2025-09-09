#!/usr/bin/env python3
"""
OAuth Configuration Management for SMLS

This module provides centralized configuration management for OAuth 2.0
authentication with Google and LinkedIn. It handles dynamic credential
management, URL generation, and validation for secure OAuth operations.

Key Features:
- Dynamic OAuth URL generation based on deployment configuration
- Credential validation and format checking
- Environment-based configuration management
- Support for multiple OAuth providers
- Runtime URL adaptation for development and production

Configuration Areas:
- OAuth Provider URLs and endpoints
- Dynamic redirect URI generation
- Credential validation and security
- Environment variable management
- Session-based configuration storage

Author: SMLS Development Team
Version: 1.0.0
License: MIT
"""

import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import json
import base64

# Load environment variables from .env file if present
# This allows for flexible configuration management across environments
load_dotenv()

class Config:
    """
    Application configuration with dynamic credential management.
    
    This class provides centralized configuration management for the SMLS
    application, including OAuth settings, security parameters, and
    dynamic URL generation. It supports both environment-based and
    runtime configuration for flexible deployment scenarios.
    """
    
    # =============================================================================
    # FLASK CONFIGURATION
    # =============================================================================
    
    # Secret key for session signing and CSRF protection
    # Should be set via environment variable in production
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Session configuration for secure session management
    SESSION_TYPE = 'filesystem'           # Use filesystem for session storage
    SESSION_FILE_DIR = './sessions'       # Directory for session files
    SESSION_PERMANENT = False             # Sessions expire when browser closes
    SESSION_USE_SIGNER = True             # Sign session cookies for security
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    
    # Session cookie security configuration
    # These settings enhance security for session management
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # =============================================================================
    # BASE URL CONFIGURATION
    # =============================================================================
    
    # Base URL for the application (set dynamically via command line or environment)
    # This URL is used for generating OAuth redirect URIs and static file paths
    BASE_URL = 'http://localhost:5000'  # Default value, can be overridden
    
    # =============================================================================
    # OAUTH PROVIDER ENDPOINTS
    # =============================================================================
    
    # Google OAuth 2.0 endpoints
    # These URLs are used for Google OAuth authentication flow
    GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'
    
    # LinkedIn OAuth 2.0 endpoints
    # These URLs are used for LinkedIn OAuth authentication flow
    LINKEDIN_AUTH_URL = 'https://www.linkedin.com/oauth/v2/authorization'
    LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
    LINKEDIN_USER_INFO_URL = 'https://api.linkedin.com/v2/userinfo'
    
    # =============================================================================
    # DYNAMIC REDIRECT URI GENERATION
    # =============================================================================
    
    @classmethod
    def get_google_redirect_uri(cls):
        """
        Generate Google OAuth redirect URI based on current configuration.
        
        This method creates the redirect URI that Google will use to send
        users back to the application after authentication. It uses the
        runtime base URL if available (for development scenarios) or
        falls back to the configured BASE_URL.
        
        Returns:
            str: The complete redirect URI for Google OAuth callbacks
            
        Example:
            http://example.com:8080/app/auth/google/callback
        """
        # Use runtime base URL if available (for development), otherwise use BASE_URL
        base_url = getattr(cls, 'RUNTIME_BASE_URL', cls.BASE_URL)
        return f"{base_url}/auth/google/callback"
    
    @classmethod
    def get_linkedin_redirect_uri(cls):
        """
        Generate LinkedIn OAuth redirect URI based on current configuration.
        
        This method creates the redirect URI that LinkedIn will use to send
        users back to the application after authentication. It uses the
        runtime base URL if available (for development scenarios) or
        falls back to the configured BASE_URL.
        
        Returns:
            str: The complete redirect URI for LinkedIn OAuth callbacks
            
        Example:
            http://example.com:8080/app/auth/linkedin/callback
        """
        # Use runtime base URL if available (for development), otherwise use BASE_URL
        base_url = getattr(cls, 'RUNTIME_BASE_URL', cls.BASE_URL)
        return f"{base_url}/auth/linkedin/callback"
    
    # =============================================================================
    # OAUTH CONFIGURATION MANAGEMENT
    # =============================================================================
    
    @classmethod
    def get_oauth_config(cls, provider):
        """
        Get OAuth configuration for a specific provider.
        
        This method returns the complete OAuth configuration for the specified
        provider, including endpoints, redirect URIs, and placeholder values
        for client credentials. The actual client credentials are injected
        at runtime from session data or environment variables.
        
        Args:
            provider (str): The OAuth provider ('google' or 'linkedin')
            
        Returns:
            dict: OAuth configuration dictionary for the provider
            
        Raises:
            KeyError: If the provider is not supported
        """
        # Provider-specific OAuth configuration
        configs = {
            'google': {
                'client_id': None,  # Will be set from session or environment
                'client_secret': None,  # Will be set from session or environment
                'redirect_uri': cls.get_google_redirect_uri(),
                'auth_url': cls.GOOGLE_AUTH_URL,
                'token_url': cls.GOOGLE_TOKEN_URL,
                'user_info_url': cls.GOOGLE_USER_INFO_URL
            },
            'linkedin': {
                'client_id': None,  # Will be set from session or environment
                'client_secret': None,  # Will be set from session or environment
                'redirect_uri': cls.get_linkedin_redirect_uri(),
                'auth_url': cls.LINKEDIN_AUTH_URL,
                'token_url': cls.LINKEDIN_TOKEN_URL,
                'user_info_url': cls.LINKEDIN_USER_INFO_URL
            }
        }
        
        # Return configuration for the specified provider
        if provider not in configs:
            raise KeyError(f"Unsupported OAuth provider: {provider}")
        
        return configs[provider]
    
    # =============================================================================
    # CREDENTIAL VALIDATION
    # =============================================================================
    
    @classmethod
    def validate_oauth_credentials(cls, provider, client_id, client_secret):
        """
        Validate OAuth credentials format and structure.
        
        This method performs comprehensive validation of OAuth credentials
        to ensure they meet the requirements for the specified provider.
        It checks for required fields, minimum lengths, and provider-specific
        format requirements.
        
        Args:
            provider (str): The OAuth provider ('google' or 'linkedin')
            client_id (str): The OAuth client ID
            client_secret (str): The OAuth client secret
            
        Returns:
            tuple: (is_valid, error_message) where is_valid is boolean
                   and error_message is a string describing any issues
                   
        Example:
            >>> Config.validate_oauth_credentials('google', '123.apps.googleusercontent.com', 'secret')
            (True, "Credentials appear valid")
        """
        # Check for required fields
        if not client_id or not client_secret:
            return False, "Client ID and Client Secret are required"
        
        # Provider-specific validation
        if provider == 'google':
            # Google-specific validation
            if len(client_id.strip()) < 10:
                return False, "Client ID appears to be too short"
            if len(client_secret.strip()) < 10:
                return False, "Client Secret appears to be too short"
            if not client_id.endswith('.apps.googleusercontent.com'):
                return False, "Google Client ID should end with '.apps.googleusercontent.com'"
                
        elif provider == 'linkedin':
            # LinkedIn-specific validation
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
        
        # All validations passed
        return True, "Credentials appear valid"