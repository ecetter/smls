import requests
import secrets
import hashlib
import base64
from urllib.parse import urlencode, parse_qs
from config import Config

class OAuthManager:
    """Handles OAuth 2.0 3-legged authorization flow for Google and LinkedIn."""
    
    def __init__(self, oauth_config=None):
        self.config = Config()
        self.oauth_config = oauth_config or {}
    
    def generate_state(self):
        """Generate a secure random state parameter for CSRF protection."""
        return secrets.token_urlsafe(32)
    
    def generate_code_verifier(self):
        """Generate PKCE code verifier for enhanced security."""
        return secrets.token_urlsafe(96)
    
    def generate_code_challenge(self, code_verifier):
        """Generate PKCE code challenge from verifier."""
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    def get_google_auth_url(self, client_id, redirect_uri=None, state=None):
        """Generate Google OAuth authorization URL."""
        if not state:
            state = self.generate_state()
        
        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)
        
        if not redirect_uri:
            redirect_uri = self.config.get_google_redirect_uri()
        
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        return f"{self.config.GOOGLE_AUTH_URL}?{urlencode(params)}", state, code_verifier
    
    def get_linkedin_auth_url(self, client_id, redirect_uri=None, state=None):
        """Generate LinkedIn OAuth authorization URL."""
        if not state:
            state = self.generate_state()
        
        if not redirect_uri:
            redirect_uri = self.config.get_linkedin_redirect_uri()
        
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'state': state,
            'scope': 'openid profile email'
        }
        
        return f"{self.config.LINKEDIN_AUTH_URL}?{urlencode(params)}", state
    
    def exchange_google_code(self, code, code_verifier, client_id, client_secret, redirect_uri=None):
        """Exchange authorization code for access token (Google)."""
        if not redirect_uri:
            redirect_uri = self.config.get_google_redirect_uri()
            
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code_verifier': code_verifier
        }
        
        response = requests.post(self.config.GOOGLE_TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()
    
    def exchange_linkedin_code(self, code, client_id, client_secret, redirect_uri=None):
        """Exchange authorization code for access token (LinkedIn)."""
        if not redirect_uri:
            redirect_uri = self.config.get_linkedin_redirect_uri()
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(self.config.LINKEDIN_TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_google_user_info(self, access_token):
        """Get user information from Google API."""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(self.config.GOOGLE_USER_INFO_URL, headers=headers)
        response.raise_for_status()
        user_data = response.json()
        
        # Debug: Print what Google API returns
        print(f"DEBUG: Google API response: {user_data}")
        
        return user_data
    
    def get_linkedin_user_info(self, access_token):
        """Get user information from LinkedIn API."""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        # Use the new LinkedIn userinfo endpoint
        response = requests.get(self.config.LINKEDIN_USER_INFO_URL, headers=headers)
        response.raise_for_status()
        user_data = response.json()
        
        # Debug: Print what LinkedIn API returns
        print(f"DEBUG: LinkedIn API response: {user_data}")
        
        # Map the response to our expected format
        # LinkedIn might return picture in different fields or formats
        picture_url = user_data.get('picture', '')
        
        # Try alternative field names if picture is empty
        if not picture_url:
            picture_url = user_data.get('picture_url', '')
        if not picture_url:
            picture_url = user_data.get('profile_picture', '')
        if not picture_url:
            picture_url = user_data.get('profilePicture', '')
        if not picture_url:
            picture_url = user_data.get('pictureUrl', '')
        if not picture_url:
            picture_url = user_data.get('avatar', '')
        if not picture_url:
            picture_url = user_data.get('avatar_url', '')
        if not picture_url:
            picture_url = user_data.get('photo', '')
        if not picture_url:
            picture_url = user_data.get('photo_url', '')
        
        # If picture is still empty, try to construct from other fields
        if not picture_url and user_data.get('sub'):
            # LinkedIn might require a separate API call for profile picture
            # For now, we'll leave it empty and log this
            print(f"DEBUG: No picture URL found in LinkedIn response. Available fields: {list(user_data.keys())}")
        
        user_info = {
            'id': user_data.get('sub'),  # LinkedIn uses 'sub' for user ID
            'name': user_data.get('name', ''),
            'email': user_data.get('email', ''),
            'picture': picture_url,
            'first_name': user_data.get('given_name', ''),
            'last_name': user_data.get('family_name', '')
        }
        
        # If we still don't have a picture, try the LinkedIn People API
        if not picture_url and user_data.get('sub'):
            try:
                print("DEBUG: Attempting to get profile picture from LinkedIn People API")
                people_response = requests.get(
                    'https://api.linkedin.com/v2/people/~:(id,profilePicture(displayImage~:playableStreams))',
                    headers=headers
                )
                if people_response.status_code == 200:
                    people_data = people_response.json()
                    print(f"DEBUG: LinkedIn People API response: {people_data}")
                    
                    # Extract picture URL from the complex LinkedIn response
                    profile_picture = people_data.get('profilePicture', {})
                    display_image = profile_picture.get('displayImage~', {})
                    elements = display_image.get('elements', [])
                    
                    if elements:
                        # Get the largest available image
                        largest_element = max(elements, key=lambda x: x.get('data', {}).get('com.linkedin.digitalmedia.mediaartifact.StillImage', {}).get('storageSize', {}).get('width', 0))
                        identifiers = largest_element.get('identifiers', [])
                        if identifiers:
                            picture_url = identifiers[0].get('identifier')
                            print(f"DEBUG: Found LinkedIn picture URL from People API: {picture_url}")
                            
            except Exception as e:
                print(f"DEBUG: LinkedIn People API call failed: {e}")
        
        # Update the user_info with the final picture URL
        user_info['picture'] = picture_url
        
        return user_info
