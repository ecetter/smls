#!/bin/bash
# Start SMLS with nginx-compatible configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting SMLS with Nginx Configuration${NC}"
echo "=============================================="

# Get the current directory (nginx directory)
NGINX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go up one directory to the main SMLS directory
SMLS_DIR="$(dirname "$NGINX_DIR")"

# Check if BASE_URL is provided
if [ -z "$BASE_URL" ]; then
    echo -e "${RED}❌ Error: BASE_URL environment variable is required${NC}"
    echo ""
    echo "Usage:"
    echo "  export BASE_URL='http://yourdomain.com/your/path'"
    echo "  ./start-with-nginx.sh"
    echo ""
    echo "Examples:"
    echo "  export BASE_URL='http://emeryetter.com/sweng861/smls'"
    echo "  export BASE_URL='https://mydomain.com/app'"
    echo "  export BASE_URL='http://localhost:8080/myapp'"
    echo ""
    echo "Note: Use the same BASE_URL that you used with setup-nginx.sh"
    exit 1
fi

# Parse BASE_URL to extract domain and path for display
URL_WITHOUT_PROTOCOL=${BASE_URL#http://}
URL_WITHOUT_PROTOCOL=${URL_WITHOUT_PROTOCOL#https://}
DOMAIN=$(echo "$URL_WITHOUT_PROTOCOL" | cut -d'/' -f1)
PATH_PART=$(echo "$URL_WITHOUT_PROTOCOL" | sed "s|^$DOMAIN||")
if [ -z "$PATH_PART" ]; then
    PATH_PART="/"
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Base URL: $BASE_URL"
echo "  Domain: $DOMAIN"
echo "  Path: $PATH_PART"
echo "  Flask will run on: localhost:8080"
echo "  Nginx will proxy: $BASE_URL -> localhost:8080"
echo ""

# Check if nginx is running
if ! pgrep nginx > /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: nginx doesn't appear to be running${NC}"
    echo "Please make sure nginx is started and configured:"
    echo "  sudo systemctl start nginx"
    echo "  export BASE_URL='$BASE_URL'"
    echo "  ./setup-nginx.sh"
    echo ""
fi

# Check if port 8080 is available
if lsof -i :8080 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Warning: Port 8080 is already in use${NC}"
    echo "Please stop any existing SMLS instances:"
    echo "  ./persist/manage.sh stop"
    echo ""
fi

# Start SMLS with the nginx-compatible configuration
echo -e "${YELLOW}🚀 Starting SMLS...${NC}"
cd "$SMLS_DIR"

# Use the persist management script to start with the correct BASE_URL
export BASE_URL="$BASE_URL"
./persist/manage.sh start

echo ""
echo -e "${GREEN}✅ SMLS started successfully!${NC}"
echo ""
echo -e "${BLUE}🌐 Your SMLS is now available at:${NC}"
echo "   $BASE_URL"
echo ""
echo -e "${BLUE}🔍 To check status:${NC}"
echo "   ./persist/manage.sh status"
echo ""
echo -e "${BLUE}📝 To view logs:${NC}"
echo "   ./persist/manage.sh logs"
echo ""
echo -e "${BLUE}🛑 To stop:${NC}"
echo "   ./persist/manage.sh stop"
echo ""
echo -e "${BLUE}📋 OAuth Configuration:${NC}"
echo "  Update your OAuth apps to use these redirect URIs:"
echo "  Google: $BASE_URL/auth/google/callback"
echo "  LinkedIn: $BASE_URL/auth/linkedin/callback"