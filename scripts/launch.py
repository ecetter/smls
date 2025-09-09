#!/usr/bin/env python3
"""
Social Media Login Service (SMLS) Launch Script
Simple script to launch the SMLS application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print the launch banner"""
    print("=" * 50)
    print("🚀 Social Media Login Service (SMLS) - Launching...")
    print("=" * 50)

def check_setup():
    """Check if the application is properly set up"""
    print("🔍 Checking setup...")
    
    # Check if virtual environment exists
    venv_path = Path("smls_env")
    if not venv_path.exists():
        print("❌ SMLS virtual environment not found!")
        print("   Please run the setup script first:")
        print("   python scripts/setup.py")
        return False
    
    # Check if requirements are installed
    if platform.system() == "Windows":
        pip_cmd = "smls_env\\Scripts\\pip"
        python_cmd = "smls_env\\Scripts\\python"
    else:
        pip_cmd = "smls_env/bin/pip"
        python_cmd = "smls_env/bin/python"
    
    try:
        # Check if Flask is installed
        result = subprocess.run([pip_cmd, "show", "flask"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Flask not found in virtual environment!")
            print("   Please run the setup script first:")
            print("   python scripts/setup.py")
            return False
    except FileNotFoundError:
        print("❌ Virtual environment not properly configured!")
        print("   Please run the setup script first:")
        print("   python scripts/setup.py")
        return False
    
    print("✅ Setup check passed")
    return True

def launch_app():
    """Launch the Flask application"""
    print("🚀 Launching OAuth Demo...")
    print()
    
    # Change to the script directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # Determine the Python command
    if platform.system() == "Windows":
        python_cmd = "smls_env\\Scripts\\python"
    else:
        python_cmd = "smls_env/bin/python"
    
    # Set environment variables
    env = os.environ.copy()
    env["FLASK_APP"] = "src/app.py"
    env["FLASK_ENV"] = "development"
    
    try:
        # Get base URL from environment or use default
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        
        print("🌐 Starting web server...")
        print(f"📱 Open your browser and go to: {base_url}")
        print("⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)
        print()
        
        # Launch the Flask app with base URL argument
        subprocess.run([python_cmd, "src/app.py", "--base-url", base_url], env=env)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except FileNotFoundError:
        print("❌ Error: Could not find Python in virtual environment")
        print("   Please run the setup script first:")
        print("   python scripts/setup.py")
    except Exception as e:
        print(f"❌ Error launching application: {e}")

def main():
    """Main launch function"""
    print_banner()
    
    if check_setup():
        launch_app()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
