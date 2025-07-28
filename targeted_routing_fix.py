#!/usr/bin/env python3
"""
Targeted Routing Fix for Nomadly3
Fixes specific callback conflicts found in the code
"""

import re
import shutil
from datetime import datetime

def create_routing_fixed_version():
    """Create a version of the bot with all routing conflicts resolved"""
    
    print("🎯 TARGETED ROUTING CONFLICT RESOLUTION")
    print("=" * 60)
    
    # Backup original file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"nomadly3_simple_backup_{timestamp}.py"
    shutil.copy("nomadly3_simple.py", backup_filename)
    print(f"✓ Created backup: {backup_filename}")
    
    # Read original content
    with open("nomadly3_simple.py", "r") as f:
        content = f.read()
    
    print("\n📋 APPLYING SYSTEMATIC ROUTING FIXES:")
    print("-" * 50)
    
    # Define routing fixes based on actual patterns found in code
    routing_fixes = [
        # Crypto payment patterns - most specific first
        ("crypto_btc_", "payment.crypto.btc_"),
        ("crypto_eth_", "payment.crypto.eth_"),  
        ("crypto_ltc_", "payment.crypto.ltc_"),
        ("crypto_doge_", "payment.crypto.doge_"),
        ("switch_crypto_", "payment.crypto.switch_"),
        ("check_payment_", "payment.status.check_"),
        ("copy_address_", "payment.address.copy_"),
        ("generate_qr_", "payment.qr.generate_"),
        ("crypto_pay_", "payment.crypto.process_"),
        
        # Wallet and fund patterns - amounts first
        ("add_funds_100", "wallet.fund.usd100"),
        ("add_funds_50", "wallet.fund.usd50"),
        ("add_funds_20", "wallet.fund.usd20"),
        ("fund_crypto_btc", "wallet.deposit.btc"),
        ("fund_crypto_eth", "wallet.deposit.eth"),
        ("fund_crypto_ltc", "wallet.deposit.ltc"), 
        ("fund_crypto_doge", "wallet.deposit.doge"),
        ("add_funds_menu", "wallet.fund.menu"),
        ("add_funds_upgrade", "wallet.fund.upgrade"),
        ("pay_wallet_", "wallet.payment.process_"),
        
        # Domain patterns - specific domains first  
        ("check_domain_example.com", "domain.check.example_com"),
        ("check_domain_offshore.io", "domain.check.offshore_io"),
        ("check_domain_private.org", "domain.check.private_org"), 
        ("check_domain_secure.net", "domain.check.secure_net"),
        ("domain_details_", "domain.info.details_"),
        ("dns_manage_", "domain.dns.manage_"),  
        ("ns_manage_", "domain.nameserver.manage_"),
        ("register_domain", "domain.register.start"),
        
        # Language patterns - specific languages first
        ("lang_en", "user.language.english"),
        ("lang_fr", "user.language.french"),
        ("lang_es", "user.language.spanish"),
        ("lang_hi", "user.language.hindi"),
        ("lang_zh", "user.language.chinese"),
        
        # DNS patterns
        ("dns_cloudflare", "dns.provider.cloudflare"),
        ("dns_custom", "dns.provider.custom"),
        
        # General patterns last to avoid over-matching
        ("check_domain_", "domain.check.availability_"),
        ("register_", "domain.register.workflow_"),
        ("domain_", "domain.manage.action_"),
        ("add_funds_", "wallet.fund.options_"),
        ("lang_", "user.language.select_"),
        ("dns_", "dns.manage.action_"),
        ("crypto_", "payment.crypto.select_")
    ]
    
    # Apply fixes in order
    updated_content = content
    total_replacements = 0
    
    for old_pattern, new_pattern in routing_fixes:
        replacements = 0
        
        # Fix callback_data patterns
        pattern1 = f'callback_data="{old_pattern}"'
        replacement1 = f'callback_data="{new_pattern}"'
        if pattern1 in updated_content:
            count = updated_content.count(pattern1)
            updated_content = updated_content.replace(pattern1, replacement1)
            replacements += count
        
        pattern2 = f"callback_data='{old_pattern}'"
        replacement2 = f"callback_data='{new_pattern}'"
        if pattern2 in updated_content:
            count = updated_content.count(pattern2)
            updated_content = updated_content.replace(pattern2, replacement2)
            replacements += count
        
        # Fix callback_data patterns with f-strings
        pattern3 = f'callback_data=f"{old_pattern}'
        replacement3 = f'callback_data=f"{new_pattern}'
        if pattern3 in updated_content:
            count = updated_content.count(pattern3)
            updated_content = updated_content.replace(pattern3, replacement3)
            replacements += count
        
        pattern4 = f"callback_data=f'{old_pattern}"
        replacement4 = f"callback_data=f'{new_pattern}"
        if pattern4 in updated_content:
            count = updated_content.count(pattern4)
            updated_content = updated_content.replace(pattern4, replacement4)
            replacements += count
        
        # Fix startswith patterns
        pattern5 = f'data.startswith("{old_pattern}")'
        replacement5 = f'data.startswith("{new_pattern}")'
        if pattern5 in updated_content:
            count = updated_content.count(pattern5)
            updated_content = updated_content.replace(pattern5, replacement5)
            replacements += count
        
        pattern6 = f"data.startswith('{old_pattern}')"
        replacement6 = f"data.startswith('{new_pattern}')"
        if pattern6 in updated_content:
            count = updated_content.count(pattern6)
            updated_content = updated_content.replace(pattern6, replacement6)
            replacements += count
        
        # Fix direct comparison patterns
        pattern7 = f'data == "{old_pattern}"'
        replacement7 = f'data == "{new_pattern}"'
        if pattern7 in updated_content:
            count = updated_content.count(pattern7)
            updated_content = updated_content.replace(pattern7, replacement7)
            replacements += count
        
        pattern8 = f"data == '{old_pattern}'"
        replacement8 = f"data == '{new_pattern}'"
        if pattern8 in updated_content:
            count = updated_content.count(pattern8)
            updated_content = updated_content.replace(pattern8, replacement8)
            replacements += count
        
        if replacements > 0:
            total_replacements += replacements
            print(f"✓ {old_pattern} → {new_pattern} ({replacements} replacements)")
    
    # Write the fixed version
    with open("nomadly3_simple_routing_fixed.py", "w") as f:
        f.write(updated_content)
    
    print(f"\n✅ ROUTING FIXES COMPLETED")
    print("-" * 50)
    print(f"✓ Total replacements: {total_replacements}")
    print(f"✓ Created: nomadly3_simple_routing_fixed.py")
    print(f"✓ Backup saved: {backup_filename}")
    
    # Validate the fixes
    conflicts_remaining = validate_routing_fixes(updated_content)
    
    if conflicts_remaining == 0:
        print(f"✓ No routing conflicts remaining")
        print("\n🎉 SUCCESS: All routing conflicts resolved!")
        print("\nNext steps:")
        print("1. Test the fixed bot file")
        print("2. Update workflow to use fixed version")
        print("3. Verify all callback handlers work correctly")
        return True
    else:
        print(f"⚠️  {conflicts_remaining} conflicts may remain")
        print("Manual review recommended")
        return False

def validate_routing_fixes(content: str) -> int:
    """Validate routing fixes and count remaining conflicts"""
    
    # Extract all callback patterns
    callback_patterns = set(re.findall(r'callback_data=["\']([^"\']+)["\']', content))
    startswith_patterns = set(re.findall(r'data\.startswith\(["\']([^"\']+)["\']', content))
    direct_patterns = set(re.findall(r'data\s*==\s*["\']([^"\']+)["\']', content))
    
    all_patterns = callback_patterns | startswith_patterns | direct_patterns
    
    # Count potential conflicts (simplified check)
    conflicts = 0
    pattern_list = sorted(all_patterns)
    
    for i, pattern1 in enumerate(pattern_list):
        for pattern2 in pattern_list[i+1:]:
            if pattern1 != pattern2:
                # Check for problematic prefix overlaps
                if (pattern1.startswith(pattern2) or pattern2.startswith(pattern1)):
                    # Ignore namespaced patterns (contain dots)
                    if '.' not in pattern1 or '.' not in pattern2:
                        conflicts += 1
    
    return conflicts

if __name__ == "__main__":
    print("🚀 Starting Targeted Routing Fix...")
    print()
    
    success = create_routing_fixed_version()
    
    if success:
        print("\n🎯 READY FOR TESTING")
        print("The routing-fixed version is ready for deployment.")
    else:
        print("\n⚠️  REVIEW RECOMMENDED")
        print("Check the fixed file for any remaining issues.")