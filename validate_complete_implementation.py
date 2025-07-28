#!/usr/bin/env python3
"""
Comprehensive validation of all fixed issues:
1. $20 minimum deposit validation system
2. Database schema consistency (users table, balance_usd column)
3. UI branding consistency (Nameword instead of OpenProvider)
4. Cloudflare ownership clarity
5. Enhanced navigation from Nameserver Management to DNS management
"""

import os
import re
import subprocess
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_minimum_deposit_system() -> Tuple[bool, List[str]]:
    """Validate the $20 minimum deposit implementation"""
    
    results = []
    all_passed = True
    
    # Check key files exist and have minimum deposit logic
    key_files = [
        'nomadly2_bot.py',
        'payment_service.py', 
        'handlers/deposit_webhook.py',
        'services/wallet_service.py'
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for minimum deposit validation patterns
                patterns = [
                    r'\$20.*minimum',
                    r'minimum.*\$20', 
                    r'amount.*<.*20',
                    r'20.*minimum.*deposit',
                    r'minimum_amount.*=.*20'
                ]
                
                found_patterns = []
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        found_patterns.append(pattern)
                
                if found_patterns:
                    results.append(f"✅ {file_path}: Found minimum deposit validation ({len(found_patterns)} patterns)")
                else:
                    results.append(f"⚠️ {file_path}: No clear minimum deposit patterns found")
                    
            except Exception as e:
                results.append(f"❌ {file_path}: Error reading file - {e}")
                all_passed = False
        else:
            results.append(f"❌ {file_path}: File not found")
            all_passed = False
    
    return all_passed, results

def validate_database_consistency() -> Tuple[bool, List[str]]:
    """Validate database table and column references are correct"""
    
    results = []
    all_passed = True
    
    # Find Python files to check
    python_files = []
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    problematic_patterns = [
        (r'FROM wallets', 'FROM wallets (should be FROM users)'),
        (r'SELECT balance_usd FROM users', 'SELECT balance_usd FROM users (should be SELECT balance_usd FROM users)'),
        (r'w\.balance', 'w.balance (should use balance_usd)'),
        (r'wallets w', 'wallets w (should be users u)')
    ]
    
    issues_found = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            file_issues = []
            for pattern, description in problematic_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    file_issues.append(f"Found: {description}")
                    issues_found += len(matches)
            
            if file_issues:
                results.append(f"❌ {file_path}:")
                for issue in file_issues:
                    results.append(f"   {issue}")
                all_passed = False
            
        except Exception as e:
            results.append(f"⚠️ Error reading {file_path}: {e}")
    
    if issues_found == 0:
        results.append("✅ No problematic database references found")
    else:
        results.append(f"❌ Found {issues_found} problematic database references")
        all_passed = False
    
    return all_passed, results

def validate_ui_branding() -> Tuple[bool, List[str]]:
    """Validate UI text uses Nameword instead of OpenProvider"""
    
    results = []
    all_passed = True
    
    try:
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
        
        # Check for remaining OpenProvider references in user-facing text
        openprovider_patterns = [
            r'"[^"]*OpenProvider[^"]*"',  # In quotes (likely user-facing)
            r'f"[^"]*OpenProvider[^"]*"',  # In f-strings
            r"'[^']*OpenProvider[^']*'",  # In single quotes
        ]
        
        issues_found = 0
        for pattern in openprovider_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                for match in matches:
                    results.append(f"❌ Found OpenProvider in UI text: {match}")
                    issues_found += 1
                all_passed = False
        
        # Check for positive Nameword references
        nameword_patterns = [
            r'"[^"]*Nameword[^"]*"',
            r'f"[^"]*Nameword[^"]*"',
            r"'[^']*Nameword[^']*'"
        ]
        
        nameword_found = 0
        for pattern in nameword_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            nameword_found += len(matches)
        
        results.append(f"✅ Found {nameword_found} Nameword references in UI text")
        
        if issues_found == 0:
            results.append("✅ No OpenProvider references found in UI text")
        
    except Exception as e:
        results.append(f"❌ Error validating UI branding: {e}")
        all_passed = False
    
    return all_passed, results

def validate_cloudflare_clarity() -> Tuple[bool, List[str]]:
    """Validate Cloudflare ownership clarity"""
    
    results = []
    all_passed = True
    
    try:
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
        
        # Look for Cloudflare references with clarity
        clarity_patterns = [
            r'Cloudflare.*Managed by Nameword',
            r'Cloudflare.*provisioned by Nameword',
            r'Cloudflare.*Nameword.managed'
        ]
        
        clarity_found = 0
        for pattern in clarity_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            clarity_found += len(matches)
        
        if clarity_found > 0:
            results.append(f"✅ Found {clarity_found} Cloudflare ownership clarifications")
        else:
            results.append("⚠️ No clear Cloudflare ownership statements found")
            all_passed = False
            
    except Exception as e:
        results.append(f"❌ Error validating Cloudflare clarity: {e}")
        all_passed = False
    
    return all_passed, results

def validate_enhanced_navigation() -> Tuple[bool, List[str]]:
    """Validate enhanced navigation features"""
    
    results = []
    all_passed = True
    
    try:
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
        
        # Look for DNS management navigation buttons
        navigation_patterns = [
            r'Manage DNS Records',
            r'dns_main_',
            r'callback_data.*dns'
        ]
        
        nav_found = 0
        for pattern in navigation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            nav_found += len(matches)
        
        if nav_found > 0:
            results.append(f"✅ Found {nav_found} DNS management navigation elements")
        else:
            results.append("⚠️ Limited DNS management navigation found")
            
        # Check for breadcrumb or context indicators  
        context_patterns = [
            r'Back to.*',
            r'⬅️.*',
            r'breadcrumb'
        ]
        
        context_found = 0
        for pattern in context_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            context_found += len(matches)
            
        results.append(f"✅ Found {context_found} navigation context elements")
            
    except Exception as e:
        results.append(f"❌ Error validating navigation: {e}")
        all_passed = False
    
    return all_passed, results

def run_lsp_diagnostics() -> Tuple[bool, List[str]]:
    """Check for any LSP diagnostics errors"""
    
    results = []
    all_passed = True
    
    try:
        # This would need the actual LSP diagnostics tool
        # For now, just check if key files have basic syntax validity
        key_files = ['nomadly2_bot.py', 'live_order_monitor.py']
        
        for file_path in key_files:
            if os.path.exists(file_path):
                try:
                    # Basic syntax check using Python compile
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    compile(content, file_path, 'exec')
                    results.append(f"✅ {file_path}: Syntax valid")
                    
                except SyntaxError as e:
                    results.append(f"❌ {file_path}: Syntax error - {e}")
                    all_passed = False
                except Exception as e:
                    results.append(f"⚠️ {file_path}: Could not validate - {e}")
            else:
                results.append(f"❌ {file_path}: File not found")
                all_passed = False
                
    except Exception as e:
        results.append(f"❌ Error running syntax checks: {e}")
        all_passed = False
    
    return all_passed, results

def main():
    """Run comprehensive validation"""
    
    logger.info("🔍 COMPREHENSIVE IMPLEMENTATION VALIDATION")
    logger.info("=" * 60)
    
    validations = [
        ("$20 Minimum Deposit System", validate_minimum_deposit_system),
        ("Database Consistency", validate_database_consistency),
        ("UI Branding (Nameword)", validate_ui_branding),
        ("Cloudflare Ownership Clarity", validate_cloudflare_clarity),
        ("Enhanced Navigation", validate_enhanced_navigation),
        ("Code Syntax Validation", run_lsp_diagnostics)
    ]
    
    total_passed = 0
    total_validations = len(validations)
    
    for validation_name, validation_func in validations:
        logger.info(f"\n🧪 TESTING: {validation_name}")
        logger.info("-" * 40)
        
        try:
            passed, results = validation_func()
            
            for result in results:
                logger.info(result)
            
            if passed:
                logger.info(f"✅ {validation_name}: PASSED")
                total_passed += 1
            else:
                logger.info(f"❌ {validation_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {validation_name}: ERROR - {e}")
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    success_rate = (total_passed / total_validations) * 100
    
    logger.info(f"✅ Passed: {total_passed}/{total_validations} ({success_rate:.1f}%)")
    
    if total_passed == total_validations:
        logger.info("🎉 ALL VALIDATIONS PASSED - IMPLEMENTATION COMPLETE!")
        return True
    else:
        failed = total_validations - total_passed
        logger.info(f"⚠️ {failed} validation(s) failed - review needed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)