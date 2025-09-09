#!/bin/bash
# Stop user-level nginx for SMLS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping User-Level Nginx for SMLS${NC}"
echo "======================================"

NGINX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NGINX_PID_FILE="$NGINX_DIR/nginx.pid"

if [ ! -f "$NGINX_PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  nginx PID file not found. nginx may not be running.${NC}"
    exit 0
fi

PID=$(cat "$NGINX_PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  nginx process not found. Cleaning up PID file.${NC}"
    rm -f "$NGINX_PID_FILE"
    exit 0
fi

echo -e "${YELLOW}🛑 Stopping nginx (PID: $PID)...${NC}"
kill "$PID"

# Wait for graceful shutdown
for i in {1..10}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo -e "${GREEN}✅ nginx stopped successfully${NC}"
        rm -f "$NGINX_PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if graceful shutdown failed
echo -e "${YELLOW}⚠️  Graceful shutdown failed, force killing...${NC}"
kill -9 "$PID" 2>/dev/null || true
rm -f "$NGINX_PID_FILE"
echo -e "${GREEN}✅ nginx stopped${NC}"
