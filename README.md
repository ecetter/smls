# SMLS - Social Media Login Service

Production-ready OAuth 2.0 authentication service with Google and LinkedIn integration.

## Quick Start

```bash
export BASE_URL='http://yourdomain.com/yourpath'
./setup.sh
```

## Management

```bash
./manage.sh status    # Check status
./manage.sh logs      # View logs
./health.sh status    # Health check
```

## Project Structure

```
smls/
├── setup.sh              # Main setup script
├── manage.sh             # Production management
├── health.sh             # Health monitoring
├── requirements.txt      # Python dependencies
├── src/                  # Application source
│   ├── app.py           # Main Flask application
│   └── auth/            # OAuth modules
├── config/              # Configuration files
├── production/          # Production tools
├── scripts/             # Setup utilities
├── docs/                # Documentation
├── persist/             # Runtime data
└── nginx/               # Nginx configuration
```

## Configuration

Set your OAuth callback URLs:
- **Google**: `http://yourdomain.com/yourpath/auth/google/callback`
- **LinkedIn**: `http://yourdomain.com/yourpath/auth/linkedin/callback`

## Features

- **Production Ready**: Gunicorn WSGI server with multiple workers
- **Secure**: Comprehensive security headers and session management
- **Monitored**: Health monitoring with auto-recovery
- **Portable**: No root access required
- **Scalable**: Automatic worker restarts and resource management

## Documentation

- [Production Guide](docs/production.md) - Detailed deployment guide
- [Configuration](docs/config.md) - Configuration reference
- [Security](docs/security.md) - Security features and best practices

## Support

For issues or questions, check the logs first:
```bash
./manage.sh logs error
./health.sh status
```