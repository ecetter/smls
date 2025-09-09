# Nginx Configuration for SMLS

This directory contains all nginx-related files for setting up SMLS with a reverse proxy configuration.

## Purpose

The nginx configuration allows SMLS to be accessed at a clean URL without port numbers:
- **Before**: `http://yourdomain.com:8080/your/path`
- **After**: `http://yourdomain.com/your/path`

## Files

- **`nginx-smls.conf`** - Generic nginx configuration template
- **`setup-nginx.sh`** - Automated nginx setup script
- **`start-with-nginx.sh`** - Script to start SMLS with nginx configuration
- **`NGINX-SETUP.md`** - Comprehensive setup and troubleshooting guide
- **`README.md`** - This file

## Quick Start

### 1. Set Your BASE_URL

```bash
# Examples:
export BASE_URL='http://yourdomain.com/your/path'
export BASE_URL='http://emeryetter.com/sweng861/smls'
export BASE_URL='https://mydomain.com/app'
```

### 2. Setup and Start

From the main SMLS directory:

```bash
# Configure nginx
./nginx/setup-nginx.sh

# Start SMLS with nginx configuration
./nginx/start-with-nginx.sh
```

Or from within this directory:

```bash
# Configure nginx
./setup-nginx.sh

# Start SMLS with nginx configuration
./start-with-nginx.sh
```

## How It Works

1. **BASE_URL Parsing**: Scripts extract domain and path from your BASE_URL
2. **Template Generation**: The nginx template is customized with your values
3. **Nginx Configuration**: nginx listens on port 80 for your domain
4. **Request Forwarding**: Requests to your path are forwarded to Flask on `localhost:8080`
5. **Path Removal**: The path prefix is removed before forwarding to Flask
6. **OAuth Callbacks**: Work with the clean URL

## Configuration Examples

### Simple Domain
```bash
export BASE_URL='http://mydomain.com'
# Result: SMLS available at http://mydomain.com
```

### Domain with Path
```bash
export BASE_URL='http://emeryetter.com/sweng861/smls'
# Result: SMLS available at http://emeryetter.com/sweng861/smls
```

### HTTPS with Path
```bash
export BASE_URL='https://secure.example.com/myapp'
# Result: SMLS available at https://secure.example.com/myapp
```

## OAuth Configuration

Update your OAuth app settings to use your BASE_URL:

### Google OAuth
- **Authorized JavaScript origins**: `http://yourdomain.com` (or `https://yourdomain.com`)
- **Authorized redirect URIs**: `{BASE_URL}/auth/google/callback`

### LinkedIn OAuth
- **Authorized redirect URLs**: `{BASE_URL}/auth/linkedin/callback`

### Example
If BASE_URL is `http://emeryetter.com/sweng861/smls`:
- Google: `http://emeryetter.com/sweng861/smls/auth/google/callback`
- LinkedIn: `http://emeryetter.com/sweng861/smls/auth/linkedin/callback`

## Management

Once set up, use the main SMLS management commands:

```bash
# From main SMLS directory
./persist/manage.sh start    # Start SMLS
./persist/manage.sh status   # Check status
./persist/manage.sh logs     # View logs
./persist/manage.sh stop     # Stop SMLS
```

## Troubleshooting

See `NGINX-SETUP.md` for detailed troubleshooting information.

## Notes

- All scripts automatically detect their location and work from any directory
- The nginx configuration is generated dynamically from your BASE_URL
- No hard-coded domains or paths - everything is configurable
- nginx setup requires sudo privileges for configuration file management
- Use the same BASE_URL for both setup and start scripts