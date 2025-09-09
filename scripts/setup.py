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
    """Create a virtual environment with pip included"""
    print("🔧 Creating SMLS virtual environment...")
    
    venv_path = Path("smls_env")
    if venv_path.exists():
        print("✅ SMLS virtual environment already exists")
        # Verify pip is available in existing environment
        if not verify_pip_installation():
            print("⚠️  Pip not found in existing environment, recreating...")
            import shutil
            shutil.rmtree(venv_path)
        else:
            return
    
    try:
        # Create virtual environment (pip is included by default in Python 3.4+)
        subprocess.run([sys.executable, "-m", "venv", "smls_env"], check=True)
        print("✅ SMLS virtual environment created successfully")
        
        # Verify pip installation
        if not verify_pip_installation():
            print("⚠️  Pip not found in virtual environment, attempting to install...")
            if not install_pip_manually():
                print_system_specific_help()
                sys.exit(1)
        else:
            print("✅ Pip verified in virtual environment")
        
    except subprocess.CalledProcessError as e:
        print("❌ Error: Failed to create virtual environment")
        print_system_specific_help()
        sys.exit(1)
    print()

def install_pip_manually():
    """Attempt to install pip manually using various user-level methods"""
    print("   Trying to install pip using ensurepip...")
    try:
        # Try to install pip manually if it's missing
        if platform.system() == "Windows":
            python_cmd = "smls_env\\Scripts\\python"
        else:
            python_cmd = "smls_env/bin/python"
        
        subprocess.run([python_cmd, "-m", "ensurepip", "--upgrade"], 
                      check=True, capture_output=True)
        if verify_pip_installation():
            print("✅ Pip installed successfully using ensurepip")
            return True
    except subprocess.CalledProcessError:
        pass
    
    print("   Trying to install pip using get-pip.py...")
    try:
        # Download get-pip.py directly into the smls_env directory
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        get_pip_path = "smls_env/get-pip.py"
        
        # Use wget to download get-pip.py
        wget_result = subprocess.run(["wget", "-O", get_pip_path, get_pip_url], 
                                   capture_output=True, text=True)
        if wget_result.returncode != 0:
            print(f"   wget failed: {wget_result.stderr}")
            # Fallback to curl if wget is not available
            curl_result = subprocess.run(["curl", "-o", get_pip_path, get_pip_url], 
                                       capture_output=True, text=True)
            if curl_result.returncode != 0:
                print(f"   curl also failed: {curl_result.stderr}")
                raise Exception("Both wget and curl failed to download get-pip.py")
            else:
                print("   Downloaded get-pip.py using curl")
        else:
            print("   Downloaded get-pip.py using wget")
        
        # Run get-pip.py with the virtual environment's Python
        if platform.system() == "Windows":
            python_cmd = "smls_env\\Scripts\\python"
        else:
            python_cmd = "smls_env/bin/python"
        
        subprocess.run([python_cmd, get_pip_path], check=True, capture_output=True)
        
        # Clean up the downloaded file
        os.unlink(get_pip_path)
        
        if verify_pip_installation():
            print("✅ Pip installed successfully using get-pip.py")
            return True
    except Exception as e:
        print(f"   get-pip.py failed: {e}")
        # Clean up get-pip.py if it exists
        try:
            if os.path.exists("smls_env/get-pip.py"):
                os.unlink("smls_env/get-pip.py")
        except:
            pass
    
    print("   Trying to use system pip if available...")
    try:
        # Check if system pip is available and try to use it
        system_pip_result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                         capture_output=True, text=True)
        if system_pip_result.returncode == 0:
            print("   System pip is available, trying to install pip in virtual environment...")
            
            if platform.system() == "Windows":
                python_cmd = "smls_env\\Scripts\\python"
            else:
                python_cmd = "smls_env/bin/python"
            
            # Try to install pip using system pip
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            if platform.system() == "Windows":
                target_path = f"smls_env/Lib/site-packages"
            else:
                target_path = f"smls_env/lib/python{python_version}/site-packages"
            
            subprocess.run([sys.executable, "-m", "pip", "install", "--target", 
                          target_path, "pip"], 
                          check=True, capture_output=True)
            
            if verify_pip_installation():
                print("✅ Pip installed successfully using system pip")
                return True
    except Exception as e:
        print(f"   System pip method failed: {e}")
    
    return False

def print_system_specific_help():
    """Print system-specific help for pip installation issues (user-level solutions only)"""
    print()
    print("❌ Unable to install pip automatically. Here are user-level solutions:")
    print()
    
    system = platform.system().lower()
    if system == "linux":
        print("📋 For Linux systems (user-level solutions):")
        print()
        print("   Option 1 - Use system Python with pip:")
        print("   • Check if pip is available: python3 -m pip --version")
        print("   • If available, recreate environment: rm -rf smls_env && python3 scripts/setup.py")
        print()
        print("   Option 2 - Install Python via user package manager:")
        print("   • Use pyenv: curl https://pyenv.run | bash")
        print("   • Or use conda/miniconda: https://docs.conda.io/en/latest/miniconda.html")
        print()
        print("   Option 3 - Use alternative Python installation:")
        print("   • Download Python from python.org and install in user directory")
        print("   • Or use your system's package manager if you have access")
        print()
        print("   After installing Python with pip, recreate the environment:")
        print("   rm -rf smls_env")
        print("   python3 scripts/setup.py")
        
    elif system == "darwin":  # macOS
        print("📋 For macOS systems (user-level solutions):")
        print()
        print("   Option 1 - Use Homebrew (if available):")
        print("   • brew install python3")
        print("   • Then: rm -rf smls_env && python3 scripts/setup.py")
        print()
        print("   Option 2 - Use pyenv:")
        print("   • curl https://pyenv.run | bash")
        print("   • pyenv install 3.10.12")
        print("   • pyenv global 3.10.12")
        print()
        print("   Option 3 - Download from python.org:")
        print("   • Download Python installer from https://python.org")
        print("   • Install in user directory")
        print()
        print("   After installing Python with pip, recreate the environment:")
        print("   rm -rf smls_env")
        print("   python3 scripts/setup.py")
        
    elif system == "windows":
        print("📋 For Windows systems (user-level solutions):")
        print()
        print("   Option 1 - Use Microsoft Store Python:")
        print("   • Install Python from Microsoft Store (includes pip)")
        print("   • Then: rmdir /s smls_env && python scripts/setup.py")
        print()
        print("   Option 2 - Download from python.org:")
        print("   • Download Python installer from https://python.org")
        print("   • Make sure to check 'Add Python to PATH' during installation")
        print()
        print("   Option 3 - Use conda/miniconda:")
        print("   • Download from https://docs.conda.io/en/latest/miniconda.html")
        print("   • Install in user directory")
        print()
        print("   After installing Python with pip, recreate the environment:")
        print("   rmdir /s smls_env")
        print("   python scripts/setup.py")
    
    else:
        print("📋 For other systems (user-level solutions):")
        print()
        print("   • Install Python with pip using your preferred method")
        print("   • Use pyenv, conda, or download from python.org")
        print("   • Ensure pip is available: python3 -m pip --version")
        print()
        print("   After installing Python with pip, recreate the environment:")
        print("   rm -rf smls_env")
        print("   python3 scripts/setup.py")
    
    print()
    print("💡 Tip: The setup script will automatically try to install pip using")
    print("   get-pip.py if ensurepip is not available, so you may not need")
    print("   to install anything manually.")
    print()

def verify_pip_installation():
    """Verify that pip is properly installed in the virtual environment"""
    try:
        # Determine the pip command
        if platform.system() == "Windows":
            pip_cmd = "smls_env\\Scripts\\pip"
        else:
            pip_cmd = "smls_env/bin/pip"
        
        # Check if pip executable exists and is functional
        result = subprocess.run([pip_cmd, "--version"], 
                              capture_output=True, text=True, check=True)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Verify pip is available before proceeding
    if not verify_pip_installation():
        print("❌ Error: Pip not available in virtual environment")
        print("   Please recreate the virtual environment")
        sys.exit(1)
    
    # Determine the pip command
    if platform.system() == "Windows":
        pip_cmd = "smls_env\\Scripts\\pip"
    else:
        pip_cmd = "smls_env/bin/pip"
    
    try:
        # Upgrade pip first
        print("🔄 Upgrading pip...")
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        print("✅ Pip upgraded successfully")
        
        # Install requirements
        print("📦 Installing project dependencies...")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Failed to install dependencies: {e}")
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
    print("🎉 Setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Launch the application:")
    if platform.system() == "Windows":
        print("   launch.bat")
        print("   OR: python scripts/launch.py")
    else:
        print("   ./launch.sh")
        print("   OR: python3 scripts/launch.py")
    print()
    print("2. Open your browser and go to the URL shown when you launch the app")
    print()
    print("3. Configure your OAuth credentials in the setup page")
    print()
    print("💡 The launch script automatically handles the virtual environment")
    print("   activation, so you don't need to activate it manually.")
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
