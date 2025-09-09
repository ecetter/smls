# Production Deployment Guide

## Quick Start

```bash
export BASE_URL='http://yourdomain.com/yourpath'
./setup.sh
```

## Management Commands

### Production Management
```bash
./manage.sh start      # Start SMLS
./manage.sh stop       # Stop SMLS
./manage.sh restart    # Restart SMLS
./manage.sh status     # Show status
./manage.sh logs       # View logs
./manage.sh monitor    # Real-time monitoring
```

### Health Monitoring
```bash
./health.sh start      # Start monitoring
./health.sh status     # Show health status
./health.sh check      # Single health check
```

## Production Features

### Stability
- **Gunicorn WSGI Server**: Multiple worker processes for scalability
- **Automatic Worker Restarts**: Prevents memory leaks (1000 requests)
- **Health Monitoring**: Continuous health checks with auto-recovery
- **Graceful Shutdown**: Proper signal handling for clean restarts

### Security
- **Security Headers**: XSS, CSRF, and clickjacking protection
- **Session Security**: HTTP-only, SameSite cookies
- **HTTPS Enforcement**: Strict Transport Security headers
- **Input Validation**: Request size limits and validation

### Monitoring
- **Real-time Monitoring**: Live dashboard with process status
- **Comprehensive Logging**: Access, error, and health logs
- **Resource Monitoring**: Memory and CPU usage tracking
- **Auto-recovery**: Automatic restart on failures

## Configuration

### Environment Variables
```bash
export BASE_URL='http://yourdomain.com/yourpath'
export SECRET_KEY='your-secret-key'
export FLASK_ENV='production'
```

### Gunicorn Configuration
- **Workers**: 4 processes (or CPU cores × 2 + 1)
- **Timeout**: 30 seconds
- **Max Requests**: 1000 (prevents memory leaks)
- **Logging**: Comprehensive access and error logs

## Logs

- **Access Log**: `persist/logs/gunicorn_access.log`
- **Error Log**: `persist/logs/gunicorn_error.log`
- **Health Log**: `persist/logs/health_check.log`

## Troubleshooting

### Application Not Responding
```bash
./manage.sh status
./manage.sh logs error
./manage.sh restart
```

### Health Issues
```bash
./health.sh check
./health.sh status
```

### View Logs
```bash
./manage.sh logs error    # Error logs
./manage.sh logs access   # Access logs
./manage.sh logs health   # Health logs
```

## Security Best Practices

1. **Regular Updates**: Keep dependencies updated
2. **Secret Management**: Use secure secret keys
3. **Access Control**: Limit server access
4. **Monitoring**: Monitor for suspicious activity
5. **Backups**: Regular configuration backups
6. **HTTPS**: Always use HTTPS in production

## Performance Optimization

### Gunicorn Tuning
- **Workers**: Adjust based on CPU cores
- **Worker Class**: Use `gevent` for I/O-bound applications
- **Timeout**: Increase for slow operations
- **Max Requests**: Adjust based on memory usage

### System Optimization
- **File Descriptors**: Increase system limits
- **Memory**: Monitor and optimize
- **CPU**: Use multiple cores effectively
- **Network**: Optimize connection handling
