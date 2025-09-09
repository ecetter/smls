# Background Management

This directory contains scripts to run SMLS in the background.

## Usage

```bash
# Start SMLS in background
./persist/manage.sh start

# Check status
./persist/manage.sh status

# View logs
./persist/manage.sh logs

# Stop SMLS
./persist/manage.sh stop

# Restart SMLS
./persist/manage.sh restart
```

## Files

- **`manage.sh`** - Main management script
- **`run_background.sh`** - Background service manager
- **`logs/smls_background.log`** - Application logs

## Notes

- SMLS runs in background and survives logout
- All logs are stored in `logs/` directory
- No root privileges required