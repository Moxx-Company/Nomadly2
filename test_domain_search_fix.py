#!/usr/bin/env python3
"""Quick test to verify domain search variable fix"""

# Test that the variable name is correct in the file
with open('nomadly3_clean_bot.py', 'r') as f:
    content = f.read()
    
print("Checking domain search fix...")
print("="*50)

# Check if the old incorrect variable is still there
if 'domain_search' in content and 'check_trustee_requirement(domain_search)' in content:
    print("❌ FAIL: Old variable 'domain_search' still found")
else:
    print("✅ PASS: Old variable 'domain_search' removed")

# Check if the correct variable is used
if 'check_trustee_requirement(full_domain)' in content:
    print("✅ PASS: Correct variable 'full_domain' is used")
else:
    print("❌ FAIL: Correct variable 'full_domain' not found")

# Count occurrences
import re
trustee_calls = re.findall(r'check_trustee_requirement\([^)]+\)', content)
print(f"\nFound {len(trustee_calls)} calls to check_trustee_requirement:")
for i, call in enumerate(trustee_calls, 1):
    print(f"  {i}. {call}")

print("\n" + "="*50)
print("Fix verification complete!")