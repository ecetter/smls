#!/bin/bash
# Check status of user-level nginx for SMLS

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 User-Level Nginx Status${NC}"
echo "=========================="

NGINX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NGINX_PID_FILE="$NGINX_DIR/nginx.pid"

if [ ! -f "$NGINX_PID_FILE" ]; then
    echo -e "${RED}❌ nginx is not running${NC}"
    exit 1
fi

PID=$(cat "$NGINX_PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
    echo -e "${GREEN}✅ nginx is running (PID: $PID)${NC}"
    echo -e "${BLUE}📋 Configuration:${NC}"
    echo "  Config: $NGINX_DIR/nginx-smls-generated.conf"
    echo "  PID: $NGINX_PID_FILE"
    echo "  Logs: $NGINX_DIR/logs/"
    echo ""
    echo -e "${BLUE}🔍 Process info:${NC}"
    ps -p "$PID" -o pid,ppid,cmd
else
    echo -e "${RED}❌ nginx is not running (stale PID file)${NC}"
    rm -f "$NGINX_PID_FILE"
    exit 1
fi
