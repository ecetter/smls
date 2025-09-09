# Configuration Reference

## Environment Variables

### Required
```bash
export BASE_URL='http://yourdomain.com/yourpath'
```

### Optional
```bash
export SECRET_KEY='your-secret-key'
export FLASK_ENV='production'
export FLASK_DEBUG='False'
```

## OAuth Configuration

### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://yourdomain.com/yourpath/auth/google/callback`

### LinkedIn OAuth
1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Create a new app
3. Add OAuth 2.0 redirect URL: `http://yourdomain.com/yourpath/auth/linkedin/callback`
4. Note your Client ID and Client Secret

## Gunicorn Configuration

### Default Settings
- **Workers**: 4 processes
- **Worker Class**: sync
- **Timeout**: 30 seconds
- **Max Requests**: 1000
- **Bind**: 0.0.0.0:5000

### Customization
Edit `config/gunicorn.conf.py` to modify:
- Worker count
- Timeout values
- Log levels
- Security settings

## Security Configuration

### Session Settings
- **Type**: filesystem
- **Timeout**: 1 hour
- **Secure**: HTTPS only
- **HTTPOnly**: XSS protection
- **SameSite**: CSRF protection

### Security Headers
- **X-Content-Type-Options**: nosniff
- **X-Frame-Options**: DENY
- **X-XSS-Protection**: 1; mode=block
- **Strict-Transport-Security**: max-age=31536000
- **Content-Security-Policy**: Restrictive policy

## Nginx Configuration

### Basic Setup
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /yourpath/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL Configuration
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location /yourpath/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Health Monitoring

### Health Check Endpoint
- **URL**: `/health`
- **Method**: GET
- **Response**: JSON with status information

### Monitoring Configuration
- **Check Interval**: 60 seconds
- **Timeout**: 10 seconds
- **Max Failures**: 3 before restart
- **Recovery**: Automatic restart on failure

## Log Configuration

### Log Levels
- **Access Log**: INFO level
- **Error Log**: INFO level
- **Health Log**: INFO level

### Log Rotation
- **Access Log**: Rotate daily
- **Error Log**: Rotate daily
- **Health Log**: Rotate daily

## Performance Tuning

### Worker Configuration
```python
# For CPU-bound applications
workers = multiprocessing.cpu_count() * 2 + 1

# For I/O-bound applications
worker_class = "gevent"
worker_connections = 1000
```

### Memory Management
```python
# Restart workers after requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50
```

### Connection Handling
```python
# Keep connections alive for better performance
keepalive = 2
backlog = 2048
```
