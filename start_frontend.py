#!/usr/bin/env python3
"""
Frontend startup script for CareerCompassAI
This script ensures the frontend starts from the correct directory
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    frontend_dir = script_dir / "frontend"
    
    # Check if frontend directory exists
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        sys.exit(1)
    
    # Check if package.json exists in frontend directory
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print(f"❌ package.json not found in frontend directory: {package_json}")
        sys.exit(1)
    
    print(f"🚀 Starting frontend server from: {frontend_dir}")
    print(f"📁 Frontend directory: {frontend_dir}")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Start npm dev server
    try:
        cmd = ["npm", "run", "dev"]
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        print(f"📂 Working directory: {os.getcwd()}")
        print("=" * 50)
        
        # Run the command
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main() 