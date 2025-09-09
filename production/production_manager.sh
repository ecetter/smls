#!/bin/bash

# =============================================================================
# SMLS Production Process Manager
# =============================================================================
#
# This script provides comprehensive process management for the SMLS application
# running in production mode with Gunicorn. It handles the complete lifecycle
# of the application including startup, shutdown, monitoring, and maintenance.
#
# Key Features:
# - Process lifecycle management (start, stop, restart)
# - Health monitoring and status reporting
# - Log management and rotation
# - Graceful shutdown handling
# - Resource monitoring and reporting
# - Error handling and recovery
#
# Usage:
#   ./production_manager.sh {start|stop|restart|status|logs|monitor}
#
# Author: SMLS Development Team
# Version: 1.0.0
# License: MIT
# =============================================================================

# Exit on any error to ensure script reliability
set -e

# =============================================================================
# CONFIGURATION AND SETUP
# =============================================================================

# Color codes for terminal output
RED='\033[0;31m'      # Error messages and failures
GREEN='\033[0;32m'    # Success messages and confirmations
YELLOW='\033[1;33m'   # Warning messages and cautions
BLUE='\033[0;34m'     # Information messages and status
NC='\033[0m'          # No color (reset)

# Directory and file path configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/persist/smls_gunicorn.pid"
LOG_DIR="$PROJECT_DIR/persist/logs"
ACCESS_LOG="$LOG_DIR/gunicorn_access.log"
ERROR_LOG="$LOG_DIR/gunicorn_error.log"
HEALTH_LOG="$LOG_DIR/health_check.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# =============================================================================
# PROCESS MANAGEMENT FUNCTIONS
# =============================================================================

# Function to check if SMLS process is running
is_running() {
    # Check if the SMLS process is currently running
    # Returns: 0 if process is running, 1 if not running
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is dead - clean up
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start SMLS in production mode
start_smls() {
    # Start the SMLS application in production mode using Gunicorn
    echo -e "${BLUE}Starting SMLS in production mode${NC}"
    
    # Check if already running
    if is_running; then
        echo -e "${YELLOW}SMLS is already running (PID: $(cat "$PID_FILE"))${NC}"
        return 0
    fi
    
    # Create .env file with BASE_URL for WSGI application
    if [ -n "$BASE_URL" ]; then
        echo "BASE_URL=$BASE_URL" > "$PROJECT_DIR/.env"
        echo "FLASK_ENV=production" >> "$PROJECT_DIR/.env"
        echo "FLASK_DEBUG=False" >> "$PROJECT_DIR/.env"
    fi
    
    # Start Gunicorn with production configuration
    cd "$PROJECT_DIR"
    gunicorn -c config/gunicorn.conf.py config.wsgi:application \
        --pid "$PID_FILE" \
        --daemon \
        --log-file "$ERROR_LOG" \
        --access-logfile "$ACCESS_LOG" \
        --log-level info
    
    # Wait for process to start and verify
    sleep 2
    
    if is_running; then
        echo -e "${GREEN}SMLS started successfully (PID: $(cat "$PID_FILE"))${NC}"
        echo -e "${BLUE}Logs:${NC}"
        echo -e "${BLUE}  Access: $ACCESS_LOG${NC}"
        echo -e "${BLUE}  Error: $ERROR_LOG${NC}"
        echo -e "${BLUE}  Health: $HEALTH_LOG${NC}"
        return 0
    else
        echo -e "${RED}Failed to start SMLS${NC}"
        return 1
    fi
}

# Function to stop SMLS gracefully
stop_smls() {
    # Stop the SMLS application gracefully
    echo -e "${BLUE}Stopping SMLS...${NC}"
    
    if ! is_running; then
        echo -e "${YELLOW}SMLS is not running${NC}"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    echo -e "${BLUE}Sending SIGTERM to process $pid...${NC}"
    
    # Send SIGTERM for graceful shutdown
    kill -TERM "$pid"
    
    # Wait for graceful shutdown (up to 30 seconds)
    local count=0
    while [ $count -lt 30 ]; do
        if ! ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}SMLS stopped successfully${NC}"
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if graceful shutdown failed
    echo -e "${YELLOW}Graceful shutdown failed, sending SIGKILL...${NC}"
    kill -KILL "$pid" 2>/dev/null || true
    
    # Wait for process to terminate
    sleep 2
    
    if ! ps -p "$pid" > /dev/null 2>&1; then
        echo -e "${GREEN}SMLS stopped successfully${NC}"
        rm -f "$PID_FILE"
        return 0
    else
        echo -e "${RED}Failed to stop SMLS${NC}"
        return 1
    fi
}

# Function to restart SMLS
restart_smls() {
    # Restart the SMLS application
    echo -e "${BLUE}Restarting SMLS...${NC}"
    
    # Stop current process
    stop_smls
    
    # Wait a moment before restarting
    sleep 2
    
    # Start new process
    start_smls
}

# =============================================================================
# STATUS AND MONITORING FUNCTIONS
# =============================================================================

# Function to show SMLS status
show_status() {
    # Display comprehensive status information for the SMLS application
    echo -e "${BLUE}SMLS Status:${NC}"
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        echo -e "${GREEN}SMLS is running (PID: $pid)${NC}"
        
        # Show process information
        echo -e "${BLUE}Process Info:${NC}"
        if command -v ps > /dev/null 2>&1; then
            ps -p "$pid" -o pid,ppid,etime,pcpu,pmem 2>/dev/null || echo "Process info not available"
        else
            echo "Process info not available"
        fi
        
        # Health check
        echo -e "${BLUE}Health Check:${NC}"
        if command -v curl > /dev/null 2>&1; then
            if curl -s -f "http://localhost:5000/health" > /dev/null 2>&1; then
                echo -e "${GREEN}  Health endpoint responding${NC}"
            else
                echo -e "${RED}  Health endpoint not responding${NC}"
            fi
        else
            echo "  Health check not available (curl not found)"
        fi
        
        # Log file information
        echo -e "${BLUE}Log Files:${NC}"
        if [ -f "$ACCESS_LOG" ]; then
            local size=$(du -h "$ACCESS_LOG" 2>/dev/null | cut -f1 || echo "unknown")
            echo -e "${BLUE}  Access: $size - $ACCESS_LOG${NC}"
        fi
        if [ -f "$ERROR_LOG" ]; then
            local size=$(du -h "$ERROR_LOG" 2>/dev/null | cut -f1 || echo "unknown")
            echo -e "${BLUE}  Error: $size - $ERROR_LOG${NC}"
        fi
        
    else
        echo -e "${RED}SMLS is not running${NC}"
    fi
}

# Function to show logs
show_logs() {
    # Display log information for the SMLS application
    local log_type=${1:-"error"}
    
    case "$log_type" in
        "access")
            if [ -f "$ACCESS_LOG" ]; then
                echo -e "${BLUE}Access Log (last 50 lines):${NC}"
                tail -n 50 "$ACCESS_LOG"
            else
                echo -e "${YELLOW}Access log not found: $ACCESS_LOG${NC}"
            fi
            ;;
        "error")
            if [ -f "$ERROR_LOG" ]; then
                echo -e "${BLUE}Error Log (last 50 lines):${NC}"
                tail -n 50 "$ERROR_LOG"
            else
                echo -e "${YELLOW}Error log not found: $ERROR_LOG${NC}"
            fi
            ;;
        "health")
            if [ -f "$HEALTH_LOG" ]; then
                echo -e "${BLUE}Health Log (last 50 lines):${NC}"
                tail -n 50 "$HEALTH_LOG"
            else
                echo -e "${YELLOW}Health log not found: $HEALTH_LOG${NC}"
            fi
            ;;
        "all")
            echo -e "${BLUE}All Logs (last 20 lines each):${NC}"
            echo -e "${BLUE}=== Access Log ===${NC}"
            [ -f "$ACCESS_LOG" ] && tail -n 20 "$ACCESS_LOG" || echo "Access log not found"
            echo -e "${BLUE}=== Error Log ===${NC}"
            [ -f "$ERROR_LOG" ] && tail -n 20 "$ERROR_LOG" || echo "Error log not found"
            echo -e "${BLUE}=== Health Log ===${NC}"
            [ -f "$HEALTH_LOG" ] && tail -n 20 "$HEALTH_LOG" || echo "Health log not found"
            ;;
        *)
            echo -e "${RED}Invalid log type: $log_type${NC}"
            echo -e "${BLUE}Available types: access, error, health, all${NC}"
            return 1
            ;;
    esac
}

# Function to monitor SMLS in real-time
monitor_smls() {
    # Provide real-time monitoring of the SMLS application
    echo -e "${BLUE}SMLS Real-time Monitor${NC}"
    echo -e "${BLUE}Press Ctrl+C to exit${NC}"
    echo ""
    
    while true; do
        clear
        echo -e "${BLUE}=== SMLS Monitor - $(date) ===${NC}"
        echo ""
        
        # Process status
        if is_running; then
            local pid=$(cat "$PID_FILE")
            echo -e "${GREEN}Status: RUNNING (PID: $pid)${NC}"
            
            # Process information
            if command -v ps > /dev/null 2>&1; then
                echo -e "${BLUE}Process Info:${NC}"
                ps -p "$pid" -o pid,ppid,etime,pcpu,pmem 2>/dev/null || echo "Process info not available"
            fi
            
            # Health check
            echo -e "${BLUE}Health Check:${NC}"
            if command -v curl > /dev/null 2>&1; then
                if curl -s -f "http://localhost:5000/health" > /dev/null 2>&1; then
                    echo -e "${GREEN}  Health endpoint: OK${NC}"
                else
                    echo -e "${RED}  Health endpoint: FAILED${NC}"
                fi
            else
                echo "  Health check not available (curl not found)"
            fi
            
        else
            echo -e "${RED}Status: NOT RUNNING${NC}"
        fi
        
        # Recent errors
        if [ -f "$ERROR_LOG" ]; then
            echo -e "${BLUE}Recent Errors:${NC}"
            tail -n 5 "$ERROR_LOG" | sed 's/^/  /'
        fi
        
        # System resources
        if command -v free > /dev/null 2>&1; then
            echo -e "${BLUE}Memory Usage:${NC}"
            free -h | grep -E "Mem|Swap" | sed 's/^/  /'
        fi
        
        echo ""
        echo -e "${BLUE}Refreshing in 5 seconds...${NC}"
        sleep 5
    done
}

# =============================================================================
# MAIN SCRIPT LOGIC
# =============================================================================

# Main script execution
case "${1:-}" in
    "start")
        start_smls
        ;;
    "stop")
        stop_smls
        ;;
    "restart")
        restart_smls
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "${2:-error}"
        ;;
    "monitor")
        monitor_smls
        ;;
    *)
        echo -e "${BLUE}SMLS Production Manager${NC}"
        echo -e "${BLUE}Usage: $0 {start|stop|restart|status|logs|monitor}${NC}"
        echo ""
        echo -e "${BLUE}Commands:${NC}"
        echo -e "${BLUE}  start   - Start SMLS in production mode${NC}"
        echo -e "${BLUE}  stop    - Stop SMLS gracefully${NC}"
        echo -e "${BLUE}  restart - Restart SMLS${NC}"
        echo -e "${BLUE}  status  - Show SMLS status and health${NC}"
        echo -e "${BLUE}  logs    - Show log files (access|error|health|all)${NC}"
        echo -e "${BLUE}  monitor - Real-time monitoring dashboard${NC}"
        echo ""
        echo -e "${BLUE}Examples:${NC}"
        echo -e "${BLUE}  $0 start${NC}"
        echo -e "${BLUE}  $0 status${NC}"
        echo -e "${BLUE}  $0 logs error${NC}"
        echo -e "${BLUE}  $0 monitor${NC}"
        exit 1
        ;;
esac