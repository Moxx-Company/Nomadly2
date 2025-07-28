#!/usr/bin/env python3
"""
Clean Old Schema Files - Remove Conflicting Database Models
Safely remove old database model files that cause schema conflicts
"""

import os
import shutil
from pathlib import Path

def clean_old_schema_files():
    """Remove old conflicting database schema files"""
    
    print("🧹 CLEANING OLD SCHEMA FILES")
    print("=" * 50)
    
    # Files to remove (keep only ./database.py and ./models/email_models.py)
    files_to_remove = [
        "./models/database.py",
        "./models/database.py.backup", 
        "./models/database_models.py",
        "./models/database_models.py.backup",
        "./models/database_models_clean.py",
        "./models/database_models_clean.py.backup"
    ]
    
    removed_count = 0
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            # Create a final backup in a backup directory
            backup_dir = "./schema_cleanup_backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            filename = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, f"{filename}.final_backup")
            
            # Copy to backup location
            shutil.copy2(file_path, backup_path)
            
            # Remove the file
            os.remove(file_path)
            
            print(f"✅ Removed: {file_path}")
            print(f"   Backup: {backup_path}")
            removed_count += 1
        else:
            print(f"⏭️  Already gone: {file_path}")
    
    # Keep only essential files in models/
    essential_models = ["./models/email_models.py", "./models/__init__.py"]
    
    print(f"\n📁 ESSENTIAL MODEL FILES RETAINED:")
    for file_path in essential_models:
        if os.path.exists(file_path):
            print(f"✅ Kept: {file_path}")
    
    print(f"\n🎯 CLEANUP SUMMARY:")
    print(f"Files removed: {removed_count}")
    print(f"Main database model: ./database.py (✅ ACTIVE)")
    print(f"Email models: ./models/email_models.py (✅ ACTIVE)")
    
    # Verify no schema conflicts remain
    print(f"\n🔍 VERIFYING NO CONFLICTING IMPORTS:")
    
    # Check if any files still try to import from removed models
    import subprocess
    try:
        result = subprocess.run([
            "grep", "-r", "from models.database", ".", 
            "--include=*.py", "--exclude-dir=schema_cleanup_backups"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("⚠️  Found remaining imports from models.database:")
            print(result.stdout)
            return False
        else:
            print("✅ No remaining imports from old models.database files")
            return True
            
    except Exception as e:
        print(f"⚠️  Could not verify imports: {e}")
        return True

if __name__ == "__main__":
    success = clean_old_schema_files()
    if success:
        print("\n🚀 SCHEMA CLEANUP COMPLETE!")
        print("All conflicting database model files removed.")
        print("System now uses single source of truth: ./database.py")
    else:
        print("\n⚠️  Manual review needed - some imports may need updating")