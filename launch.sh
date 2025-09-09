#!/bin/bash
# Social Media Login Service (SMLS) Launch Script for Linux/Mac

echo "🚀 Social Media Login Service (SMLS) - Launching..."
echo "================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "smls_env" ]; then
    echo "❌ SMLS virtual environment not found!"
    echo "   Please run the setup script first:"
    echo "   python3 scripts/setup.py"
    exit 1
fi

# Activate virtual environment and run the app
echo "🌐 Starting SMLS..."
echo "📱 Open your browser and go to the URL shown below"
echo "⏹️  Press Ctrl+C to stop the server"
echo "================================"
echo ""

source smls_env/bin/activate
python3 src/app.py
