#!/usr/bin/env python3
import os
import ast
import re
from pathlib import Path

def find_python_imports(file_path):
    """Find all imports in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        imports = set()
        
        # Find from X import Y
        from_imports = re.findall(r'from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import', content)
        imports.update(from_imports)
        
        # Find import X
        direct_imports = re.findall(r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)', content, re.MULTILINE)
        imports.update(direct_imports)
        
        return [imp for imp in imports if not imp.startswith(('os', 'sys', 'json', 'time', 'datetime', 'logging', 'asyncio', 'httpx', 'random', 'telegram', 'sqlalchemy', 'psycopg2', 're', 'hashlib', 'secrets', 'string', 'traceback', 'types', 'ipaddress', 'shutil'))]
        
    except Exception as e:
        return []

def get_local_file_path(import_name):
    """Convert import name to potential file path"""
    candidates = [
        f"{import_name}.py",
        f"{import_name.replace('.', '/')}.py",
        f"{import_name.replace('.', '/')}//__init__.py"
    ]
    return candidates

print("🔍 NOMADLY3 PROJECT FILE ANALYSIS")
print("=" * 50)

# Core files
core_files = {
    'nomadly3_clean_bot.py': 'Main bot application',
    'fresh_database.py': 'Database schema and manager'
}

print("\n📋 CORE FILES:")
for file, desc in core_files.items():
    exists = "✅ EXISTS" if os.path.exists(file) else "❌ MISSING"
    print(f"  {file} - {desc} [{exists}]")

# Find dependencies from core files
all_imports = set()
for core_file in core_files.keys():
    if os.path.exists(core_file):
        imports = find_python_imports(core_file)
        all_imports.update(imports)

print(f"\n📦 DEPENDENCIES FOUND IN CORE FILES ({len(all_imports)}):")

# Check which dependencies exist as local files
essential_files = set(core_files.keys())
essential_files.add('background_payment_monitor.py')  # Known essential

for imp in sorted(all_imports):
    candidates = get_local_file_path(imp)
    found = False
    for candidate in candidates:
        if os.path.exists(candidate):
            essential_files.add(candidate)
            print(f"  ✅ {imp} -> {candidate}")
            found = True
            break
    if not found:
        print(f"  ❓ {imp} -> (external or missing)")

print(f"\n🎯 ESSENTIAL FILES IDENTIFIED ({len(essential_files)}):")
for file in sorted(essential_files):
    print(f"  - {file}")

# Count total files
total_py_files = len([f for f in Path('.').rglob('*.py') if not f.is_relative_to('.cache') and not f.is_relative_to('__pycache__')])
removable_count = total_py_files - len(essential_files)

print(f"\n📊 PROJECT CLEANUP SUMMARY:")
print(f"  Total Python files: {total_py_files}")
print(f"  Essential files: {len(essential_files)}")
print(f"  Removable files: ~{removable_count}")
print(f"  Space savings: ~{(removable_count/total_py_files)*100:.1f}%")
