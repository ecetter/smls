#!/bin/bash
# Setup script for nginx reverse proxy configuration for SMLS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 SMLS Nginx Setup${NC}"
echo "=================================="

# Check if BASE_URL is provided
if [ -z "$BASE_URL" ]; then
    echo -e "${RED}❌ Error: BASE_URL environment variable is required${NC}"
    echo ""
    echo "Usage:"
    echo "  export BASE_URL='http://yourdomain.com/your/path'"
    echo "  ./setup-nginx.sh"
    echo ""
    echo "Examples:"
    echo "  export BASE_URL='http://emeryetter.com/sweng861/smls'"
    echo "  export BASE_URL='https://mydomain.com/app'"
    echo "  export BASE_URL='http://localhost:8080/myapp'"
    exit 1
fi

echo -e "${GREEN}✅ BASE_URL: $BASE_URL${NC}"

# Parse BASE_URL to extract domain and path
# Remove protocol (http:// or https://)
URL_WITHOUT_PROTOCOL=${BASE_URL#http://}
URL_WITHOUT_PROTOCOL=${URL_WITHOUT_PROTOCOL#https://}

# Extract domain (everything before the first slash)
DOMAIN=$(echo "$URL_WITHOUT_PROTOCOL" | cut -d'/' -f1)

# Extract path (everything after the domain, including leading slash)
PATH_PART=$(echo "$URL_WITHOUT_PROTOCOL" | sed "s|^$DOMAIN||")

# If no path specified, default to root
if [ -z "$PATH_PART" ]; then
    PATH_PART="/"
fi

echo -e "${GREEN}✅ Domain: $DOMAIN${NC}"
echo -e "${GREEN}✅ Path: $PATH_PART${NC}"

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}❌ Error: nginx is not installed${NC}"
    echo "Please install nginx first:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install nginx"
    echo "  CentOS/RHEL: sudo yum install nginx"
    echo "  macOS: brew install nginx"
    exit 1
fi

echo -e "${GREEN}✅ nginx is installed${NC}"

# Check nginx version
NGINX_VERSION=$(nginx -v 2>&1 | cut -d' ' -f3)
echo -e "${GREEN}✅ nginx version: $NGINX_VERSION${NC}"

# Get the current directory (nginx directory)
NGINX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go up one directory to the main SMLS directory
SMLS_DIR="$(dirname "$NGINX_DIR")"
NGINX_CONFIG_TEMPLATE="$NGINX_DIR/nginx-smls.conf"
NGINX_CONFIG_GENERATED="$NGINX_DIR/nginx-smls-generated.conf"

echo -e "${BLUE}📁 SMLS directory: $SMLS_DIR${NC}"
echo -e "${BLUE}📄 Nginx config template: $NGINX_CONFIG_TEMPLATE${NC}"

# Check if the nginx config template exists
if [ ! -f "$NGINX_CONFIG_TEMPLATE" ]; then
    echo -e "${RED}❌ Error: nginx-smls.conf template not found in $NGINX_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ nginx-smls.conf template found${NC}"

# Generate the actual nginx configuration by replacing placeholders
echo -e "${YELLOW}🔧 Generating nginx configuration...${NC}"
sed -e "s|DOMAIN|$DOMAIN|g" \
    -e "s|PATH|$PATH_PART|g" \
    "$NGINX_CONFIG_TEMPLATE" > "$NGINX_CONFIG_GENERATED"

echo -e "${GREEN}✅ Generated configuration: $NGINX_CONFIG_GENERATED${NC}"

# Test nginx configuration
echo -e "${YELLOW}🔍 Testing nginx configuration...${NC}"
if sudo nginx -t -c "$NGINX_CONFIG_GENERATED"; then
    echo -e "${GREEN}✅ nginx configuration test passed${NC}"
else
    echo -e "${RED}❌ nginx configuration test failed${NC}"
    echo "Please check the generated configuration file for syntax errors"
    rm -f "$NGINX_CONFIG_GENERATED"
    exit 1
fi

# Determine nginx sites directory
if [ -d "/etc/nginx/sites-available" ]; then
    # Ubuntu/Debian style
    SITES_AVAILABLE="/etc/nginx/sites-available"
    SITES_ENABLED="/etc/nginx/sites-enabled"
    NGINX_SITE_CONFIG="$SITES_AVAILABLE/smls"
elif [ -d "/etc/nginx/conf.d" ]; then
    # CentOS/RHEL style
    SITES_AVAILABLE="/etc/nginx/conf.d"
    SITES_ENABLED="/etc/nginx/conf.d"
    NGINX_SITE_CONFIG="$SITES_AVAILABLE/smls.conf"
else
    echo -e "${RED}❌ Error: Could not determine nginx configuration directory${NC}"
    echo "Please manually copy the generated configuration to your nginx configuration directory"
    echo "Generated config: $NGINX_CONFIG_GENERATED"
    exit 1
fi

echo -e "${BLUE}📂 Nginx sites directory: $SITES_AVAILABLE${NC}"

# Copy the generated configuration file
echo -e "${YELLOW}📋 Copying nginx configuration...${NC}"
sudo cp "$NGINX_CONFIG_GENERATED" "$NGINX_SITE_CONFIG"
echo -e "${GREEN}✅ Configuration copied to $NGINX_SITE_CONFIG${NC}"

# Enable the site (Ubuntu/Debian only)
if [ -d "/etc/nginx/sites-enabled" ]; then
    echo -e "${YELLOW}🔗 Enabling site...${NC}"
    sudo ln -sf "$NGINX_SITE_CONFIG" "$SITES_ENABLED/smls"
    echo -e "${GREEN}✅ Site enabled${NC}"
fi

# Test the configuration again
echo -e "${YELLOW}🔍 Testing updated nginx configuration...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}✅ Updated nginx configuration test passed${NC}"
else
    echo -e "${RED}❌ Updated nginx configuration test failed${NC}"
    echo "Please check the configuration file for errors"
    exit 1
fi

# Reload nginx
echo -e "${YELLOW}🔄 Reloading nginx...${NC}"
if sudo systemctl reload nginx; then
    echo -e "${GREEN}✅ nginx reloaded successfully${NC}"
elif sudo service nginx reload; then
    echo -e "${GREEN}✅ nginx reloaded successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Could not reload nginx automatically${NC}"
    echo "Please run: sudo systemctl reload nginx (or sudo service nginx reload)"
fi

# Clean up generated config file
rm -f "$NGINX_CONFIG_GENERATED"

echo ""
echo -e "${GREEN}🎉 Nginx setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Configuration Summary:${NC}"
echo "  Domain: $DOMAIN"
echo "  Path: $PATH_PART"
echo "  Full URL: $BASE_URL"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Make sure your SMLS application is running on localhost:8080"
echo "2. Start SMLS with the same BASE_URL"
echo "3. Test the setup"
echo ""
echo -e "${BLUE}🔧 To start SMLS with the same configuration:${NC}"
echo "   export BASE_URL='$BASE_URL'"
echo "   cd $SMLS_DIR"
echo "   ./nginx/start-with-nginx.sh"
echo ""
echo -e "${BLUE}🌐 Your SMLS will be available at:${NC}"
echo "   $BASE_URL"
echo ""
echo -e "${BLUE}🔍 To check nginx status:${NC}"
echo "   sudo systemctl status nginx"
echo ""
echo -e "${BLUE}📝 To view nginx logs:${NC}"
echo "   sudo tail -f /var/log/nginx/access.log"
echo "   sudo tail -f /var/log/nginx/error.log"