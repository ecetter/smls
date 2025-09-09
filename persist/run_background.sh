#!/bin/bash
# Background service script for SMLS Flask application
# This script allows you to run the Flask app in the background and manage it

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go up one directory to the main SMLS directory
APP_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$SCRIPT_DIR/smls.pid"
LOG_FILE="$SCRIPT_DIR/logs/smls_background.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[SMLS]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SMLS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[SMLS]${NC} $1"
}

print_error() {
    echo -e "${RED}[SMLS]${NC} $1"
}

# Function to check if the app is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the app
start_app() {
    if is_running; then
        print_warning "SMLS is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    print_status "Starting SMLS in background..."
    
    # Create logs directory if it doesn't exist
    mkdir -p "$SCRIPT_DIR/logs"
    
    # Change to the app directory
    cd "$APP_DIR"
    
    # Start the app in background and save PID
    nohup python3 scripts/launch.py > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    # Wait a moment to check if it started successfully
    sleep 2
    
    if is_running; then
        print_success "SMLS started successfully (PID: $pid)"
        print_status "Logs: $LOG_FILE"
        print_status "Access your app at the URL shown in the logs"
        return 0
    else
        print_error "Failed to start SMLS"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the app
stop_app() {
    if ! is_running; then
        print_warning "SMLS is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    print_status "Stopping SMLS (PID: $pid)..."
    
    # Try graceful shutdown first
    kill "$pid" 2>/dev/null
    
    # Wait for graceful shutdown
    local count=0
    while [ $count -lt 10 ] && is_running; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if is_running; then
        print_warning "Graceful shutdown failed, forcing stop..."
        kill -9 "$pid" 2>/dev/null
        sleep 1
    fi
    
    if ! is_running; then
        print_success "SMLS stopped successfully"
        rm -f "$PID_FILE"
        return 0
    else
        print_error "Failed to stop SMLS"
        return 1
    fi
}

# Function to show status
show_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_success "SMLS is running (PID: $pid)"
        
        # Show recent log entries
        if [ -f "$LOG_FILE" ]; then
            print_status "Recent log entries:"
            tail -n 5 "$LOG_FILE" | sed 's/^/  /'
        fi
    else
        print_warning "SMLS is not running"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Showing SMLS logs (press Ctrl+C to exit):"
        tail -f "$LOG_FILE"
    else
        print_warning "No log file found at $LOG_FILE"
    fi
}

# Function to restart the app
restart_app() {
    print_status "Restarting SMLS..."
    stop_app
    sleep 2
    start_app
}

# Function to show help
show_help() {
    echo "SMLS Background Service Manager"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs|help}"
    echo ""
    echo "Commands:"
    echo "  start   - Start SMLS in background"
    echo "  stop    - Stop SMLS"
    echo "  restart - Restart SMLS"
    echo "  status  - Show SMLS status"
    echo "  logs    - Show live logs"
    echo "  help    - Show this help message"
    echo ""
    echo "Files:"
    echo "  PID file: $PID_FILE"
    echo "  Log file: $LOG_FILE"
}

# Main script logic
case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Invalid command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
