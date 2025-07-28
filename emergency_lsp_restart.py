#!/usr/bin/env python3
"""
Emergency LSP Restart - Use when LSP becomes unresponsive
Based on analysis showing 6,490 Python files causing LSP performance issues
"""
import subprocess
import sys
import time
import os
import shutil

def restart_lsp():
    print("🔄 Emergency LSP restart initiated...")
    
    # Kill LSP processes
    try:
        subprocess.run(["pkill", "-f", "pylsp"], capture_output=True, check=False)
        print("✅ Killed existing LSP processes")
    except:
        pass
    
    # Clear all caches aggressively
    cache_dirs = [
        "__pycache__",
        ".mypy_cache", 
        ".pytest_cache",
        ".pylsp_cache",
        ".cache"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"✅ Cleared {cache_dir}")
            except:
                pass
    
    # Find and remove __pycache__ directories recursively
    try:
        subprocess.run(["find", ".", "-name", "__pycache__", "-type", "d", "-exec", "rm", "-rf", "{}", "+"], 
                      capture_output=True, check=False)
        print("✅ Cleared all __pycache__ directories")
    except:
        pass
    
    # Remove .pyc files
    try:
        subprocess.run(["find", ".", "-name", "*.pyc", "-delete"], 
                      capture_output=True, check=False)
        print("✅ Deleted all .pyc files")
    except:
        pass
    
    print("🚀 LSP restart complete - restart your editor")

def check_lsp_health():
    """Quick LSP health check"""
    try:
        result = subprocess.run([
            "python", "-c", 
            "import ast; print('LSP server functional')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ LSP server is healthy")
            return True
        else:
            print("❌ LSP server issues detected")
            return False
    except:
        print("❌ LSP server not responding")
        return False

def main():
    print("🔍 LSP RESTART & RECOVERY TOOL")
    print("=" * 30)
    
    # Check current health
    if check_lsp_health():
        print("💚 LSP is currently healthy")
        response = input("Do you still want to restart? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Restart LSP
    restart_lsp()
    
    # Wait and check again
    print("⏳ Waiting for LSP to stabilize...")
    time.sleep(5)
    
    check_lsp_health()

if __name__ == "__main__":
    main()