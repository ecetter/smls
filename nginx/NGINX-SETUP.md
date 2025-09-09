# SMLS with Nginx Reverse Proxy Setup

This guide will help you set up SMLS to work with nginx as a reverse proxy, allowing you to access your application at a clean URL without port numbers.

## Overview

The setup uses nginx as a reverse proxy that:
- Listens on port 80 (standard HTTP port)
- Receives requests to your configured URL
- Forwards them to your Flask app running on `localhost:8080`
- Removes the path prefix before forwarding to Flask

## Prerequisites

- nginx installed and running
- SMLS application set up and working
- Your domain pointing to your server

## Quick Setup

### 1. Set Your BASE_URL

First, set the BASE_URL environment variable with your desired URL:

```bash
# Examples:
export BASE_URL='http://yourdomain.com/your/path'
export BASE_URL='http://emeryetter.com/sweng861/smls'
export BASE_URL='https://mydomain.com/app'
export BASE_URL='http://localhost:8080/myapp'
```

### 2. Configure Nginx

Run the nginx setup script with your BASE_URL:

```bash
./setup-nginx.sh
```

This script will:
- Parse your BASE_URL to extract domain and path
- Generate the nginx configuration
- Test the nginx configuration
- Copy the configuration to the appropriate nginx directory
- Enable the site
- Reload nginx

### 3. Start SMLS with Nginx Configuration

```bash
./start-with-nginx.sh
```

This will start SMLS with the same BASE_URL configuration.

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Parse Your BASE_URL

Extract the domain and path from your BASE_URL:
- Domain: everything before the first slash after the protocol
- Path: everything after the domain (including leading slash)

Example: `http://emeryetter.com/sweng861/smls`
- Domain: `emeryetter.com`
- Path: `/sweng861/smls`

### 2. Generate Nginx Configuration

```bash
# Replace DOMAIN and PATH in the template
sed -e "s|DOMAIN|yourdomain.com|g" \
    -e "s|PATH|/your/path|g" \
    nginx-smls.conf > nginx-smls-generated.conf
```

### 3. Copy and Enable Configuration

```bash
# For Ubuntu/Debian
sudo cp nginx-smls-generated.conf /etc/nginx/sites-available/smls
sudo ln -s /etc/nginx/sites-available/smls /etc/nginx/sites-enabled/

# For CentOS/RHEL
sudo cp nginx-smls-generated.conf /etc/nginx/conf.d/smls.conf
```

### 4. Test and Reload Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Start SMLS

```bash
export BASE_URL="http://yourdomain.com/your/path"
./persist/manage.sh start
```

## Configuration Details

### Nginx Configuration Template (`nginx-smls.conf`)

The nginx configuration template uses placeholders:
- `DOMAIN` - Your domain name
- `PATH` - Your application path

The setup script automatically replaces these with values from your BASE_URL.

### SMLS Configuration

When using nginx:
- SMLS runs on `localhost:8080` (internal)
- BASE_URL is set to your desired external URL
- OAuth callbacks use the external URL
- Static files are served through nginx

## Testing the Setup

### 1. Check Nginx Status

```bash
sudo systemctl status nginx
```

### 2. Check SMLS Status

```bash
./persist/manage.sh status
```

### 3. Test the Application

Visit your configured URL (the BASE_URL you set).

You should see the SMLS login page.

### 4. Check Logs

```bash
# SMLS logs
./persist/manage.sh logs

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## OAuth Configuration

When using nginx, update your OAuth app settings to use your BASE_URL:

### Google OAuth
- **Authorized JavaScript origins**: `http://yourdomain.com` (or `https://yourdomain.com`)
- **Authorized redirect URIs**: `{BASE_URL}/auth/google/callback`

### LinkedIn OAuth
- **Authorized redirect URLs**: `{BASE_URL}/auth/linkedin/callback`

### Examples

If your BASE_URL is `http://emeryetter.com/sweng861/smls`:
- Google redirect URI: `http://emeryetter.com/sweng861/smls/auth/google/callback`
- LinkedIn redirect URI: `http://emeryetter.com/sweng861/smls/auth/linkedin/callback`

## Troubleshooting

### Common Issues

#### 1. "502 Bad Gateway" Error
- Check if SMLS is running: `./persist/manage.sh status`
- Check SMLS logs: `./persist/manage.sh logs`
- Verify nginx configuration: `sudo nginx -t`

#### 2. "404 Not Found" Error
- Check if the nginx configuration is active
- Verify the site is enabled: `ls -la /etc/nginx/sites-enabled/`
- Check nginx error logs: `sudo tail -f /var/log/nginx/error.log`
- Verify the path in your BASE_URL matches the nginx configuration

#### 3. OAuth Callback Issues
- Verify OAuth redirect URIs match your BASE_URL exactly
- Check that BASE_URL is set correctly
- Review SMLS logs for OAuth errors

#### 4. Static Files Not Loading
- Check if static files are being served correctly
- Verify the static file paths in nginx configuration
- Check browser developer tools for 404 errors

### Debug Commands

```bash
# Check nginx configuration
sudo nginx -t

# Check nginx status
sudo systemctl status nginx

# Check SMLS status
./persist/manage.sh status

# View SMLS logs
./persist/manage.sh logs

# Check what's running on port 8080
sudo lsof -i :8080

# Check what's running on port 80
sudo lsof -i :80

# Test your specific URL
curl -I http://yourdomain.com/your/path
```

## Security Considerations

### Production Recommendations

1. **Use HTTPS**: Set up SSL certificates and configure HTTPS
2. **Firewall**: Only allow necessary ports (80, 443, 22)
3. **Rate Limiting**: Configure nginx rate limiting
4. **Security Headers**: Add security headers in nginx
5. **Log Monitoring**: Monitor nginx and application logs

### SSL/HTTPS Setup

To enable HTTPS, uncomment and configure the HTTPS section in the generated nginx configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # ... rest of configuration
}
```

## Management Commands

### Start SMLS with Nginx
```bash
export BASE_URL='http://yourdomain.com/your/path'
./start-with-nginx.sh
```

### Stop SMLS
```bash
./persist/manage.sh stop
```

### Restart SMLS
```bash
./persist/manage.sh restart
```

### Check Status
```bash
./persist/manage.sh status
```

### View Logs
```bash
./persist/manage.sh logs
```

## File Structure

```
smls/
├── nginx/                          # Nginx configuration directory
│   ├── nginx-smls.conf            # Nginx configuration template
│   ├── setup-nginx.sh             # Nginx setup script
│   ├── start-with-nginx.sh        # Start SMLS with nginx config
│   ├── NGINX-SETUP.md            # This guide
│   └── README.md                  # Nginx directory overview
├── persist/                        # Background management
│   ├── manage.sh
│   ├── run_background.sh
│   └── README.md
└── ...                            # Other project files
```

## Examples

### Example 1: Simple Domain
```bash
export BASE_URL='http://mydomain.com'
./setup-nginx.sh
./start-with-nginx.sh
```
Result: SMLS available at `http://mydomain.com`

### Example 2: Domain with Path
```bash
export BASE_URL='http://emeryetter.com/sweng861/smls'
./setup-nginx.sh
./start-with-nginx.sh
```
Result: SMLS available at `http://emeryetter.com/sweng861/smls`

### Example 3: HTTPS with Path
```bash
export BASE_URL='https://secure.example.com/myapp'
./setup-nginx.sh
./start-with-nginx.sh
```
Result: SMLS available at `https://secure.example.com/myapp`

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Verify all configuration files are correct
4. Test each component individually
5. Ensure your BASE_URL is consistent across all steps