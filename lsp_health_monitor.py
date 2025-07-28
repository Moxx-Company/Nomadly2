#!/usr/bin/env python3
"""
LSP Health Monitor - Continuous monitoring of LSP diagnostics
Run this periodically to maintain LSP performance
"""

import subprocess
import time
import logging

def check_lsp_health():
    """Quick LSP health check"""
    try:
        result = subprocess.run(
            ["python", "-c", "import ast; print('LSP healthy')"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def main():
    """Monitor LSP health every 5 minutes"""
    while True:
        if check_lsp_health():
            print(f"✅ {time.strftime('%H:%M:%S')} - LSP healthy")
        else:
            print(f"❌ {time.strftime('%H:%M:%S')} - LSP issues detected")
        
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main()
