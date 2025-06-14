#!/usr/bin/env python3
"""
Backend startup script for CareerCompassAI
This script ensures the backend starts from the correct directory
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir / "backend"
    
    # Check if backend directory exists
    if not backend_dir.exists():
        print(f"❌ Backend directory not found: {backend_dir}")
        sys.exit(1)
    
    # Check if main.py exists in backend directory
    main_py = backend_dir / "main.py"
    if not main_py.exists():
        print(f"❌ main.py not found in backend directory: {main_py}")
        sys.exit(1)
    
    print(f"🚀 Starting backend server from: {backend_dir}")
    print(f"📁 Backend directory: {backend_dir}")
    print(f"🐍 Python executable: {sys.executable}")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Start uvicorn server
    try:
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ]
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        print(f"📂 Working directory: {os.getcwd()}")
        print("=" * 50)
        
        # Run the command
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main() 