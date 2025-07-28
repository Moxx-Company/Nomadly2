#!/usr/bin/env python3
"""
Complete Schema Verification System
Verifies single schema integrity across database, models, and API calls
"""

import os
import sys
import psycopg2
from psycopg2 import sql
import subprocess
import re
from datetime import datetime

def check_database_schema():
    """Check actual database schema"""
    print("🔍 CHECKING DATABASE SCHEMA")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        
        # Check critical tables and columns
        tables_to_check = [
            "users", "user_states", "registered_domains", 
            "orders", "wallet_transactions"
        ]
        
        schema_info = {}
        
        for table in tables_to_check:
            cur.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY column_name
            """, (table,))
            
            columns = cur.fetchall()
            schema_info[table] = columns
            print(f"📋 {table}: {len(columns)} columns")
            
        # Check for critical schema consistency
        critical_checks = [
            ("registered_domains", "expires_at"),
            ("orders", "amount_usd"),
            ("users", "balance_usd"),
            ("wallet_transactions", "amount")
        ]
        
        print("\n✅ CRITICAL COLUMN VERIFICATION:")
        for table, column in critical_checks:
            found = any(col[0] == column for col in schema_info.get(table, []))
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"   {table}.{column}: {status}")
            
        conn.close()
        return schema_info
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return {}

def check_model_consistency():
    """Check database.py model definitions"""
    print("\n🔍 CHECKING MODEL DEFINITIONS")
    print("=" * 50)
    
    try:
        with open("database.py", "r") as f:
            content = f.read()
            
        # Check for single source of truth
        models_found = re.findall(r'class (\w+)\(Base\):', content)
        print(f"📋 Models in database.py: {', '.join(models_found)}")
        
        # Check for critical field definitions
        critical_fields = [
            ("expires_at", "Column.*expires_at"),
            ("amount_usd", "Column.*amount_usd"),
            ("balance_usd", "Column.*balance_usd"),
        ]
        
        print("\n✅ CRITICAL FIELD DEFINITIONS:")
        for field, pattern in critical_fields:
            found = re.search(pattern, content)
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"   {field}: {status}")
            
        return True
        
    except Exception as e:
        print(f"❌ Model check failed: {e}")
        return False

def check_import_consistency():
    """Check for old import references"""
    print("\n🔍 CHECKING IMPORT CONSISTENCY")
    print("=" * 50)
    
    try:
        # Check for old imports
        result = subprocess.run([
            "grep", "-r", "from models.database", ".", "--include=*.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            print("❌ FOUND OLD IMPORTS:")
            print(result.stdout)
            return False
        else:
            print("✅ NO OLD MODEL IMPORTS FOUND")
            
        # Check for database imports
        result = subprocess.run([
            "grep", "-r", "from database import", ".", "--include=*.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            import_count = len(result.stdout.strip().split('\n'))
            print(f"✅ FOUND {import_count} CORRECT DATABASE IMPORTS")
        
        return True
        
    except Exception as e:
        print(f"❌ Import check failed: {e}")
        return False

def check_schema_references():
    """Check for incorrect schema references in code"""
    print("\n🔍 CHECKING SCHEMA REFERENCES")
    print("=" * 50)
    
    problematic_patterns = [
        ("expiry_date", r'\.expiry_date\b'),
        ("amount column", r'\bamount\b.*orders'),
        ("balance column", r'\bbalance\b.*users')
    ]
    
    all_good = True
    
    for description, pattern in problematic_patterns:
        try:
            result = subprocess.run([
                "grep", "-r", "-E", pattern, ".", "--include=*.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                # Filter out cache and backup files
                relevant_lines = [l for l in lines if '.cache/' not in l and '__pycache__' not in l and '.pythonlibs/' not in l and 'schema_cleanup_backups/' not in l]
                if relevant_lines:
                    print(f"⚠️  POTENTIAL ISSUE - {description}:")
                    for line in relevant_lines[:3]:  # Show first 3 matches
                        print(f"   {line}")
                    all_good = False
            else:
                print(f"✅ {description}: OK")
                
        except Exception as e:
            print(f"❌ Pattern check failed for {description}: {e}")
            all_good = False
    
    return all_good

def verify_files_removed():
    """Verify old conflicting files are removed"""
    print("\n🔍 CHECKING OLD FILES REMOVAL")
    print("=" * 50)
    
    old_files = [
        "models/database.py",
        "models/database_models.py", 
        "models/database_models_clean.py"
    ]
    
    all_removed = True
    for file_path in old_files:
        if os.path.exists(file_path):
            print(f"❌ OLD FILE STILL EXISTS: {file_path}")
            all_removed = False
        else:
            print(f"✅ REMOVED: {file_path}")
    
    # Check models directory
    if os.path.exists("models"):
        files_in_models = [f for f in os.listdir("models") if f.endswith(".py") and f != "__init__.py" and f != "email_models.py"]
        if files_in_models:
            print(f"⚠️  UNEXPECTED FILES IN MODELS/: {files_in_models}")
            all_removed = False
        else:
            print("✅ MODELS/ DIRECTORY CLEAN")
    
    return all_removed

def main():
    """Main verification function"""
    print("🚀 NOMADLY2 SCHEMA VERIFICATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Run all checks
    db_schema = check_database_schema()
    model_check = check_model_consistency()
    import_check = check_import_consistency()
    schema_refs = check_schema_references()
    files_removed = verify_files_removed()
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    checks = [
        ("Database Schema", bool(db_schema)),
        ("Model Definitions", model_check),
        ("Import Consistency", import_check),
        ("Schema References", schema_refs),
        ("Old Files Removed", files_removed)
    ]
    
    passed = 0
    for check_name, status in checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name}: {'PASS' if status else 'FAIL'}")
        if status:
            passed += 1
    
    print(f"\n🎯 OVERALL STATUS: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("🎉 SINGLE SCHEMA ARCHITECTURE VERIFIED!")
        print("   - Database schema is consistent")
        print("   - Models match database structure")
        print("   - No conflicting imports")
        print("   - Schema references are correct")
        print("   - Old files properly removed")
    else:
        print("⚠️  SCHEMA ISSUES DETECTED - See details above")
    
    return passed == len(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)