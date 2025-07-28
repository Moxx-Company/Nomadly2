#!/usr/bin/env python3
"""
Alternative FastAPI dependency installation for Nomadly3
Bypasses uv package manager build conflicts
"""

import subprocess
import sys
import os

def install_fastapi_deps():
    """Install FastAPI dependencies using alternative methods"""
    
    # Method 1: Try direct pip installation in virtual environment
    print("🔧 Attempting FastAPI dependency installation...")
    
    dependencies = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "httpx==0.25.2",
        "pydantic[email]==2.5.0"
    ]
    
    # Try pip install with user flag
    try:
        print("📦 Installing FastAPI dependencies with pip...")
        for dep in dependencies:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "--user", "--upgrade", dep
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully installed: {dep}")
            else:
                print(f"❌ Failed to install {dep}: {result.stderr}")
                
    except Exception as e:
        print(f"❌ Pip installation failed: {e}")
        
    # Method 2: Test installation
    try:
        print("\n🧪 Testing FastAPI installation...")
        import fastapi
        import uvicorn
        import httpx
        import pydantic
        
        print("✅ FastAPI dependencies successfully installed!")
        print(f"   - fastapi: {fastapi.__version__}")
        print(f"   - uvicorn: {uvicorn.__version__}")
        print(f"   - httpx: {httpx.__version__}")
        print(f"   - pydantic: {pydantic.VERSION}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    success = install_fastapi_deps()
    sys.exit(0 if success else 1)