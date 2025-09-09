#!/bin/bash
# SMLS Complete Setup and Launch Script
# This script automates the entire workflow:
# 1. Create environment and ensure dependencies are satisfied
# 2. Setup configuration
# 3. Launch SMLS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}║     🚀 SMLS Complete Setup and Launch                       ║${NC}"
echo -e "${PURPLE}║     Social Media Login Service - Automated Setup            ║${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if BASE_URL is provided
if [ -z "$BASE_URL" ]; then
    echo -e "${RED}❌ Error: BASE_URL environment variable is required${NC}"
    echo ""
    echo -e "${BLUE}Usage:${NC}"
    echo "  export BASE_URL='http://yourdomain.com/your/path'"
    echo "  ./setup-and-launch.sh"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  export BASE_URL='http://emeryetter.com/sweng861/smls'"
    echo "  export BASE_URL='http://mydomain.com/app'"
    echo "  export BASE_URL='http://localhost:8080/myapp'"
    echo ""
    echo -e "${YELLOW}💡 All URLs work without root access${NC}"
    echo -e "${YELLOW}💡 The script automatically adds port 8080 for user-level deployment${NC}"
    exit 1
fi

echo -e "${GREEN}✅ BASE_URL: $BASE_URL${NC}"
echo ""

# Get the current directory
SMLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${BLUE}📁 Working directory: $SMLS_DIR${NC}"
echo ""

# =============================================================================
# STEP 1: Create environment and ensure dependencies are satisfied
# =============================================================================

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  STEP 1: Environment Setup and Dependencies                ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}🔧 Setting up Python environment and dependencies...${NC}"

# Check if virtual environment exists
if [ ! -d "smls_env" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv smls_env
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source smls_env/bin/activate

# Check if pip is available
if ! python -m pip --version > /dev/null 2>&1; then
    echo -e "${YELLOW}📦 Installing pip...${NC}"
    python -m ensurepip --upgrade
    if ! python -m pip --version > /dev/null 2>&1; then
        echo -e "${YELLOW}📦 Downloading and installing pip manually...${NC}"
        curl -sSL https://bootstrap.pypa.io/get-pip.py | python
    fi
fi

# Install/upgrade pip
echo -e "${YELLOW}📦 Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
python -m pip install -r requirements.txt

echo -e "${GREEN}✅ Environment setup complete${NC}"
echo ""

# =============================================================================
# STEP 2: Setup configuration
# =============================================================================

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  STEP 2: Configuration Setup                               ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Parse BASE_URL to determine deployment type
URL_WITHOUT_PROTOCOL=${BASE_URL#http://}
URL_WITHOUT_PROTOCOL=${URL_WITHOUT_PROTOCOL#https://}
DOMAIN=$(echo "$URL_WITHOUT_PROTOCOL" | cut -d'/' -f1)
PATH_PART=$(echo "$URL_WITHOUT_PROTOCOL" | sed "s|^$DOMAIN||")
if [ -z "$PATH_PART" ]; then
    PATH_PART="/"
fi

# Always use user-level deployment (no root required)
# If user wants clean URLs, they can use a reverse proxy or port forwarding
DEPLOYMENT_TYPE="user-level"

# Determine the port to use
if [[ "$DOMAIN" == *":8080" ]] || [[ "$DOMAIN" == *":8443" ]]; then
    # User specified a port
    echo -e "${BLUE}🔧 Using port 8080 for nginx, port 5000 for Flask${NC}"
elif [[ "$DOMAIN" == *":80" ]] || [[ "$DOMAIN" == *":443" ]]; then
    # User specified standard ports - convert to user-level
    echo -e "${BLUE}🔧 Converting to port 8080 for user-level access${NC}"
    # Update BASE_URL to use port 8080
    if [[ "$BASE_URL" == *":80" ]]; then
        BASE_URL="${BASE_URL/:80/:8080}"
    elif [[ "$BASE_URL" == *":443" ]]; then
        BASE_URL="${BASE_URL/:443/:8443}"
    fi
    echo -e "${BLUE}   Updated BASE_URL: $BASE_URL${NC}"
else
    # No port specified - add port 8080 for user-level
    echo -e "${BLUE}🔧 Adding port 8080 for user-level access${NC}"
    # Add port 8080 to BASE_URL
    if [[ "$BASE_URL" == http://* ]]; then
        # Remove http:// prefix
        URL_WITHOUT_PROTOCOL="${BASE_URL#http://}"
        # Add port 8080
        BASE_URL="http://${URL_WITHOUT_PROTOCOL%%/*}:8080/${URL_WITHOUT_PROTOCOL#*/}"
    elif [[ "$BASE_URL" == https://* ]]; then
        # Remove https:// prefix
        URL_WITHOUT_PROTOCOL="${BASE_URL#https://}"
        # Add port 8443
        BASE_URL="https://${URL_WITHOUT_PROTOCOL%%/*}:8443/${URL_WITHOUT_PROTOCOL#*/}"
    fi
    echo -e "${BLUE}   Updated BASE_URL: $BASE_URL${NC}"
fi

echo -e "${BLUE}   Domain: $DOMAIN${NC}"
echo -e "${BLUE}   Path: $PATH_PART${NC}"
echo ""

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p sessions
mkdir -p nginx/logs
echo -e "${GREEN}✅ Directories created${NC}"

# Setup nginx configuration
echo -e "${YELLOW}🔧 Setting up nginx configuration...${NC}"

# Generate user-level nginx configuration
sed -e "s|DOMAIN|$DOMAIN|g" \
    -e "s|PATH|$PATH_PART|g" \
    nginx/nginx-smls.conf > nginx/nginx-smls-generated.conf

# Update paths for user-level deployment
sed -i.bak \
    -e "s|/var/log/nginx|$SMLS_DIR/nginx/logs|g" \
    -e "s|/etc/nginx|$SMLS_DIR/nginx|g" \
    nginx/nginx-smls-generated.conf
rm -f nginx/nginx-smls-generated.conf.bak

echo -e "${GREEN}✅ nginx configuration generated${NC}"

echo -e "${GREEN}✅ Configuration setup complete${NC}"
echo ""

# =============================================================================
# STEP 3: Launch SMLS
# =============================================================================

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  STEP 3: Launch SMLS                                       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if nginx is available
NGINX_CMD=""
if command -v nginx &> /dev/null; then
    NGINX_CMD="nginx"
    echo -e "${GREEN}✅ nginx found${NC}"
elif [ -f "$HOME/nginx/sbin/nginx" ]; then
    NGINX_CMD="$HOME/nginx/sbin/nginx"
    echo -e "${GREEN}✅ User nginx found${NC}"
else
    echo -e "${YELLOW}⚠️  nginx not found - will run in direct Flask mode${NC}"
    echo -e "${YELLOW}   To use nginx reverse proxy, install nginx first${NC}"
    NGINX_CMD=""
fi

# Start nginx if available (user-level only)
if [ -n "$NGINX_CMD" ]; then
    echo -e "${YELLOW}🚀 Starting nginx in user mode...${NC}"
    
    # Check if nginx is already running
    if [ -f "nginx/nginx.pid" ] && kill -0 "$(cat nginx/nginx.pid)" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  nginx is already running, stopping it first...${NC}"
        kill "$(cat nginx/nginx.pid)" 2>/dev/null || true
        rm -f nginx/nginx.pid
    fi
    
    # Start nginx in user mode
    $NGINX_CMD -c "$SMLS_DIR/nginx/nginx-smls-generated.conf" -p "$SMLS_DIR/nginx" -g "pid nginx.pid; error_log logs/error.log; access_log logs/access.log;" &
    sleep 2
    
    if [ -f "nginx/nginx.pid" ] && kill -0 "$(cat nginx/nginx.pid)" 2>/dev/null; then
        echo -e "${GREEN}✅ nginx started successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  nginx failed to start, continuing with direct Flask mode${NC}"
        NGINX_CMD=""
    fi
fi

# Start SMLS
echo -e "${YELLOW}🚀 Starting SMLS...${NC}"

# Use the persist management script to start SMLS
export BASE_URL="$BASE_URL"
./persist/manage.sh start

# Wait a moment for SMLS to start
sleep 3

# Check if SMLS is running
if ./persist/manage.sh status > /dev/null 2>&1; then
    echo -e "${GREEN}✅ SMLS started successfully${NC}"
else
    echo -e "${RED}❌ SMLS failed to start${NC}"
    echo -e "${YELLOW}📝 Check the logs: ./persist/manage.sh logs${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 SMLS Setup and Launch Complete!${NC}"
echo ""

# =============================================================================
# SUCCESS SUMMARY
# =============================================================================

echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                    🎉 SUCCESS! 🎉                          ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ Environment: Python virtual environment created and activated${NC}"
echo -e "${GREEN}✅ Dependencies: All Python packages installed${NC}"
echo -e "${GREEN}✅ Configuration: nginx configuration generated${NC}"
echo -e "${GREEN}✅ SMLS: Application started and running${NC}"

if [ -n "$NGINX_CMD" ]; then
    echo -e "${GREEN}✅ Nginx: Reverse proxy running (port 8080)${NC}"
fi

echo ""
echo -e "${BLUE}🌐 Your SMLS is now available at:${NC}"
echo -e "${CYAN}   $BASE_URL${NC}"
echo ""

echo -e "${BLUE}📋 OAuth Configuration:${NC}"
echo -e "${CYAN}   Google: $BASE_URL/auth/google/callback${NC}"
echo -e "${CYAN}   LinkedIn: $BASE_URL/auth/linkedin/callback${NC}"
echo ""

echo -e "${BLUE}🔧 Management Commands:${NC}"
echo -e "${CYAN}   Status: ./persist/manage.sh status${NC}"
echo -e "${CYAN}   Logs: ./persist/manage.sh logs${NC}"
echo -e "${CYAN}   Stop: ./persist/manage.sh stop${NC}"

if [ -n "$NGINX_CMD" ]; then
    echo -e "${CYAN}   Nginx Status: ./nginx/status-user-nginx.sh${NC}"
    echo -e "${CYAN}   Stop Nginx: ./nginx/stop-user-nginx.sh${NC}"
fi

echo ""
echo -e "${BLUE}📝 Log Locations:${NC}"
echo -e "${CYAN}   SMLS Logs: ./persist/logs/smls_background.log${NC}"
if [ -n "$NGINX_CMD" ]; then
    echo -e "${CYAN}   Nginx Logs: ./nginx/logs/${NC}"
fi

echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo -e "${CYAN}   1. Update your OAuth app settings with the callback URLs above${NC}"
echo -e "${CYAN}   2. Visit $BASE_URL to test your application${NC}"
echo -e "${CYAN}   3. Use the management commands to monitor and control SMLS${NC}"

echo ""
echo -e "${GREEN}🚀 SMLS is ready to use!${NC}"
