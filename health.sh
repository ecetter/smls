#!/bin/bash

# SMLS Health Management Script
# Simple interface for health monitoring commands

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if command is provided
if [ $# -eq 0 ]; then
    echo "SMLS Health Monitor"
    echo "====================="
    echo ""
    echo "Usage: $0 {start|status|check}"
    echo ""
    echo "Commands:"
    echo "  start   - Start continuous health monitoring"
    echo "  status  - Show current health status"
    echo "  check   - Perform single health check"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start monitoring in background"
    echo "  $0 status   # Check current status"
    echo "  $0 check    # Single health check"
    exit 1
fi

# Forward command to health monitor
exec "$SCRIPT_DIR/production/health_monitor.sh" "$@"
