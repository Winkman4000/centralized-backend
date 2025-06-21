#!/usr/bin/env python3

import os
import sys
import subprocess
import time
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['backend', 'frontend', 'data', 'models']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    print("✓ Directories created")

def check_files():
    """Check if all necessary files exist"""
    required_files = [
        'backend/main.py',
        'frontend/index.html',
        'frontend/app.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✓ All required files present")
    return True

def start_server():
    """Start the FastAPI server"""
    print("\nStarting Centralized NN Backend Server...")
    print("=" * 50)
    print("🧠 Neural Network Management Interface")
    print("📊 Real-time monitoring and logging")
    print("🔧 Token, Layer, and Head management")
    print("📈 Dataset creation and management")
    print("=" * 50)
    print("\nServer will be available at:")
    print("🌐 http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        os.chdir('backend')
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped by user")
    except Exception as e:
        print(f"\n✗ Server error: {e}")

def main():
    print("🚀 Centralized Neural Network Backend")
    print("=" * 40)
    
    # Check and create directories
    create_directories()
    
    # Check if files exist
    if not check_files():
        print("Please ensure all required files are present")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 