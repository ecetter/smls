#!/bin/bash

# SMLS Main Setup Script
# Simple entry point for the complete setup and launch process

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if BASE_URL is provided
if [ -z "$BASE_URL" ]; then
    echo "Error: BASE_URL environment variable is required"
    echo ""
    echo "Usage:"
    echo "  export BASE_URL='http://yourdomain.com/yourpath'"
    echo "  ./setup.sh"
    echo ""
    echo "Example:"
    echo "  export BASE_URL='http://example.com/smls'"
    echo "  ./setup.sh"
    exit 1
fi

echo "Starting SMLS Setup..."
echo "Base URL: $BASE_URL"
echo ""

# Run the main setup script
exec "$SCRIPT_DIR/scripts/setup-and-launch.sh"
