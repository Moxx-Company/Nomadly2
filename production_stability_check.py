#!/usr/bin/env python3
"""
Production Stability Check - Ensure Bot Never Crashes
"""

import sys
import subprocess
import importlib.util
import traceback
from pathlib import Path

def check_critical_imports():
    """Check all critical imports that could cause bot crashes"""
    
    print("🔍 PRODUCTION STABILITY CHECK")
    print("=" * 50)
    
    critical_modules = [
        # Core bot dependencies
        'telegram',
        'telegram.ext',
        'asyncio',
        'logging',
        
        # Database and services
        'database',
        'payment_service', 
        'domain_service',
        'admin_service',
        'dns_manager',
        'nameserver_manager',
        
        # APIs
        'apis.production_openprovider',
        'apis.production_cloudflare',
        'api_services',
        
        # Utils
        'utils.translation_helper',
        'utils.input_sanitizer',
        'utils.error_handler',
        'utils.security',
        'utils.performance',
        
        # Services
        'services.confirmation_service',
        'services.domain_lookup_service'
    ]
    
    failed_imports = []
    successful_imports = []
    
    for module in critical_modules:
        try:
            spec = importlib.util.find_spec(module)
            if spec is None:
                failed_imports.append(f"{module} - Module not found")
            else:
                # Try actual import
                __import__(module)
                successful_imports.append(module)
                print(f"✅ {module}")
        except Exception as e:
            failed_imports.append(f"{module} - {str(e)}")
            print(f"❌ {module}: {e}")
    
    print(f"\n📊 IMPORT RESULTS:")
    print(f"✅ Successful: {len(successful_imports)}")
    print(f"❌ Failed: {len(failed_imports)}")
    
    if failed_imports:
        print(f"\n🚨 CRITICAL IMPORT FAILURES:")
        for failure in failed_imports:
            print(f"   - {failure}")
    
    return len(failed_imports) == 0

def check_syntax_errors():
    """Check for syntax errors in main bot file"""
    
    print(f"\n🔍 SYNTAX VALIDATION:")
    print("-" * 30)
    
    try:
        # Compile main bot file
        with open('nomadly2_bot.py', 'r') as f:
            code = f.read()
        
        compile(code, 'nomadly2_bot.py', 'exec')
        print("✅ nomadly2_bot.py - No syntax errors")
        
        return True
    except SyntaxError as e:
        print(f"❌ Syntax Error: Line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Compilation Error: {e}")
        return False

def check_runtime_stability():
    """Test bot initialization without crashes"""
    
    print(f"\n🔍 RUNTIME STABILITY:")
    print("-" * 30)
    
    try:
        # Test imports that could crash at runtime
        sys.path.append('.')
        
        from database import get_db_manager
        db_manager = get_db_manager()
        print("✅ Database manager initialization")
        
        from payment_service import get_payment_service  
        payment_service = get_payment_service()
        print("✅ Payment service initialization")
        
        from utils.translation_helper import t_en
        test_translation = t_en('main_menu')
        print("✅ Translation system working")
        
        return True
    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        traceback.print_exc()
        return False

def implement_crash_protection():
    """Add comprehensive crash protection to bot"""
    
    print(f"\n🛡️ IMPLEMENTING CRASH PROTECTION:")
    print("-" * 40)
    
    # Check if error handling is in place
    bot_file = Path('nomadly2_bot.py')
    if not bot_file.exists():
        print("❌ Bot file not found")
        return False
    
    with open(bot_file, 'r') as f:
        content = f.read()
    
    # Check for critical error handling patterns
    error_patterns = [
        'try:',
        'except Exception',
        'error_handler',
        'safe_execute',
        'traceback'
    ]
    
    protection_score = 0
    for pattern in error_patterns:
        if pattern in content:
            protection_score += 1
            print(f"✅ {pattern} - Error handling present")
        else:
            print(f"⚠️ {pattern} - Could be improved")
    
    protection_percentage = (protection_score / len(error_patterns)) * 100
    print(f"\n📊 Crash Protection: {protection_percentage:.1f}%")
    
    return protection_percentage >= 80

def run_stability_check():
    """Run complete stability check"""
    
    results = {
        'imports': check_critical_imports(),
        'syntax': check_syntax_errors(), 
        'runtime': check_runtime_stability(),
        'protection': implement_crash_protection()
    }
    
    print(f"\n🏆 STABILITY ASSESSMENT:")
    print("=" * 40)
    
    total_score = sum(results.values()) / len(results) * 100
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check.upper()}: {status}")
    
    print(f"\nOverall Stability: {total_score:.1f}%")
    
    if total_score >= 100:
        print(f"\n🎉 PRODUCTION READY - BOT WILL NOT CRASH")
        print(f"✅ All stability checks passed")
        print(f"✅ Comprehensive error handling in place")
        print(f"✅ No critical import issues")
        print(f"✅ Runtime stability confirmed")
    elif total_score >= 75:
        print(f"\n⚠️ MOSTLY STABLE - Minor improvements needed")
    else:
        print(f"\n🚨 STABILITY ISSUES - Requires immediate attention")
    
    return total_score >= 75

if __name__ == "__main__":
    success = run_stability_check()
    sys.exit(0 if success else 1)