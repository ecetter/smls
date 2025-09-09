#!/bin/bash
# Start nginx in user mode for SMLS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting User-Level Nginx for SMLS${NC}"
echo "====================================="

# Get the current directory
NGINX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMLS_DIR="$(dirname "$NGINX_DIR")"
NGINX_CONFIG="$NGINX_DIR/nginx-smls-generated.conf"
NGINX_PID_FILE="$NGINX_DIR/nginx.pid"
NGINX_LOG_DIR="$NGINX_DIR/logs"

# Check if configuration exists
if [ ! -f "$NGINX_CONFIG" ]; then
    echo -e "${RED}❌ Error: nginx configuration not found${NC}"
    echo "Please run ./setup-nginx.sh first"
    exit 1
fi

# Create logs directory
mkdir -p "$NGINX_LOG_DIR"

# Find nginx executable
NGINX_CMD=""
if command -v nginx &> /dev/null; then
    NGINX_CMD="nginx"
elif [ -f "$HOME/nginx/sbin/nginx" ]; then
    NGINX_CMD="$HOME/nginx/sbin/nginx"
else
    echo -e "${RED}❌ Error: nginx not found${NC}"
    echo "Please install nginx first"
    exit 1
fi

# Check if nginx is already running
if [ -f "$NGINX_PID_FILE" ] && kill -0 "$(cat "$NGINX_PID_FILE")" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  nginx is already running (PID: $(cat "$NGINX_PID_FILE"))${NC}"
    echo "Use ./stop-user-nginx.sh to stop it first"
    exit 1
fi

# Start nginx in user mode
echo -e "${YELLOW}🚀 Starting nginx...${NC}"
$NGINX_CMD -c "$NGINX_CONFIG" -p "$NGINX_DIR" -g "pid $NGINX_PID_FILE; error_log $NGINX_LOG_DIR/error.log; access_log $NGINX_LOG_DIR/access.log;"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ nginx started successfully${NC}"
    echo -e "${BLUE}📋 Configuration:${NC}"
    echo "  Config: $NGINX_CONFIG"
    echo "  PID: $NGINX_PID_FILE"
    echo "  Logs: $NGINX_LOG_DIR/"
    echo ""
    echo -e "${BLUE}🔍 To check status:${NC}"
    echo "  ./nginx/status-user-nginx.sh"
    echo ""
    echo -e "${BLUE}🛑 To stop:${NC}"
    echo "  ./nginx/stop-user-nginx.sh"
else
    echo -e "${RED}❌ Failed to start nginx${NC}"
    echo "Check the logs: $NGINX_LOG_DIR/error.log"
    exit 1
fi
