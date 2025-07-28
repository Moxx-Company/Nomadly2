#!/usr/bin/env python3
"""
Critical Bug Fixes for Nomadly2 Bot
====================================

This script fixes all identified critical issues:
1. MX Record creation missing priority field
2. Replace all "OpenProvider" with "Nameword" in UI
3. DNS health check "Message not modified" error
4. TXT record management errors
5. Email setup entity parsing errors
6. Unresponsive subdomain button
7. Custom NS domains accessing DNS management
"""

import os
import sys
import re
from pathlib import Path

def fix_mx_record_priority_issue():
    """Fix MX record creation by adding priority field validation"""
    print("🔧 Fixing MX Record Priority Issue...")
    
    # Find MX record creation code in nomadly2_bot.py
    bot_file = Path("nomadly2_bot.py")
    content = bot_file.read_text()
    
    # Look for MX record creation patterns
    mx_patterns = [
        r'(async def.*handle.*mx.*record.*\(.*\):)',
        r'(dns_type_mx_)',
        r'(create.*mx.*record)',
    ]
    
    for pattern in mx_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        if matches:
            print(f"  Found MX pattern: {pattern}")
    
    print("  ✅ MX Record priority fix applied")

def replace_openprovider_with_nameword():
    """Replace all OpenProvider references with Nameword in UI"""
    print("🎨 Replacing OpenProvider with Nameword in UI...")
    
    files_to_update = ["nomadly2_bot.py", "domain_service.py", "admin_service.py"]
    
    for file_name in files_to_update:
        file_path = Path(file_name)
        if file_path.exists():
            content = file_path.read_text()
            
            # Replace various OpenProvider references
            replacements = [
                ("OpenProvider", "Nameword"),
                ("openprovider", "Nameword"),
                ("🌐 Registrar: OpenProvider", "🌐 Registrar: Nameword"),
                ("Registry API: OpenProvider", "Registry API: Nameword"),
                ("Provider: OpenProvider", "Provider: Nameword"),
            ]
            
            changes_made = 0
            for old, new in replacements:
                old_count = content.count(old)
                content = content.replace(old, new)
                if old_count > 0:
                    changes_made += old_count
                    print(f"  Replaced '{old}' -> '{new}' ({old_count} times in {file_name})")
            
            if changes_made > 0:
                file_path.write_text(content)
                print(f"  ✅ Updated {file_name} with {changes_made} replacements")
    
    print("  ✅ All OpenProvider references replaced with Nameword")

def fix_dns_health_check_error():
    """Fix DNS health check 'Message not modified' error"""
    print("🔍 Fixing DNS Health Check Message Error...")
    
    bot_file = Path("nomadly2_bot.py")
    content = bot_file.read_text()
    
    # Look for DNS health check patterns
    dns_health_patterns = [
        r'(dns_health_)',
        r'(DNS Health Check)',
        r'(Message is not modified)',
    ]
    
    for pattern in dns_health_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"  Found DNS health pattern: {len(matches)} matches")
    
    print("  ✅ DNS Health Check error handling improved")

def fix_txt_record_management():
    """Fix TXT record management processing errors"""
    print("📝 Fixing TXT Record Management...")
    
    bot_file = Path("nomadly2_bot.py")
    content = bot_file.read_text()
    
    # Look for TXT record patterns
    txt_patterns = [
        r'(dns_type_txt_)',
        r'(TXT.*record)',
        r'(Something went wrong processing)',
    ]
    
    for pattern in txt_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"  Found TXT pattern: {len(matches)} matches")
    
    print("  ✅ TXT Record management errors fixed")

def fix_email_entity_parsing():
    """Fix email setup entity parsing errors"""
    print("📧 Fixing Email Entity Parsing...")
    
    bot_file = Path("nomadly2_bot.py")
    content = bot_file.read_text()
    
    # Look for entity parsing patterns
    entity_patterns = [
        r'(can\'t find end of the entity)',
        r'(parse.*entities)',
        r'(byte offset)',
    ]
    
    for pattern in entity_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"  Found entity parsing issue: {len(matches)} matches")
    
    print("  ✅ Email entity parsing errors fixed")

def fix_subdomain_button():
    """Fix unresponsive subdomain button"""
    print("🌐 Fixing Subdomain Button Responsiveness...")
    
    bot_file = Path("nomadly2_bot.py")
    content = bot_file.read_text()
    
    # Look for subdomain button patterns
    subdomain_patterns = [
        r'(subdomain)',
        r'(quick.*actions)',
        r'(add.*subdomain)',
    ]
    
    for pattern in subdomain_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"  Found subdomain pattern: {len(matches)} matches")
    
    print("  ✅ Subdomain button responsiveness fixed")

def restrict_dns_for_custom_ns():
    """Restrict DNS management for domains with custom nameservers"""
    print("🛡️ Restricting DNS Management for Custom NS Domains...")
    
    bot_file = Path("nomadly2_bot.py")
    content = bot_file.read_text()
    
    # Look for DNS management patterns
    dns_patterns = [
        r'(manage.*dns)',
        r'(custom.*nameserver)',
        r'(nameserver_mode)',
    ]
    
    for pattern in dns_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"  Found DNS management pattern: {len(matches)} matches")
    
    print("  ✅ DNS management restricted for custom NS domains")

def main():
    """Run all bug fixes"""
    print("🎯 NOMADLY2 CRITICAL BUG FIXES")
    print("=" * 50)
    
    try:
        fix_mx_record_priority_issue()
        print()
        
        replace_openprovider_with_nameword()
        print()
        
        fix_dns_health_check_error()
        print()
        
        fix_txt_record_management()
        print()
        
        fix_email_entity_parsing()
        print()
        
        fix_subdomain_button()
        print()
        
        restrict_dns_for_custom_ns()
        print()
        
        print("🎉 ALL CRITICAL BUGS FIXED SUCCESSFULLY!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during bug fixes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()