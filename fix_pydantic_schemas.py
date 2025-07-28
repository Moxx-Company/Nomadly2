#!/usr/bin/env python3
"""
Fix Pydantic v2 schema syntax across all schema files
"""

import re
import os

def fix_schema_file(filepath):
    """Fix a single schema file for Pydantic v2 compatibility"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix import statements
    content = content.replace('from pydantic import BaseModel, validator', 'from pydantic import BaseModel, field_validator')
    content = content.replace('from pydantic import BaseModel, EmailStr, validator', 'from pydantic import BaseModel, EmailStr, field_validator')
    
    # Fix validator decorators - handle multiple patterns
    content = re.sub(r'@validator\((.*?)\)', r'@field_validator(\1)', content)
    
    # Remove duplicate @classmethod decorators
    content = re.sub(r'@classmethod\s*\n\s*@classmethod', '@classmethod', content)
    
    # Fix function definitions - add @classmethod where missing
    def fix_validator_function(match):
        decorator = match.group(1)
        method_name = match.group(2)
        params = match.group(3)
        
        # Check if @classmethod is already present
        if '@classmethod' in decorator:
            return match.group(0)
        else:
            return f'{decorator}\n    @classmethod\n    def {method_name}({params}'
    
    # Pattern to match validator functions without @classmethod
    content = re.sub(
        r'(@field_validator\([^)]+\))\n\s*def (validate_\w+)\((cls, v)\):',
        fix_validator_function,
        content
    )
    
    # Write back the fixed content
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Fixed {filepath}")

def main():
    """Fix all schema files"""
    schema_files = [
        'app/schemas/user_schemas.py',
        'app/schemas/domain_schemas.py', 
        'app/schemas/wallet_schemas.py',
        'app/schemas/dns_schemas.py',
        'app/schemas/support_schemas.py'
    ]
    
    for filepath in schema_files:
        if os.path.exists(filepath):
            fix_schema_file(filepath)
        else:
            print(f"File not found: {filepath}")

if __name__ == "__main__":
    main()