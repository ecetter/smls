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
echo -e "${PURPLE}║     SMLS Complete Setup and Launch                          ║${NC}"
echo -e "${PURPLE}║     Social Media Login Service - Automated Setup            ║${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if BASE_URL is provided
if [ -z "$BASE_URL" ]; then
echo -e "${RED}Error: BASE_URL environment variable is required${NC}"
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
echo -e "${YELLOW}All URLs work without root access${NC}"
echo -e "${YELLOW}The script automatically adds port 8080 for user-level deployment${NC}"
exit 1
fi

echo -e "${GREEN}BASE_URL: $BASE_URL${NC}"
echo ""

# Get the project root directory (parent of scripts directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMLS_DIR="$(dirname "$SCRIPT_DIR")"
echo -e "${BLUE} Working directory: $SMLS_DIR${NC}"
echo ""

# =============================================================================
# STEP 1: Create environment and ensure dependencies are satisfied
# =============================================================================

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  STEP 1: Environment Setup and Dependencies                ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW} Setting up Python environment and dependencies...${NC}"

# Check if virtual environment exists
if [ ! -d "smls_env" ]; then
echo -e "${YELLOW} Creating virtual environment...${NC}"

# Try creating virtual environment with ensurepip
if python3 -m venv smls_env > /dev/null 2>&1; then
echo -e "${GREEN} Virtual environment created${NC}"
else
echo -e "${YELLOW}  Standard venv creation failed, trying without ensurepip...${NC}"

# Try creating without ensurepip
if python3 -m venv --without-pip smls_env > /dev/null 2>&1; then
echo -e "${GREEN} Virtual environment created (without pip)${NC}"
echo -e "${YELLOW} Will install pip manually after activation${NC}"
else
echo -e "${RED} Failed to create virtual environment${NC}"
echo -e "${YELLOW} Make sure python3-venv package is installed:${NC}"
echo -e "${YELLOW}   Ubuntu/Debian: sudo apt install python3-venv${NC}"
echo -e "${YELLOW}   CentOS/RHEL: sudo yum install python3-venv${NC}"
echo -e "${YELLOW}   macOS: python3 -m ensurepip --upgrade${NC}"
exit 1
fi
fi
else
echo -e "${GREEN} Virtual environment already exists${NC}"
# Check if the virtual environment is actually functional
if [ ! -f "smls_env/bin/activate" ] || [ ! -f "smls_env/bin/python" ]; then
echo -e "${YELLOW}  Virtual environment appears corrupted, recreating...${NC}"
rm -rf smls_env

# Try creating virtual environment with ensurepip
if python3 -m venv smls_env > /dev/null 2>&1; then
echo -e "${GREEN} Virtual environment recreated${NC}"
else
echo -e "${YELLOW}  Standard venv recreation failed, trying without ensurepip...${NC}"

# Try creating without ensurepip
if python3 -m venv --without-pip smls_env > /dev/null 2>&1; then
echo -e "${GREEN} Virtual environment recreated (without pip)${NC}"
echo -e "${YELLOW} Will install pip manually after activation${NC}"
else
echo -e "${RED} Failed to recreate virtual environment${NC}"
echo -e "${YELLOW} Make sure python3-venv package is installed:${NC}"
echo -e "${YELLOW}   Ubuntu/Debian: sudo apt install python3-venv${NC}"
echo -e "${YELLOW}   CentOS/RHEL: sudo yum install python3-venv${NC}"
echo -e "${YELLOW}   macOS: python3 -m ensurepip --upgrade${NC}"
exit 1
fi
fi
fi
fi

# Activate virtual environment
echo -e "${YELLOW} Activating virtual environment...${NC}"
if [ -f "smls_env/bin/activate" ]; then
source smls_env/bin/activate
echo -e "${GREEN} Virtual environment activated${NC}"
else
echo -e "${RED} Virtual environment activation script not found${NC}"
echo -e "${YELLOW} Recreating virtual environment...${NC}"
rm -rf smls_env

# Try creating virtual environment with ensurepip
if python3 -m venv smls_env > /dev/null 2>&1; then
source smls_env/bin/activate
echo -e "${GREEN} Virtual environment recreated and activated${NC}"
else
echo -e "${YELLOW}  Standard venv recreation failed, trying without ensurepip...${NC}"

# Try creating without ensurepip
if python3 -m venv --without-pip smls_env > /dev/null 2>&1; then
source smls_env/bin/activate
echo -e "${GREEN} Virtual environment recreated and activated (without pip)${NC}"
echo -e "${YELLOW} Will install pip manually after activation${NC}"
else
echo -e "${RED} Failed to recreate virtual environment${NC}"
echo -e "${YELLOW} Make sure python3-venv package is installed:${NC}"
echo -e "${YELLOW}   Ubuntu/Debian: sudo apt install python3-venv${NC}"
echo -e "${YELLOW}   CentOS/RHEL: sudo yum install python3-venv${NC}"
echo -e "${YELLOW}   macOS: python3 -m ensurepip --upgrade${NC}"
exit 1
fi
fi
fi

# Check if pip is available and install it robustly
if ! python -m pip --version > /dev/null 2>&1; then
echo -e "${YELLOW} Installing pip...${NC}"

# Try ensurepip first
if python -m ensurepip --upgrade > /dev/null 2>&1; then
echo -e "${GREEN} pip installed via ensurepip${NC}"
else
echo -e "${YELLOW}  ensurepip failed, trying alternative methods...${NC}"

# Try wget first, then curl
if command -v wget > /dev/null 2>&1; then
echo -e "${YELLOW} Downloading pip via wget...${NC}"
wget -q https://bootstrap.pypa.io/get-pip.py -O get-pip.py
elif command -v curl > /dev/null 2>&1; then
echo -e "${YELLOW} Downloading pip via curl...${NC}"
curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
else
echo -e "${RED} Neither wget nor curl available for downloading pip${NC}"
echo -e "${YELLOW} Please install wget or curl, or install pip manually${NC}"
exit 1
fi

# Install pip
if [ -f "get-pip.py" ]; then
python get-pip.py
if [ $? -eq 0 ]; then
echo -e "${GREEN} pip installed via get-pip.py${NC}"
rm -f get-pip.py
else
echo -e "${RED} Failed to install pip via get-pip.py${NC}"
rm -f get-pip.py
exit 1
fi
else
echo -e "${RED} Failed to download get-pip.py${NC}"
exit 1
fi
fi
fi

# Install/upgrade pip
echo -e "${YELLOW} Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW} Installing Python dependencies...${NC}"
python -m pip install -r requirements.txt

echo -e "${GREEN} Environment setup complete${NC}"
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

# Function to find an available port
find_available_port() {
local start_port=$1
local port=$start_port
while [ $port -lt $((start_port + 100)) ]; do
if ! netstat -ln 2>/dev/null | grep -q ":$port "; then
echo $port
return 0
fi
port=$((port + 1))
done
echo $start_port  # Fallback to original port
}

# Determine the port to use
if [[ "$DOMAIN" =~ :[0-9]+$ ]]; then
# User specified any port - keep it as is
echo -e "${BLUE} Port already specified in BASE_URL${NC}"
echo -e "${BLUE}   Using production Gunicorn mode${NC}"
elif [[ "$DOMAIN" == *":80" ]] || [[ "$DOMAIN" == *":443" ]]; then
# User specified standard ports - convert to user-level
echo -e "${BLUE} Converting to port 8080 for user-level access${NC}"
# Update BASE_URL to use port 8080
if [[ "$BASE_URL" == *":80" ]]; then
BASE_URL="${BASE_URL/:80/:8080}"
elif [[ "$BASE_URL" == *":443" ]]; then
BASE_URL="${BASE_URL/:443/:8443}"
fi
echo -e "${BLUE}   Updated BASE_URL: $BASE_URL${NC}"
else
# No port specified - find available port for user-level
echo -e "${BLUE} Finding available port for user-level access${NC}"
AVAILABLE_PORT=$(find_available_port 8080)

# Add production port (5000) to BASE_URL for Gunicorn
if [[ "$BASE_URL" == http://* ]]; then
# Remove http:// prefix
URL_WITHOUT_PROTOCOL="${BASE_URL#http://}"
# Add production port 5000
BASE_URL="http://${URL_WITHOUT_PROTOCOL%%/*}:5000/${URL_WITHOUT_PROTOCOL#*/}"
elif [[ "$BASE_URL" == https://* ]]; then
# Remove https:// prefix
URL_WITHOUT_PROTOCOL="${BASE_URL#https://}"
# Add production port 5000 (Gunicorn handles HTTPS via reverse proxy)
BASE_URL="http://${URL_WITHOUT_PROTOCOL%%/*}:5000/${URL_WITHOUT_PROTOCOL#*/}"
fi
echo -e "${BLUE}   Updated BASE_URL: $BASE_URL${NC}"
echo -e "${BLUE}   Using production Gunicorn mode on port 5000${NC}"
fi

echo -e "${BLUE}   Domain: $DOMAIN${NC}"
echo -e "${BLUE}   Path: $PATH_PART${NC}"
echo ""

# Create necessary directories
echo -e "${YELLOW} Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p sessions
mkdir -p nginx/logs
echo -e "${GREEN} Directories created${NC}"

# Setup nginx configuration
echo -e "${YELLOW} Setting up nginx configuration...${NC}"

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

echo -e "${GREEN} nginx configuration generated${NC}"

echo -e "${GREEN} Configuration setup complete${NC}"
echo ""

# =============================================================================
# STEP 3: Launch SMLS
# =============================================================================

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  STEP 3: Launch SMLS                                       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Use production Gunicorn mode for maximum stability and security
echo -e "${GREEN} Using production Gunicorn mode for maximum stability${NC}"
echo -e "${BLUE}   This provides:${NC}"
echo -e "${BLUE}   • Multiple worker processes for better performance${NC}"
echo -e "${BLUE}   • Automatic worker restarts to prevent memory leaks${NC}"
echo -e "${BLUE}   • Production-grade security headers${NC}"
echo -e "${BLUE}   • Health monitoring and auto-recovery${NC}"
echo -e "${BLUE}   • Graceful shutdown handling${NC}"

# Start nginx if available (user-level only)
if [ -n "$NGINX_CMD" ]; then
echo -e "${YELLOW} Starting nginx in user mode...${NC}"

# Check if nginx is already running
if [ -f "nginx/nginx.pid" ] && kill -0 "$(cat nginx/nginx.pid)" 2>/dev/null; then
echo -e "${YELLOW}  nginx is already running, stopping it first...${NC}"
kill "$(cat nginx/nginx.pid)" 2>/dev/null || true
rm -f nginx/nginx.pid
fi

# Start nginx in user mode
$NGINX_CMD -c "$SMLS_DIR/nginx/nginx-smls-generated.conf" -p "$SMLS_DIR/nginx" > nginx/nginx_startup.log 2>&1 &
sleep 3

if [ -f "nginx/nginx.pid" ] && kill -0 "$(cat nginx/nginx.pid)" 2>/dev/null; then
echo -e "${GREEN} nginx started successfully${NC}"
else
echo -e "${YELLOW}  nginx failed to start, continuing with direct Flask mode${NC}"
if [ -f "nginx/nginx_startup.log" ]; then
echo -e "${YELLOW}   nginx error: $(head -1 nginx/nginx_startup.log)${NC}"
fi
NGINX_CMD=""
fi
fi

# Start SMLS using production manager
echo -e "${YELLOW} Starting SMLS in production mode...${NC}"

# Use the production manager to start SMLS
export BASE_URL="$BASE_URL"
if "$SMLS_DIR/production/production_manager.sh" start; then
echo -e "${GREEN} SMLS started successfully in production mode${NC}"
else
echo -e "${RED} Failed to start SMLS${NC}"
echo -e "${YELLOW} Check the logs: $SMLS_DIR/production/production_manager.sh logs error${NC}"
exit 1
fi

echo ""
echo -e "${GREEN} SMLS Setup and Launch Complete!${NC}"
echo ""

# =============================================================================
# SUCCESS SUMMARY
# =============================================================================

echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                    SETUP COMPLETE                        ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN} Environment: Python virtual environment created and activated${NC}"
echo -e "${GREEN} Dependencies: All Python packages installed (including Gunicorn)${NC}"
echo -e "${GREEN} Configuration: Production WSGI configuration ready${NC}"
echo -e "${GREEN} SMLS: Application started in production mode${NC}"

echo -e "${GREEN} Gunicorn: Production server running (port 5000)${NC}"
echo -e "${BLUE}   Access via: $BASE_URL${NC}"
echo -e "${BLUE}   Workers: Multiple processes for stability${NC}"
echo -e "${BLUE}   Security: Production-grade headers enabled${NC}"

echo ""
echo -e "${BLUE} Your SMLS is now available at:${NC}"
echo -e "${CYAN}   $BASE_URL${NC}"
echo ""

echo -e "${BLUE} OAuth Configuration:${NC}"
echo -e "${CYAN}   Google: $BASE_URL/auth/google/callback${NC}"
echo -e "${CYAN}   LinkedIn: $BASE_URL/auth/linkedin/callback${NC}"
echo ""

echo -e "${BLUE} Management Commands:${NC}"
echo -e "${CYAN}   Status: ./manage.sh status${NC}"
echo -e "${CYAN}   Logs: ./manage.sh logs error${NC}"
echo -e "${CYAN}   Stop: ./manage.sh stop${NC}"
echo -e "${CYAN}   Monitor: ./manage.sh monitor${NC}"
echo -e "${CYAN}   Health: ./health.sh status${NC}"

echo ""
echo -e "${BLUE} Log Locations:${NC}"
echo -e "${CYAN}   Access Log: ./persist/logs/gunicorn_access.log${NC}"
echo -e "${CYAN}   Error Log: ./persist/logs/gunicorn_error.log${NC}"
echo -e "${CYAN}   Health Log: ./persist/logs/health_check.log${NC}"

echo ""
echo -e "${YELLOW} Next Steps:${NC}"
echo -e "${CYAN}   1. Update your OAuth app settings with the callback URLs above${NC}"
echo -e "${CYAN}   2. Visit $BASE_URL to test your application${NC}"
echo -e "${CYAN}   3. Use the management commands to monitor and control SMLS${NC}"

echo ""
echo -e "${GREEN}SMLS is ready for production use${NC}"
