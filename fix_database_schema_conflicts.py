#!/usr/bin/env python3
"""
Database Schema Conflict Resolution
Fix recurring schema issues by ensuring all model files have consistent column names
"""

import os
import re
from pathlib import Path

def fix_schema_conflicts():
    """Fix all database schema conflicts across all model files"""
    
    print("🔍 ANALYZING DATABASE SCHEMA CONFLICTS")
    print("=" * 60)
    
    # Files to check and fix
    model_files = [
        "./database.py",
        "./models/database.py", 
        "./models/database_models.py",
        "./models/database_models_clean.py"
    ]
    
    fixes_applied = 0
    
    for file_path in model_files:
        if not os.path.exists(file_path):
            continue
            
        print(f"\n📁 Checking: {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: expiry_date -> expires_at
        if 'expiry_date' in content:
            content = content.replace('expiry_date', 'expires_at')
            print(f"  ✅ Fixed: expiry_date -> expires_at")
            fixes_applied += 1
            
        # Fix 2: amount = Column -> amount_usd = Column (only in orders context)
        if 'amount = Column(DECIMAL' in content or 'amount = Column(Float' in content:
            # Only replace in Order class context
            content = re.sub(
                r'(\s+)amount = Column\((DECIMAL|Float|Numeric)[^)]*\)',
                r'\1amount_usd = Column(\2(10, 2), nullable=False)',
                content
            )
            print(f"  ✅ Fixed: amount -> amount_usd in orders")
            fixes_applied += 1
        
        # Fix 3: Ensure user_states table has correct columns
        if 'user_states' in content and 'state_data' in content:
            # Fix models that use state_data instead of data
            content = content.replace('state_data = Column', 'data = Column')
            print(f"  ✅ Fixed: state_data -> data in user_states")
            fixes_applied += 1
            
        # Only write if changes were made
        if content != original_content:
            # Create backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w') as f:
                f.write(original_content)
                
            # Write fixed content
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"  💾 File updated (backup: {backup_path})")
        else:
            print(f"  ✅ No changes needed")
    
    print(f"\n🎯 SCHEMA CONFLICT RESOLUTION COMPLETE")
    print(f"Total fixes applied: {fixes_applied}")
    
    # Verify the main database.py file has correct schema
    print(f"\n🔍 VERIFYING MAIN DATABASE.PY SCHEMA")
    with open('./database.py', 'r') as f:
        main_content = f.read()
    
    schema_issues = []
    if 'expiry_date' in main_content:
        schema_issues.append("❌ Still has expiry_date")
    if 'amount = Column' in main_content and 'orders' in main_content:
        schema_issues.append("❌ Still has amount instead of amount_usd")
    
    if schema_issues:
        print("Issues found:")
        for issue in schema_issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ Main database.py schema is consistent")
        return True

if __name__ == "__main__":
    success = fix_schema_conflicts()
    if success:
        print("\n🚀 All database schema conflicts resolved!")
        print("System should now have consistent column names across all model files.")
    else:
        print("\n⚠️  Some issues remain - manual review required")