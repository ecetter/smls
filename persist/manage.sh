#!/bin/bash
# Simple management script for SMLS
# This provides easy commands to manage your SMLS application

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 SMLS Management${NC}"
echo "=================="

case "$1" in
    start)
        echo -e "${GREEN}Starting SMLS in background...${NC}"
        "$SCRIPT_DIR/run_background.sh" start
        ;;
    stop)
        echo -e "${GREEN}Stopping SMLS...${NC}"
        "$SCRIPT_DIR/run_background.sh" stop
        ;;
    restart)
        echo -e "${GREEN}Restarting SMLS...${NC}"
        "$SCRIPT_DIR/run_background.sh" restart
        ;;
    status)
        "$SCRIPT_DIR/run_background.sh" status
        ;;
    logs)
        "$SCRIPT_DIR/run_background.sh" logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start SMLS in background (survives logout)"
        echo "  stop    - Stop SMLS"
        echo "  restart - Restart SMLS"
        echo "  status  - Check if SMLS is running"
        echo "  logs    - View live logs"
        echo ""
        echo "Examples:"
        echo "  $0 start    # Start the app in background"
        echo "  $0 status   # Check if it's running"
        echo "  $0 logs     # View logs"
        echo "  $0 stop     # Stop the app"
        ;;
esac
