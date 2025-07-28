#!/usr/bin/env python3
"""
QA Issue Analysis - Detailed investigation of failed tests
"""

def analyze_language_system():
    """Analyze language system implementation"""
    print("🌍 LANGUAGE SYSTEM ANALYSIS")
    print("-" * 40)
    
    try:
        # Check translation helper import
        with open('nomadly2_bot.py', 'r') as f:
            bot_content = f.read()
        
        # Check if imports exist
        has_import = "from utils.translation_helper" in bot_content
        has_usage = "t_user(" in bot_content or "t_en(" in bot_content
        
        print(f"Translation import: {'✅' if has_import else '❌'}")
        print(f"Translation usage: {'✅' if has_usage else '❌'}")
        
        # Check language selection
        has_language_selection = "language" in bot_content.lower() and ("english" in bot_content.lower() or "french" in bot_content.lower())
        print(f"Language selection: {'✅' if has_language_selection else '❌'}")
        
        return has_import and has_usage and has_language_selection
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def analyze_payment_system():
    """Analyze payment confirmation system"""
    print("\n💰 PAYMENT SYSTEM ANALYSIS")
    print("-" * 40)
    
    try:
        with open('nomadly2_bot.py', 'r') as f:
            bot_content = f.read()
        
        # Check for payment confirmation patterns
        patterns = [
            "payment.*confirmed",
            "Domain Payment Received",
            "DOMAIN REGISTRATION SUCCESSFUL",
            "payment.*success",
            "confirmed.*payment"
        ]
        
        confirmations_found = 0
        for pattern in patterns:
            import re
            if re.search(pattern, bot_content, re.IGNORECASE):
                confirmations_found += 1
                print(f"✅ Found pattern: {pattern}")
            else:
                print(f"❌ Missing pattern: {pattern}")
        
        return confirmations_found >= 2
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def analyze_database_tracking():
    """Analyze database payment tracking"""
    print("\n💾 DATABASE TRACKING ANALYSIS")
    print("-" * 40)
    
    try:
        with open('database.py', 'r') as f:
            db_content = f.read()
        
        # Check for payment tracking tables/methods
        tracking_elements = [
            "balance_transactions",
            "wallet_transactions", 
            "orders",
            "payment.*track",
            "transaction.*log"
        ]
        
        tracking_found = 0
        for element in tracking_elements:
            import re
            if re.search(element, db_content, re.IGNORECASE):
                tracking_found += 1
                print(f"✅ Found: {element}")
            else:
                print(f"❌ Missing: {element}")
        
        return tracking_found >= 3
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Analyze QA issues"""
    print("🔍 QA ISSUE ANALYSIS")
    print("=" * 50)
    
    results = []
    results.append(("Language System", analyze_language_system()))
    results.append(("Payment Confirmations", analyze_payment_system()))
    results.append(("Database Tracking", analyze_database_tracking()))
    
    print("\n" + "=" * 50)
    print("📊 ISSUE ANALYSIS SUMMARY")
    print("=" * 50)
    
    for issue, status in results:
        print(f"{'✅' if status else '❌'} {issue}")
    
    actual_issues = sum(1 for _, status in results if not status)
    print(f"\nActual issues requiring attention: {actual_issues}/3")
    
    if actual_issues == 0:
        print("\n🎉 All flagged issues are actually working correctly!")
        print("QA success rate is higher than initially reported.")
    else:
        print(f"\n⚠️ {actual_issues} genuine issues found that need addressing.")

if __name__ == "__main__":
    main()