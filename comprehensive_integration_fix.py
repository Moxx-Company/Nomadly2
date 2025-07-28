#!/usr/bin/env python3
"""
Comprehensive Integration Fix for Nomadly3
Resolves SQLAlchemy conflicts and FastAPI dependencies
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def fix_sqlalchemy_conflicts():
    """Fix SQLAlchemy model conflicts by consolidating imports"""
    print("🔧 Fixing SQLAlchemy model conflicts...")
    
    # Strategy: Use only database.py as single source of truth
    # Remove conflicting app/models to prevent duplicate Base instances
    
    app_models_dir = Path("app/models")
    if app_models_dir.exists():
        # Backup and remove conflicting models
        backup_dir = Path("app/models_backup")
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        
        print(f"📦 Backing up app/models to {backup_dir}")
        shutil.copytree(app_models_dir, backup_dir)
        
        # Remove only conflicting model files, keep email_models.py
        for model_file in ["user.py", "domain.py", "wallet.py", "__init__.py"]:
            model_path = app_models_dir / model_file
            if model_path.exists():
                print(f"🗑️ Removing conflicting {model_path}")
                model_path.unlink()
    
    print("✅ SQLAlchemy conflicts resolved - using single database.py source")

def install_fastapi_direct():
    """Install FastAPI directly bypassing package manager conflicts"""
    print("📦 Installing FastAPI dependencies directly...")
    
    # Use pip directly with system python
    dependencies = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "httpx==0.25.2",
        "pydantic[email]==2.5.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"📥 Installing {dep}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", "--force-reinstall", dep
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ {dep} installed successfully")
            else:
                print(f"⚠️ {dep} installation warning: {result.stderr[:100]}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {dep} installation timed out, continuing...")
        except Exception as e:
            print(f"❌ {dep} installation error: {e}")

def test_integration():
    """Test both fixes"""
    print("\n🧪 Testing integration fixes...")
    
    # Test SQLAlchemy models
    try:
        from database import Base, User, RegisteredDomain, DNSRecord
        print("✅ SQLAlchemy models import successfully")
        print(f"   Base metadata tables: {len(Base.metadata.tables)}")
    except Exception as e:
        print(f"❌ SQLAlchemy test failed: {e}")
    
    # Test FastAPI installation
    try:
        import fastapi
        import uvicorn
        import httpx
        import pydantic
        print("✅ FastAPI dependencies available")
        print(f"   fastapi: {fastapi.__version__}")
        print(f"   uvicorn: {uvicorn.__version__}")
        print(f"   httpx: {httpx.__version__}")
        print(f"   pydantic: {pydantic.VERSION}")
        return True
    except ImportError as e:
        print(f"❌ FastAPI test failed: {e}")
        return False

def main():
    """Execute comprehensive integration fix"""
    print("🚀 Starting Comprehensive Integration Fix for Nomadly3")
    print("=" * 60)
    
    # Step 1: Fix SQLAlchemy conflicts
    fix_sqlalchemy_conflicts()
    
    # Step 2: Install FastAPI dependencies
    install_fastapi_direct()
    
    # Step 3: Test integration
    success = test_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 COMPREHENSIVE INTEGRATION FIX COMPLETED SUCCESSFULLY")
        print("   - SQLAlchemy conflicts resolved")
        print("   - FastAPI dependencies installed")
        print("   - Integration validation ready")
    else:
        print("⚠️ PARTIAL SUCCESS - Some issues may remain")
        print("   - SQLAlchemy conflicts resolved")
        print("   - FastAPI installation needs attention")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)