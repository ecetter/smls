# Social Media Login Service (SMLS)

A secure OAuth 2.0 authentication service supporting Google+ and LinkedIn login.

## Quick Start

### 1. Setup
```bash
python scripts/setup.py
```

### 2. Launch
```bash
python scripts/launch.py
```

### 3. Configure OAuth
1. Visit the setup page (URL shown after launch)
2. Enter your Google+ and LinkedIn OAuth credentials
3. Use the provided redirect URIs in your OAuth apps

## Deployment

### Option 1: Direct Flask (Development)
**Environment Variable (Recommended)**
```bash
export BASE_URL=https://yourdomain.com
python scripts/launch.py
```

**Direct Command Line**
```bash
python src/app.py --base-url https://yourdomain.com
```

### Option 2: Nginx Reverse Proxy (Production)
For clean URLs without port numbers, use the nginx configuration:

```bash
# Set your desired URL
export BASE_URL='http://yourdomain.com/your/path'

# Setup nginx reverse proxy
./nginx/setup-nginx.sh

# Start SMLS with nginx
./nginx/start-with-nginx.sh
```

This will make SMLS available at your BASE_URL instead of requiring port numbers.

Examples:
- `export BASE_URL='http://emeryetter.com/sweng861/smls'`
- `export BASE_URL='https://mydomain.com/app'`
- `export BASE_URL='http://localhost/myapp'`

See `nginx/NGINX-SETUP.md` for detailed nginx setup instructions.

### OAuth App Configuration
- **Google+**: Use redirect URI `{BASE_URL}/auth/google/callback`
- **LinkedIn**: Use redirect URI `{BASE_URL}/auth/linkedin/callback`

Examples:
- If BASE_URL is `http://emeryetter.com/sweng861/smls`:
  - Google: `http://emeryetter.com/sweng861/smls/auth/google/callback`
  - LinkedIn: `http://emeryetter.com/sweng861/smls/auth/linkedin/callback`

## Requirements

- Python 3.8+
- Google+ OAuth app
- LinkedIn OAuth app

## License

MIT License