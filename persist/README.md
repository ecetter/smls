# SMLS Persistence Management

This directory contains scripts to run the SMLS Flask application in the background, allowing it to continue running even after you log out of the server.

## Purpose

The scripts in this directory provide:
- **Background execution**: Run SMLS without keeping a terminal session open
- **Process persistence**: Application continues running after logout
- **Process management**: Easy start, stop, restart, and status checking
- **Logging**: All output captured to log files

## Files

- **`manage.sh`** - Simple management interface (recommended for daily use)
- **`run_background.sh`** - Full-featured background service manager
- **`smls.pid`** - Process ID file (created when app is running)
- **`logs/smls_background.log`** - Application logs (created when app starts)

## Quick Start

```bash
# Start SMLS in background
./manage.sh start

# Check if it's running
./manage.sh status

# View live logs
./manage.sh logs

# Stop SMLS
./manage.sh stop
```

## Commands

### Using `manage.sh` (Recommended)

```bash
./manage.sh start    # Start SMLS in background (survives logout)
./manage.sh stop     # Stop SMLS
./manage.sh restart  # Restart SMLS
./manage.sh status   # Check if SMLS is running
./manage.sh logs     # View live logs
```

### Using `run_background.sh` (Advanced)

```bash
./run_background.sh start    # Start SMLS in background
./run_background.sh stop     # Stop SMLS
./run_background.sh restart  # Restart SMLS
./run_background.sh status   # Show detailed status
./run_background.sh logs     # View live logs
./run_background.sh help     # Show detailed help
```

## Workflow

1. **Start the application**:
   ```bash
   ./manage.sh start
   ```

2. **Verify it's running**:
   ```bash
   ./manage.sh status
   ```

3. **Log out of the server** - SMLS will continue running!

4. **When you return, check status**:
   ```bash
   ./manage.sh status
   ```

5. **View logs if needed**:
   ```bash
   ./manage.sh logs
   ```

6. **Stop when finished**:
   ```bash
   ./manage.sh stop
   ```

## Features

- ✅ **Survives logout**: Uses `nohup` to run in background
- ✅ **Process tracking**: Maintains PID file for process management
- ✅ **Comprehensive logging**: All output saved to log files
- ✅ **Graceful shutdown**: Attempts graceful stop before force kill
- ✅ **Status monitoring**: Easy way to check if app is running
- ✅ **User-level**: No root privileges required
- ✅ **Error handling**: Proper error messages and status reporting

## Troubleshooting

### App won't start
- Check if another instance is already running: `./manage.sh status`
- Check logs for errors: `./manage.sh logs`
- Ensure Python and dependencies are installed

### App stops unexpectedly
- Check logs for error messages: `./manage.sh logs`
- Verify the Flask app is properly configured
- Check if the port is available

### Can't stop the app
- Try: `./manage.sh stop`
- If that fails, manually kill the process:
  ```bash
  cat smls.pid | xargs kill
  rm -f smls.pid
  ```

## Notes

- The application runs from the parent directory (main SMLS directory)
- All logs are stored in `logs/smls_background.log`
- The process ID is stored in `smls.pid`
- No root privileges are required for any operations
