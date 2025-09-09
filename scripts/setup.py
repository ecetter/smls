#!/usr/bin/env python3
"""
Social Media Login Service (SMLS) Setup Script
One-click setup for the SMLS application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print the setup banner"""
    print("=" * 60)
    print("🚀 Social Media Login Service (SMLS) - Setup Script")
    print("=" * 60)
    print("Setting up your SMLS application...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    print()

def create_virtual_environment():
    """Create a virtual environment"""
    print("🔧 Creating SMLS virtual environment...")
    
    venv_path = Path("smls_env")
    if venv_path.exists():
        print("✅ SMLS virtual environment already exists")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "smls_env"], check=True)
        print("✅ SMLS virtual environment created successfully")
    except subprocess.CalledProcessError:
        print("❌ Error: Failed to create virtual environment")
        sys.exit(1)
    print()

def get_activation_command():
    """Get the activation command based on the platform"""
    if platform.system() == "Windows":
        return "smls_env\\Scripts\\activate"
    else:
        return "source smls_env/bin/activate"

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine the pip command
    if platform.system() == "Windows":
        pip_cmd = "smls_env\\Scripts\\pip"
    else:
        pip_cmd = "smls_env/bin/pip"
    
    try:
        # Upgrade pip first
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error: Failed to install dependencies")
        sys.exit(1)
    print()

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "sessions",
        "logs",
        "src/static/images"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    print()


def print_completion_message():
    """Print the completion message"""
    activation_cmd = get_activation_command()
    
    print("🎉 Setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Activate the virtual environment:")
    print(f"   {activation_cmd}")
    print()
    print("2. Run the application:")
    print("   python src/app.py")
    print()
    print("3. Open your browser and go to the URL shown when you launch the app")
    print()
    print("4. Configure your OAuth credentials in the setup page")
    print()
    print("📚 For more information, see the README.md file")
    print("=" * 60)

def main():
    """Main setup function"""
    print_banner()
    
    # Change to the script directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    try:
        check_python_version()
        create_virtual_environment()
        install_dependencies()
        create_directories()
        # Environment configuration now handled via command line arguments
        print_completion_message()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
