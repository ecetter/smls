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

### Configure Base URL
**Option 1: Environment Variable (Recommended)**
```bash
export BASE_URL=https://yourdomain.com
python scripts/launch.py
```

**Option 2: Direct Command Line**
```bash
python src/app.py --base-url https://yourdomain.com
```

### OAuth App Configuration
- **Google+**: Use redirect URI `https://yourdomain.com/auth/google/callback`
- **LinkedIn**: Use redirect URI `https://yourdomain.com/auth/linkedin/callback`

## Requirements

- Python 3.8+
- Google+ OAuth app
- LinkedIn OAuth app

## License

MIT License