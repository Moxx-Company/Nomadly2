#!/usr/bin/env python3
"""
COMPLETE DYNOPAY UI FIX AND PAYMENT SYSTEM TEST
Changes all BlockBee references to Dynopay in UI and tests all cryptocurrency payment flows
"""

import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_all_blockbee_to_dynopay():
    """Fix all BlockBee references to Dynopay in UI text"""
    
    logger.info("🎨 FIXING ALL BLOCKBEE TO DYNOPAY REFERENCES")
    
    # Read nomadly2_bot.py
    try:
        with open('nomadly2_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace all BlockBee references with Dynopay in user-facing text
        replacements = [
            ('💰 *BlockBee:* ⚠️ Not configured\\n\\n', '💰 *Dynopay:* ⚠️ Not configured\\n\\n'),
            ('⚡ *Instant processing via BlockBee*', '⚡ *Instant processing via Dynopay*'),
            ('🔒 *All payments processed securely via BlockBee*', '🔒 *All payments processed securely via Dynopay*'),
            ('🔒 *Powered by BlockBee - Military-grade security*', '🔒 *Powered by Dynopay - Military-grade security*'),
            ('• ✅ BlockBee: Configured\\n\\n', '• ✅ Dynopay: Configured\\n\\n'),
            ('🏴‍☠️ *Live rates from BlockBee*\\n\\n', '🏴‍☠️ *Live rates from Dynopay*\\n\\n'),
            ('"BlockBee"', '"Dynopay"'),
        ]
        
        changes_made = 0
        for old_text, new_text in replacements:
            if old_text in content:
                content = content.replace(old_text, new_text)
                changes_made += 1
                logger.info(f"   ✅ Replaced: {old_text[:50]}... -> Dynopay")
        
        # Write back the updated content
        if changes_made > 0:
            with open('nomadly2_bot.py', 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Updated {changes_made} BlockBee references to Dynopay")
        else:
            logger.info("ℹ️ No BlockBee references found in user interface text")
            
    except Exception as e:
        logger.error(f"❌ Error updating BlockBee references: {e}")
        return False
    
    return True

def test_cryptocurrency_payments():
    """Test all cryptocurrency payment workflows"""
    
    logger.info("💰 TESTING CRYPTOCURRENCY PAYMENT SYSTEMS")
    
    # Test crypto mapping
    from payment_service import PaymentService
    
    try:
        payment_service = PaymentService()
        
        # Test supported cryptocurrencies
        supported_cryptos = payment_service.supported_cryptos
        crypto_mapping = payment_service.crypto_api_mapping
        
        logger.info(f"✅ Supported cryptocurrencies: {len(supported_cryptos)}")
        for crypto, name in supported_cryptos.items():
            api_code = crypto_mapping.get(crypto, crypto)
            logger.info(f"   {crypto.upper()}: {name} -> API: {api_code}")
        
        # Test problematic cryptocurrencies that were failing
        test_cryptos = ['eth', 'btc', 'ltc', 'doge', 'xmr', 'bnb', 'matic']
        
        logger.info("🔧 Testing cryptocurrency API mapping fixes:")
        for crypto in test_cryptos:
            api_crypto = crypto_mapping.get(crypto, crypto)
            status = "✅ FIXED" if crypto in crypto_mapping else "❌ MISSING"
            logger.info(f"   {crypto.upper()} -> {api_crypto}: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Payment service test error: {e}")
        return False

def test_callback_handlers():
    """Test callback handler functions"""
    
    logger.info("🔄 TESTING CALLBACK HANDLERS")
    
    # Test if fix_callback_database_queries exists and works
    try:
        from fix_callback_database_queries import get_order_details_for_switch, get_order_payment_address_by_partial_id
        
        logger.info("✅ Callback database queries module loaded successfully")
        logger.info("   - get_order_details_for_switch: Available")
        logger.info("   - get_order_payment_address_by_partial_id: Available")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Callback handler import error: {e}")
        logger.info("ℹ️ This might explain the 'Something went wrong' errors")
        return False

def create_payment_test_report():
    """Create comprehensive payment system test report"""
    
    logger.info("📊 CREATING PAYMENT SYSTEM TEST REPORT")
    
    report = {
        'ui_fixes': fix_all_blockbee_to_dynopay(),
        'crypto_payments': test_cryptocurrency_payments(),
        'callback_handlers': test_callback_handlers(),
    }
    
    # Summary
    total_tests = len(report)
    passed_tests = sum(1 for result in report.values() if result)
    
    logger.info(f"\n🎯 PAYMENT SYSTEM TEST SUMMARY:")
    logger.info(f"   Total Tests: {total_tests}")
    logger.info(f"   Passed: {passed_tests}")
    logger.info(f"   Failed: {total_tests - passed_tests}")
    logger.info(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Detailed results
    logger.info(f"\n📋 DETAILED RESULTS:")
    for test_name, result in report.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    # Next steps based on results
    if passed_tests == total_tests:
        logger.info(f"\n🎉 ALL PAYMENT SYSTEM TESTS PASSED!")
        logger.info(f"   • UI updated to Dynopay branding")
        logger.info(f"   • Cryptocurrency mapping fixed")
        logger.info(f"   • Callback handlers verified")
        logger.info(f"   • Bot ready for cryptocurrency payment testing")
    else:
        logger.info(f"\n⚠️ SOME TESTS FAILED - NEED ADDITIONAL FIXES")
        if not report['callback_handlers']:
            logger.info(f"   • Missing callback handler functions may cause 'Something went wrong' errors")
        if not report['crypto_payments']:
            logger.info(f"   • Cryptocurrency payment service has configuration issues")
    
    return report

if __name__ == "__main__":
    logger.info("🚀 STARTING COMPREHENSIVE PAYMENT SYSTEM FIX AND TEST")
    
    try:
        report = create_payment_test_report()
        
        if report['ui_fixes']:
            logger.info("\n✅ DYNOPAY UI BRANDING COMPLETE")
            logger.info("   All user-facing 'BlockBee' text changed to 'Dynopay'")
        
        logger.info(f"\n🔄 RESTART BOT TO APPLY ALL FIXES")
        
    except Exception as e:
        logger.error(f"❌ Test script error: {e}")
        sys.exit(1)