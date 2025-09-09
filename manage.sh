#!/bin/bash

# SMLS Management Script
# Simple interface for production management commands

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if command is provided
if [ $# -eq 0 ]; then
    echo "SMLS Management"
    echo "=================="
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs|monitor|health}"
    echo ""
    echo "Commands:"
    echo "  start    - Start SMLS in production mode"
    echo "  stop     - Stop SMLS gracefully"
    echo "  restart  - Restart SMLS"
    echo "  status   - Show SMLS status and health"
    echo "  logs     - Show logs (access|error|health)"
    echo "  monitor  - Real-time monitoring dashboard"
    echo "  health   - Health check status"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs error"
    echo "  $0 monitor"
    exit 1
fi

# Forward command to production manager
exec "$SCRIPT_DIR/production/production_manager.sh" "$@"
