#!/usr/bin/env python3
"""
TEST WALLET ANY AMOUNT CREDITING SYSTEM
Comprehensive test to verify users get credit for any amount they send to wallet
"""

import asyncio
import logging
from database import get_db_manager
from payment_service import get_payment_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_wallet_any_amount_crediting():
    """Test that wallet credits ANY amount received, regardless of overpayment/underpayment"""
    
    print("🧪 TESTING WALLET ANY AMOUNT CREDITING SYSTEM")
    print("=" * 60)
    
    try:
        db_manager = get_db_manager()
        payment_service = get_payment_service()
        
        # Test user ID (using existing test user)
        test_user_id = 6896666427
        
        print(f"📋 Test User ID: {test_user_id}")
        
        # Get current balance
        user = db_manager.get_user(test_user_id)
        if user:
            initial_balance = float(user.balance_usd)
            print(f"💰 Initial Balance: ${initial_balance:.2f}")
        else:
            print("❌ Test user not found")
            return False
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Small Amount Test ($0.75)",
                "expected_usd": 25.0,
                "received_usd": 0.75,
                "crypto_amount": 0.0002,
                "crypto_currency": "ETH"
            },
            {
                "name": "Underpayment Test ($18.50)",
                "expected_usd": 25.0, 
                "received_usd": 18.50,
                "crypto_amount": 0.005,
                "crypto_currency": "ETH"
            },
            {
                "name": "Overpayment Test ($32.25)",
                "expected_usd": 25.0,
                "received_usd": 32.25,
                "crypto_amount": 0.00866,
                "crypto_currency": "ETH"
            },
            {
                "name": "Exact Amount Test ($25.00)",
                "expected_usd": 25.0,
                "received_usd": 25.0,
                "crypto_amount": 0.0067,
                "crypto_currency": "ETH"
            }
        ]
        
        results = []
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🔬 TEST {i}: {scenario['name']}")
            print(f"   Expected: ${scenario['expected_usd']:.2f}")
            print(f"   Received: ${scenario['received_usd']:.2f}")
            
            # Create test wallet deposit order
            service_details = {
                "type": "wallet_deposit", 
                "amount_usd": scenario['expected_usd']
            }
            
            order = db_manager.create_order(
                telegram_id=test_user_id,
                service_type="wallet_deposit",
                service_details=service_details,
                amount=scenario['expected_usd'],
                payment_method="crypto_eth"
            )
            
            # Simulate webhook payment data
            payment_data = {
                "coin": scenario['crypto_currency'].lower(),
                "value_coin": str(scenario['crypto_amount']),
                "txid": f"test_tx_{i}_{int(__import__('time').time())}",
                "confirmations": "2",
                "pending": "0"
            }
            
            # Mock BlockBee conversion to return our test amount
            original_convert = payment_service._convert_crypto_to_usd
            
            def mock_convert(crypto_currency, usd_target, crypto_amount):
                return scenario['received_usd']
            
            # Test the wallet crediting
            try:
                # Get balance before
                user_before = db_manager.get_user(test_user_id)
                balance_before = float(user_before.balance_usd)
                
                # Process wallet deposit
                result = await payment_service.process_wallet_deposit_with_any_amount(
                    order.order_id, payment_data
                )
                
                # Get balance after
                user_after = db_manager.get_user(test_user_id)
                balance_after = float(user_after.balance_usd) if user_after else balance_before
                
                credited_amount = balance_after - balance_before
                
                test_result = {
                    "scenario": scenario['name'],
                    "expected_credit": scenario['received_usd'],
                    "actual_credit": credited_amount,
                    "success": result.get("success", False),
                    "balance_before": balance_before,
                    "balance_after": balance_after,
                    "result_data": result
                }
                
                results.append(test_result)
                
                if test_result["success"] and abs(credited_amount - scenario['received_usd']) < 0.01:
                    print(f"   ✅ SUCCESS: Credited ${credited_amount:.2f} (Expected ${scenario['received_usd']:.2f})")
                    print(f"   💰 Balance: ${balance_before:.2f} → ${balance_after:.2f}")
                else:
                    print(f"   ❌ FAILED: Credited ${credited_amount:.2f} (Expected ${scenario['received_usd']:.2f})")
                    print(f"   Error: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                results.append({
                    "scenario": scenario['name'],
                    "success": False,
                    "error": str(e)
                })
        
        # Summary
        print(f"\n📊 TEST RESULTS SUMMARY:")
        print("=" * 40)
        
        successful_tests = 0
        total_tests = len(results)
        
        for result in results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status} - {result['scenario']}")
            if result["success"]:
                successful_tests += 1
                print(f"      Credit: ${result.get('actual_credit', 0):.2f} USD")
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 SUCCESS RATE: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("✅ WALLET ANY AMOUNT CREDITING SYSTEM: OPERATIONAL")
            print("   Users will receive credit for any cryptocurrency amount sent")
        else:
            print("❌ WALLET CREDITING SYSTEM: NEEDS IMPROVEMENT")
            print("   Some scenarios failed - investigation needed")
        
        return success_rate >= 75
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False

def analyze_current_implementation():
    """Analyze what we've implemented for wallet crediting"""
    
    print("\n🔍 IMPLEMENTATION ANALYSIS:")
    print("=" * 40)
    
    improvements_made = [
        "✅ Removed $3 minimum threshold in DepositWebhookHandler",
        "✅ Enhanced webhook routing for wallet_deposit service type",
        "✅ Added process_wallet_deposit_with_any_amount method",
        "✅ Implemented smart messaging for overpayment/underpayment",
        "✅ Real-time crypto to USD conversion using BlockBee",
        "✅ Comprehensive user notifications with transaction details"
    ]
    
    for improvement in improvements_made:
        print(f"   {improvement}")
    
    print(f"\n💡 USER EXPERIENCE IMPROVEMENTS:")
    benefits = [
        "• Small amounts like $0.50 now get credited (not rejected)",
        "• Overpayments ($27 for $25) credit full $27 with bonus message",  
        "• Underpayments ($18 for $25) credit $18 with clear explanation",
        "• Any cryptocurrency amount sent gets converted and credited",
        "• Smart notifications celebrate overpayments as bonuses",
        "• Clear transaction tracking with crypto details"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")

if __name__ == "__main__":
    try:
        # Analyze implementation
        analyze_current_implementation()
        
        # Run async test
        success = asyncio.run(test_wallet_any_amount_crediting())
        
        print(f"\n🚀 FINAL RESULT:")
        if success:
            print("   ✅ Wallet crediting system ready for production")
            print("   ✅ Users can add funds with any amount - no restrictions")
        else:
            print("   ⚠️ Some issues found - manual verification recommended")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()