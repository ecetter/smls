# Nginx Configuration

This directory contains nginx configuration files for SMLS.

## Files

- **`nginx-smls.conf`** - Configuration template
- **`nginx-smls-generated.conf`** - Generated configuration (created by setup script)
- **`start-user-nginx.sh`** - Start nginx in user mode
- **`stop-user-nginx.sh`** - Stop nginx
- **`status-user-nginx.sh`** - Check nginx status

## Usage

Use the main setup script instead of these files directly:

```bash
export BASE_URL='http://yourdomain.com/your/path'
./setup-and-launch.sh
```