# SMLS Production Deployment Guide

## Production-Ready Features

This SMLS deployment includes production-grade features for long-term stability and security:

### Stability Features
- **Gunicorn WSGI Server**: Production-grade server with multiple worker processes
- **Automatic Worker Restarts**: Prevents memory leaks by restarting workers after 1000 requests
- **Health Monitoring**: Continuous health checks with auto-recovery
- **Graceful Shutdown**: Proper signal handling for clean restarts
- **Process Management**: Robust process lifecycle management

### Security Features
- **Security Headers**: XSS, CSRF, and clickjacking protection
- **Session Security**: Secure cookies with HTTP-only and SameSite protection
- **HTTPS Enforcement**: Strict Transport Security headers
- **Content Security Policy**: XSS attack prevention
- **Input Validation**: Request size limits and validation
- **Health Endpoint**: Monitoring without exposing sensitive data

### Monitoring Features
- **Real-time Monitoring**: Live dashboard with process status
- **Comprehensive Logging**: Access, error, and health check logs
- **Resource Monitoring**: Memory and CPU usage tracking
- **Auto-recovery**: Automatic restart on failures
- **Status Reporting**: Detailed status information

## Quick Start

### Setup and Launch
```bash
export BASE_URL='http://yourdomain.com/yourpath'
./setup.sh
```

### Management Commands
```bash
# Check status
./manage.sh status

# View logs
./manage.sh logs error

# Monitor in real-time
./manage.sh monitor

# Health check
./health.sh status

# Stop/restart
./manage.sh stop
./manage.sh start
```

## Production Configuration

### Gunicorn Configuration (`config/gunicorn.conf.py`)
- **Workers**: 4 processes (or CPU cores × 2 + 1)
- **Worker Class**: Synchronous workers for stability
- **Timeout**: 30 seconds
- **Max Requests**: 1000 (prevents memory leaks)
- **Logging**: Comprehensive access and error logs
- **Security**: Request size limits and field limits

### WSGI Application (`config/wsgi.py`)
- **Security Headers**: Automatically applied to all responses
- **Health Endpoint**: `/health` for monitoring
- **Production Settings**: Optimized for production use
- **Error Handling**: Proper error responses

### Process Management (`production/production_manager.sh`)
- **Graceful Shutdown**: SIGTERM → SIGKILL fallback
- **PID Management**: Proper process tracking
- **Log Rotation**: Automatic log management
- **Status Monitoring**: Comprehensive status reporting

### Health Monitoring (`production/health_monitor.sh`)
- **Continuous Monitoring**: 60-second intervals
- **Auto-recovery**: Restart after 3 consecutive failures
- **Health Checks**: HTTP endpoint validation
- **Logging**: All health check activities logged

## Security Configuration

### Environment Variables
```bash
# Set these in your deployment
export SECRET_KEY='your-very-secure-secret-key-here'
export FLASK_ENV='production'
export FLASK_DEBUG='False'
```

### Security Headers Applied
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'`

### Session Security
- Secure cookies (HTTPS only)
- HTTP-only cookies (XSS protection)
- SameSite protection (CSRF protection)
- 1-hour session timeout

## Monitoring and Logs

### Log Files
- **Access Log**: `persist/logs/gunicorn_access.log`
- **Error Log**: `persist/logs/gunicorn_error.log`
- **Health Log**: `persist/logs/health_check.log`
- **Startup Log**: `persist/logs/gunicorn_startup.log`

### Monitoring Commands
```bash
# Real-time monitoring dashboard
./manage.sh monitor

# Health status
./health.sh status

# View recent errors
./manage.sh logs error

# View access logs
./manage.sh logs access
```

## Maintenance

### Regular Tasks
1. **Monitor Logs**: Check for errors and unusual activity
2. **Health Checks**: Verify application is responding
3. **Resource Usage**: Monitor memory and CPU usage
4. **Security Updates**: Keep dependencies updated
5. **Backup Configuration**: Backup your configuration files

### Troubleshooting
```bash
# Check if process is running
./manage.sh status

# View startup logs
./manage.sh logs startup

# Restart if needed
./manage.sh restart

# Health check
./health.sh check
```

## Emergency Procedures

### Application Not Responding
1. Check status: `./manage.sh status`
2. View error logs: `./manage.sh logs error`
3. Restart: `./manage.sh restart`
4. Monitor: `./manage.sh monitor`

### High Memory Usage
1. Check worker processes: `ps aux | grep gunicorn`
2. Restart workers: `./manage.sh restart`
3. Monitor memory: `./manage.sh monitor`

### Security Incident
1. Stop application: `./manage.sh stop`
2. Check logs for suspicious activity
3. Update security configuration
4. Restart with new configuration

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

## Security Best Practices

1. **Regular Updates**: Keep all dependencies updated
2. **Secret Management**: Use secure secret keys
3. **Access Control**: Limit server access
4. **Monitoring**: Monitor for suspicious activity
5. **Backups**: Regular configuration backups
6. **Logging**: Comprehensive audit logging
7. **Network Security**: Use firewalls and VPNs
8. **HTTPS**: Always use HTTPS in production

## Support

For issues or questions:
1. Check the logs first
2. Use the monitoring tools
3. Review this documentation
4. Check the health status
5. Restart if necessary

---

**SMLS is now production-ready with enterprise-grade stability and security.**