#!/usr/bin/env python3
"""
Fix all references to use fresh database model names
Replace old model names with fresh database equivalents
"""

import os
import re

def fix_file(filepath):
    """Fix model references in a single file"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace model names
    replacements = {
        'WalletTransaction': 'Transaction',
        'RegisteredDomain': 'Domain',
        'from ..models.domain import RegisteredDomain': 'from ..models.domain import Domain',
        'from ..models.wallet import WalletTransaction, Order': 'from ..models.wallet import Transaction, Order',
        'from ..models.wallet import Transaction, Order\nfrom ..models.user import User': 'from ..models.wallet import Transaction, Order\nfrom ..models.user import User',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Fix type hints
    content = re.sub(r'List\[WalletTransaction\]', 'List[Transaction]', content)
    content = re.sub(r'Optional\[WalletTransaction\]', 'Optional[Transaction]', content)
    content = re.sub(r'List\[RegisteredDomain\]', 'List[Domain]', content)
    content = re.sub(r'Optional\[RegisteredDomain\]', 'Optional[Domain]', content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"No changes needed for {filepath}")

def main():
    """Fix all repository and service files"""
    files_to_fix = [
        'app/repositories/transaction_repo.py',
        'app/repositories/domain_repo.py', 
        'app/repositories/dns_repo.py',
        'app/repositories/user_repo.py',
        'app/services/domain_service.py',
        'app/services/dns_service.py',
        'app/services/wallet_service.py',
        'app/services/user_service.py'
    ]
    
    for filepath in files_to_fix:
        fix_file(filepath)

if __name__ == "__main__":
    main()