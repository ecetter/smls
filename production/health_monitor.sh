#!/bin/bash

# =============================================================================
# SMLS Health Monitoring System
# =============================================================================
#
# This script provides comprehensive health monitoring for the SMLS application
# running in production mode. It continuously monitors application health,
# performs automated recovery, and provides detailed health reporting.
#
# Key Features:
# - Continuous health monitoring with configurable intervals
# - Automated recovery and restart on failures
# - Comprehensive health reporting and logging
# - Integration with production management system
# - Resource monitoring and alerting
# - Graceful error handling and recovery
#
# Usage:
#   ./health_monitor.sh {start|status|check}
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
HEALTH_LOG="$PROJECT_DIR/persist/logs/health_check.log"
PRODUCTION_MANAGER="$SCRIPT_DIR/production_manager.sh"

# Health monitoring configuration
HEALTH_CHECK_INTERVAL=60        # Seconds between health checks
HEALTH_CHECK_TIMEOUT=10         # Timeout for health check requests
MAX_CONSECUTIVE_FAILURES=3      # Failures before triggering recovery
HEALTH_ENDPOINT="http://localhost:5000/health"  # Health check endpoint

# Ensure log directory exists
mkdir -p "$(dirname "$HEALTH_LOG")"

# =============================================================================
# HEALTH MONITORING FUNCTIONS
# =============================================================================

# Function to log health check results
log_health_check() {
    # Log health check results with timestamp and details
    local level="$1"
    local message="$2"
    local details="${3:-}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Format log entry with timestamp and level
    local log_entry="[$timestamp] [$level] $message"
    if [ -n "$details" ]; then
        log_entry="$log_entry - $details"
    fi
    
    # Write to health log file
    echo "$log_entry" >> "$HEALTH_LOG"
    
    # Also output to console for real-time monitoring
    case "$level" in
        "INFO")
            echo -e "${BLUE}[$timestamp] $message${NC}"
            ;;
        "WARN")
            echo -e "${YELLOW}[$timestamp] $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}[$timestamp] $message${NC}"
            ;;
    esac
}

# Function to perform health check
perform_health_check() {
    # Perform a comprehensive health check of the SMLS application
    local health_status="PASSED"
    local health_details=""
    
    # Check if process is running
    if [ ! -f "$PID_FILE" ]; then
        health_status="FAILED"
        health_details="Process not running (no PID file)"
        log_health_check "ERROR" "Health check failed" "$health_details"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    if ! ps -p "$pid" > /dev/null 2>&1; then
        health_status="FAILED"
        health_details="Process not running (PID $pid not found)"
        log_health_check "ERROR" "Health check failed" "$health_details"
        return 1
    fi
    
    # Check health endpoint
    if command -v curl > /dev/null 2>&1; then
        local health_response
        if health_response=$(curl -s -f --max-time "$HEALTH_CHECK_TIMEOUT" "$HEALTH_ENDPOINT" 2>/dev/null); then
            # Parse health response
            if echo "$health_response" | grep -q '"status":"healthy"'; then
                health_details="Health endpoint responding correctly"
            else
                health_status="FAILED"
                health_details="Health endpoint returned invalid response"
                log_health_check "ERROR" "Health check failed" "$health_details"
                return 1
            fi
        else
            health_status="FAILED"
            health_details="Health endpoint not responding"
            log_health_check "ERROR" "Health check failed" "$health_details"
            return 1
        fi
    else
        # Fallback to process check only
        health_details="Process running (curl not available for endpoint check)"
        log_health_check "WARN" "Health check limited" "curl not available"
    fi
    
    # Log successful health check
    log_health_check "INFO" "Health check passed" "$health_details"
    return 0
}

# Function to start health monitoring
start_health_monitoring() {
    # Start continuous health monitoring of the SMLS application
    log_health_check "INFO" "Starting health monitoring" "Interval: ${HEALTH_CHECK_INTERVAL}s"
    
    local consecutive_failures=0
    local check_count=0
    
    # Main monitoring loop
    while true; do
        check_count=$((check_count + 1))
        
        # Perform health check
        if perform_health_check; then
            # Health check passed
            consecutive_failures=0
            log_health_check "INFO" "Health check $check_count passed" "Consecutive failures: 0"
        else
            # Health check failed
            consecutive_failures=$((consecutive_failures + 1))
            log_health_check "WARN" "Health check $check_count failed" "Consecutive failures: $consecutive_failures"
            
            # Check if we need to trigger recovery
            if [ $consecutive_failures -ge $MAX_CONSECUTIVE_FAILURES ]; then
                log_health_check "ERROR" "Triggering recovery" "Consecutive failures: $consecutive_failures"
                
                # Attempt to restart the application
                if [ -f "$PRODUCTION_MANAGER" ]; then
                    log_health_check "INFO" "Restarting application" "Using production manager"
                    "$PRODUCTION_MANAGER" restart
                    
                    # Wait for restart to complete
                    sleep 10
                    
                    # Reset failure counter after restart attempt
                    consecutive_failures=0
                else
                    log_health_check "ERROR" "Recovery failed" "Production manager not found"
                fi
            fi
        fi
        
        # Wait for next health check
        sleep "$HEALTH_CHECK_INTERVAL"
    done
}

# Function to show health status
show_health_status() {
    # Display current health status of the SMLS application
    echo -e "${BLUE}SMLS Health Status${NC}"
    echo -e "${BLUE}====================${NC}"
    
    # Current health check
    echo -e "${BLUE}Health check:${NC}"
    if perform_health_check; then
        echo -e "${GREEN} PASSED${NC}"
    else
        echo -e "${RED} FAILED${NC}"
    fi
    
    # Process status
    echo -e "${BLUE}Process:${NC}"
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN} RUNNING (PID: $pid)${NC}"
        else
            echo -e "${RED} NOT RUNNING${NC}"
        fi
    else
        echo -e "${RED} NOT RUNNING${NC}"
    fi
    
    # Recent health log entries
    if [ -f "$HEALTH_LOG" ]; then
        echo -e "${BLUE}Recent Health Activity:${NC}"
        tail -n 10 "$HEALTH_LOG" | sed 's/^/  /'
    else
        echo -e "${YELLOW}No health log found${NC}"
    fi
}

# Function to perform single health check
perform_single_health_check() {
    # Perform a single health check and display results
    echo -e "${BLUE}Performing health check...${NC}"
    
    if perform_health_check; then
        echo -e "${GREEN}Health check: PASSED${NC}"
        return 0
    else
        echo -e "${RED}Health check: FAILED${NC}"
        return 1
    fi
}

# =============================================================================
# MAIN SCRIPT LOGIC
# =============================================================================

# Main script execution
case "${1:-}" in
    "start")
        start_health_monitoring
        ;;
    "status")
        show_health_status
        ;;
    "check")
        perform_single_health_check
        ;;
    *)
        echo -e "${BLUE}SMLS Health Monitor${NC}"
        echo -e "${BLUE}Usage: $0 {start|status|check}${NC}"
        echo ""
        echo -e "${BLUE}Commands:${NC}"
        echo -e "${BLUE}  start  - Start continuous health monitoring${NC}"
        echo -e "${BLUE}  status - Show current health status${NC}"
        echo -e "${BLUE}  check  - Perform single health check${NC}"
        echo ""
        echo -e "${BLUE}Examples:${NC}"
        echo -e "${BLUE}  $0 start${NC}"
        echo -e "${BLUE}  $0 status${NC}"
        echo -e "${BLUE}  $0 check${NC}"
        echo ""
        echo -e "${BLUE}Health Monitoring Features:${NC}"
        echo -e "${BLUE}  - Continuous monitoring with ${HEALTH_CHECK_INTERVAL}s intervals${NC}"
        echo -e "${BLUE}  - Automated recovery after ${MAX_CONSECUTIVE_FAILURES} failures${NC}"
        echo -e "${BLUE}  - Comprehensive logging and reporting${NC}"
        echo -e "${BLUE}  - Integration with production management${NC}"
        exit 1
        ;;
esac
