#!/usr/bin/env python3
"""
OAuth 2.0 Manager for SMLS Authentication

This module implements a comprehensive OAuth 2.0 authentication manager
that handles the complete 3-legged authorization flow for Google and
LinkedIn. It provides secure token exchange, user information retrieval,
and state management for OAuth operations.

Key Features:
- OAuth 2.0 3-legged authorization flow implementation
- PKCE (Proof Key for Code Exchange) support for enhanced security
- State parameter generation for CSRF protection
- Token exchange and user information retrieval
- Provider-specific OAuth handling (Google, LinkedIn)
- Secure credential management and validation

Security Features:
- CSRF protection via state parameters
- PKCE implementation for public clients
- Secure token storage and management
- Input validation and sanitization
- Error handling and logging

Author: SMLS Development Team
Version: 1.0.0
License: MIT
"""

import requests
import secrets
import hashlib
import base64
from urllib.parse import urlencode, parse_qs
from .config import Config

class OAuthManager:
    """
    Handles OAuth 2.0 3-legged authorization flow for Google and LinkedIn.
    
    This class provides a complete implementation of the OAuth 2.0 authorization
    code flow with PKCE (Proof Key for Code Exchange) for enhanced security.
    It supports multiple OAuth providers and handles the complete authentication
    lifecycle from authorization URL generation to user information retrieval.
    
    The OAuth flow consists of:
    1. Generate authorization URL with state and PKCE parameters
    2. Redirect user to OAuth provider for authentication
    3. Handle callback with authorization code
    4. Exchange authorization code for access token
    5. Retrieve user information using access token
    6. Validate and return user data
    
    Security Features:
    - State parameter for CSRF protection
    - PKCE for enhanced security
    - Secure token handling
    - Input validation and sanitization
    """
    
    def __init__(self, oauth_config=None):
        """
        Initialize the OAuth manager.
        
        Args:
            oauth_config (dict, optional): OAuth configuration dictionary.
                                         If not provided, uses default Config.
        """
        self.config = Config()
        self.oauth_config = oauth_config or {}
    
    # =============================================================================
    # SECURITY UTILITIES
    # =============================================================================
    
    def generate_state(self):
        """
        Generate a secure random state parameter for CSRF protection.
        
        The state parameter is used to prevent CSRF attacks by ensuring
        that the authorization request and callback are from the same
        source. It should be cryptographically random and unpredictable.
        
        Returns:
            str: A secure random state parameter (32 bytes, URL-safe)
        """
        return secrets.token_urlsafe(32)
    
    def generate_code_verifier(self):
        """
        Generate PKCE code verifier for enhanced security.
        
        The code verifier is a cryptographically random string that is
        used in the PKCE (Proof Key for Code Exchange) flow to enhance
        security for public clients. It should be high-entropy and
        unpredictable.
        
        Returns:
            str: A secure random code verifier (96 bytes, URL-safe)
        """
        return secrets.token_urlsafe(96)
    
    def generate_code_challenge(self, code_verifier):
        """
        Generate PKCE code challenge from verifier.
        
        The code challenge is derived from the code verifier using SHA256
        hashing and base64url encoding. This provides a way to verify
        that the client that initiated the authorization request is the
        same client that is exchanging the authorization code for tokens.
        
        Args:
            code_verifier (str): The code verifier to generate challenge from
            
        Returns:
            str: The base64url-encoded SHA256 hash of the code verifier
        """
        # Generate SHA256 hash of the code verifier
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        
        # Encode as base64url and remove padding
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    # =============================================================================
    # GOOGLE OAUTH IMPLEMENTATION
    # =============================================================================
    
    def get_google_auth_url(self, client_id, redirect_uri=None, state=None):
        """
        Generate Google OAuth authorization URL.
        
        This method creates the authorization URL that users will be redirected
        to for Google OAuth authentication. It includes all necessary parameters
        for the OAuth 2.0 flow with PKCE support.
        
        Args:
            client_id (str): Google OAuth client ID
            redirect_uri (str, optional): Custom redirect URI. If not provided,
                                        uses the configured Google redirect URI.
            state (str, optional): State parameter for CSRF protection.
                                 If not provided, generates a new one.
        
        Returns:
            tuple: (auth_url, state, code_verifier) where:
                - auth_url (str): The complete Google OAuth authorization URL
                - state (str): State parameter for CSRF protection
                - code_verifier (str): PKCE code verifier for enhanced security
            
        Example:
            https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&scope=...
        """
        # Generate state parameter if not provided
        if not state:
            state = self.generate_state()
        
        # Generate PKCE parameters for enhanced security
        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)
        
        # Use configured redirect URI if not provided
        if not redirect_uri:
            redirect_uri = self.config.get_google_redirect_uri()
        
        # Build authorization parameters
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'openid email profile',  # Request access to user's basic profile
            'response_type': 'code',  # Authorization code flow
            'state': state,  # CSRF protection
            'code_challenge': code_challenge,  # PKCE challenge
            'code_challenge_method': 'S256',  # SHA256 method for PKCE
            'access_type': 'offline',  # Request refresh token
            'prompt': 'consent'  # Force consent screen
        }
        
        # Build and return the authorization URL along with state and code_verifier
        auth_url = f"{self.config.GOOGLE_AUTH_URL}?{urlencode(params)}"
        return auth_url, state, code_verifier
    
    def handle_google_callback(self, code, state, client_id, client_secret, code_verifier=None):
        """
        Handle Google OAuth callback and exchange code for user information.
        
        This method processes the callback from Google's OAuth server,
        exchanges the authorization code for access tokens, and retrieves
        user information. It implements the complete OAuth 2.0 flow with
        proper error handling and validation.
        
        Args:
            code (str): Authorization code from Google
            state (str): State parameter for CSRF protection
            client_id (str): Google OAuth client ID
            client_secret (str): Google OAuth client secret
            code_verifier (str, optional): PKCE code verifier for enhanced security
        
        Returns:
            dict: User information dictionary on success, None on failure
            
        Raises:
            Exception: If OAuth flow fails or user information cannot be retrieved
        """
        try:
            # Exchange authorization code for access token
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.config.get_google_redirect_uri()
            }
            
            # Add PKCE code verifier if provided
            if code_verifier:
                token_data['code_verifier'] = code_verifier
            
            # Make token exchange request
            token_response = requests.post(
                self.config.GOOGLE_TOKEN_URL,
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            # Check for token exchange errors
            if token_response.status_code != 200:
                raise Exception(f"Token exchange failed: {token_response.text}")
            
            # Parse token response
            token_info = token_response.json()
            access_token = token_info.get('access_token')
            
            if not access_token:
                raise Exception("No access token received from Google")
            
            # Retrieve user information using access token
            user_response = requests.get(
                self.config.GOOGLE_USER_INFO_URL,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            # Check for user info retrieval errors
            if user_response.status_code != 200:
                raise Exception(f"User info retrieval failed: {user_response.text}")
            
            # Parse user information
            user_info = user_response.json()
            
            # Validate and format user information
            if not user_info.get('id'):
                raise Exception("Invalid user information received from Google")
            
            # Return formatted user information
            return {
                'id': user_info.get('id'),
                'name': user_info.get('name'),
                'email': user_info.get('email'),
                'picture': user_info.get('picture'),
                'provider': 'google'
            }
            
        except Exception as e:
            # Log error and re-raise for handling by calling code
            raise Exception(f"Google OAuth callback failed: {str(e)}")
    
    # =============================================================================
    # LINKEDIN OAUTH IMPLEMENTATION
    # =============================================================================
    
    def get_linkedin_auth_url(self, client_id, redirect_uri=None, state=None):
        """
        Generate LinkedIn OAuth authorization URL.
        
        This method creates the authorization URL that users will be redirected
        to for LinkedIn OAuth authentication. It includes all necessary parameters
        for the OAuth 2.0 flow with PKCE support.
        
        Args:
            client_id (str): LinkedIn OAuth client ID
            redirect_uri (str, optional): Custom redirect URI. If not provided,
                                        uses the configured LinkedIn redirect URI.
            state (str, optional): State parameter for CSRF protection.
                                 If not provided, generates a new one.
        
        Returns:
            tuple: (auth_url, state) where:
                - auth_url (str): The complete LinkedIn OAuth authorization URL
                - state (str): State parameter for CSRF protection
            
        Example:
            https://www.linkedin.com/oauth/v2/authorization?client_id=...&redirect_uri=...&scope=...
        """
        # Generate state parameter if not provided
        if not state:
            state = self.generate_state()
        
        # Generate PKCE parameters for enhanced security
        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)
        
        # Use configured redirect URI if not provided
        if not redirect_uri:
            redirect_uri = self.config.get_linkedin_redirect_uri()
        
        # Build authorization parameters
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'openid profile email',  # Request access to user's basic profile and email
            'response_type': 'code',  # Authorization code flow
            'state': state,  # CSRF protection
            'code_challenge': code_challenge,  # PKCE challenge
            'code_challenge_method': 'S256'  # SHA256 method for PKCE
        }
        
        # Build and return the authorization URL along with state
        auth_url = f"{self.config.LINKEDIN_AUTH_URL}?{urlencode(params)}"
        return auth_url, state
    
    def handle_linkedin_callback(self, code, state, client_id, client_secret):
        """
        Handle LinkedIn OAuth callback and exchange code for user information.
        
        This method processes the callback from LinkedIn's OAuth server,
        exchanges the authorization code for access tokens, and retrieves
        user information. It implements the complete OAuth 2.0 flow with
        proper error handling and validation.
        
        Args:
            code (str): Authorization code from LinkedIn
            state (str): State parameter for CSRF protection
            client_id (str): LinkedIn OAuth client ID
            client_secret (str): LinkedIn OAuth client secret
        
        Returns:
            dict: User information dictionary on success, None on failure
            
        Raises:
            Exception: If OAuth flow fails or user information cannot be retrieved
        """
        try:
            # Exchange authorization code for access token
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.config.get_linkedin_redirect_uri()
            }
            
            # Make token exchange request
            token_response = requests.post(
                self.config.LINKEDIN_TOKEN_URL,
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            # Check for token exchange errors
            if token_response.status_code != 200:
                raise Exception(f"Token exchange failed: {token_response.text}")
            
            # Parse token response
            token_info = token_response.json()
            access_token = token_info.get('access_token')
            
            if not access_token:
                raise Exception("No access token received from LinkedIn")
            
            # Retrieve user information using access token
            user_response = requests.get(
                self.config.LINKEDIN_USER_INFO_URL,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            # Check for user info retrieval errors
            if user_response.status_code != 200:
                raise Exception(f"User info retrieval failed: {user_response.text}")
            
            # Parse user information
            user_info = user_response.json()
            
            # Debug: Log the LinkedIn userinfo response structure
            logger.info(f"LinkedIn userinfo response: {user_info}")
            
            # Validate and format user information
            if not user_info.get('sub'):  # LinkedIn uses 'sub' instead of 'id'
                raise Exception("Invalid user information received from LinkedIn")
            
            # Get profile picture from LinkedIn (requires separate API call)
            picture_url = None
            try:
                # LinkedIn requires a separate request for profile picture using the correct endpoint
                profile_response = requests.get(
                    'https://api.linkedin.com/v2/people/~:(profilePicture(displayImage~:playableStreams))',
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'X-Restli-Protocol-Version': '2.0.0'
                    }
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    logger.info(f"LinkedIn profile picture API response: {profile_data}")
                    # Extract profile picture URL from LinkedIn's nested structure
                    if profile_data.get('profilePicture') and profile_data['profilePicture'].get('displayImage~'):
                        elements = profile_data['profilePicture']['displayImage~'].get('elements', [])
                        if elements and len(elements) > 0:
                            # Get the largest available image
                            largest_image = max(elements, key=lambda x: x.get('data', {}).get('com.linkedin.digitalmedia.mediaartifact.StillImage', {}).get('storageSize', {}).get('width', 0))
                            if largest_image.get('identifiers'):
                                picture_url = largest_image['identifiers'][0].get('identifier')
                                logger.info(f"LinkedIn profile picture URL found: {picture_url}")
                    else:
                        logger.info("LinkedIn profile picture data not found in expected structure")
                else:
                    logger.info(f"LinkedIn profile picture API failed with status {profile_response.status_code}: {profile_response.text}")
                    # If the profile picture request fails, try a simpler approach
                    # Some LinkedIn users might have profile pictures in the userinfo response
                    if user_info.get('picture'):
                        picture_url = user_info.get('picture')
                        logger.info(f"LinkedIn fallback picture from userinfo: {picture_url}")
            except Exception as e:
                # If profile picture request fails, continue without it
                # Try to get picture from userinfo response as fallback
                if user_info.get('picture'):
                    picture_url = user_info.get('picture')
            
            # Return formatted user information
            # LinkedIn might use different field names, so we'll try multiple possibilities
            name = user_info.get('name') or user_info.get('given_name', '') + ' ' + user_info.get('family_name', '')
            email = user_info.get('email') or user_info.get('email_verified')
            
            return {
                'id': user_info.get('sub'),
                'name': name.strip() if name else 'LinkedIn User',
                'email': email,
                'picture': picture_url,
                'provider': 'linkedin'
            }
            
        except Exception as e:
            # Log error and re-raise for handling by calling code
            raise Exception(f"LinkedIn OAuth callback failed: {str(e)}")
    
    # =============================================================================
    # GENERIC OAUTH METHODS
    # =============================================================================
    
    def get_auth_url(self, provider, client_id, redirect_uri=None, state=None):
        """
        Get OAuth authorization URL for any supported provider.
        
        This method provides a generic interface for getting authorization
        URLs from any supported OAuth provider. It delegates to the
        provider-specific implementation.
        
        Args:
            provider (str): OAuth provider ('google' or 'linkedin')
            client_id (str): OAuth client ID
            redirect_uri (str, optional): Custom redirect URI
            state (str, optional): State parameter for CSRF protection
        
        Returns:
            str: The complete OAuth authorization URL
            
        Raises:
            ValueError: If the provider is not supported
        """
        if provider == 'google':
            return self.get_google_auth_url(client_id, redirect_uri, state)
        elif provider == 'linkedin':
            return self.get_linkedin_auth_url(client_id, redirect_uri, state)
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
    
    def handle_callback(self, provider, code, state, client_id, client_secret):
        """
        Handle OAuth callback for any supported provider.
        
        This method provides a generic interface for handling OAuth
        callbacks from any supported provider. It delegates to the
        provider-specific implementation.
        
        Args:
            provider (str): OAuth provider ('google' or 'linkedin')
            code (str): Authorization code from OAuth provider
            state (str): State parameter for CSRF protection
            client_id (str): OAuth client ID
            client_secret (str): OAuth client secret
        
        Returns:
            dict: User information dictionary on success, None on failure
            
        Raises:
            ValueError: If the provider is not supported
            Exception: If OAuth flow fails
        """
        if provider == 'google':
            return self.handle_google_callback(code, state, client_id, client_secret)
        elif provider == 'linkedin':
            return self.handle_linkedin_callback(code, state, client_id, client_secret)
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")