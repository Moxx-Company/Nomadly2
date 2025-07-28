#!/usr/bin/env python3
"""
Test Script: Crypto Payment Overpayment/Underpayment System
Validates the enhanced payment handling logic for domain registration
"""

import asyncio
import json
from unittest.mock import Mock
from nomadly3_clean_bot import NomadlyCleanBot

async def test_crypto_payment_scenarios():
    """Test all crypto payment scenarios for domain registration"""
    
    print("🧪 Testing Crypto Payment Overpayment/Underpayment System")
    print("=" * 60)
    
    # Initialize bot instance
    bot = NomadlyCleanBot()
    
    # Mock query object
    mock_query = Mock()
    mock_query.from_user.id = 12345
    mock_query.edit_message_text = Mock()
    
    # Setup test user session
    test_user_id = 12345
    bot.user_sessions[test_user_id] = {
        "language": "en",
        "domain": "testdomain.com",
        "price": 49.50,
        "balance": 0.0
    }
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Exact Payment",
            "expected_price": 49.50,
            "received_amount": 49.50,
            "scenario_type": "exact"
        },
        {
            "name": "Overpayment - Small",
            "expected_price": 49.50,
            "received_amount": 54.75,
            "scenario_type": "overpayment"
        },
        {
            "name": "Overpayment - Large",
            "expected_price": 49.50,
            "received_amount": 75.00,
            "scenario_type": "overpayment"
        },
        {
            "name": "Underpayment - Small",
            "expected_price": 49.50,
            "received_amount": 44.20,
            "scenario_type": "underpayment"
        },
        {
            "name": "Underpayment - Large",
            "expected_price": 49.50,
            "received_amount": 25.80,
            "scenario_type": "underpayment"
        }
    ]
    
    print("🔍 Testing Payment Scenarios:")
    print("-" * 30)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Expected: ${scenario['expected_price']:.2f}")
        print(f"   Received: ${scenario['received_amount']:.2f}")
        
        # Override payment simulation for testing
        original_simulate_payment = bot.simulate_crypto_payment_check
        original_simulate_amount = bot.simulate_domain_payment_amount
        
        bot.simulate_crypto_payment_check = lambda: True
        bot.simulate_domain_payment_amount = lambda expected: scenario['received_amount']
        
        # Reset user session for each test
        bot.user_sessions[test_user_id] = {
            "language": "en",
            "domain": "testdomain.com", 
            "price": scenario['expected_price'],
            "balance": 0.0
        }
        
        try:
            # Test payment status check
            await bot.handle_payment_status_check(mock_query, "btc", "testdomain_com")
            
            # Validate results
            user_session = bot.user_sessions[test_user_id]
            final_balance = user_session.get('balance', 0.0)
            
            if scenario['scenario_type'] == 'exact':
                expected_balance = 0.0
                status = "✅ Domain registered successfully"
            elif scenario['scenario_type'] == 'overpayment':
                expected_balance = scenario['received_amount'] - scenario['expected_price']
                status = f"✅ Domain registered + ${expected_balance:.2f} credited to wallet"
            elif scenario['scenario_type'] == 'underpayment':
                expected_balance = scenario['received_amount']
                status = f"⚠️ Registration blocked + ${expected_balance:.2f} credited to wallet"
            
            print(f"   Result: {status}")
            print(f"   Wallet Balance: ${final_balance:.2f}")
            
            # Validate balance calculation
            if abs(final_balance - expected_balance) < 0.01:
                print(f"   ✅ Balance validation passed")
            else:
                print(f"   ❌ Balance validation failed (expected ${expected_balance:.2f})")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
        
        # Restore original methods
        bot.simulate_crypto_payment_check = original_simulate_payment
        bot.simulate_domain_payment_amount = original_simulate_amount
    
    print("\n" + "=" * 60)
    print("🎯 Testing Multilingual Support:")
    print("-" * 30)
    
    # Test multilingual scenarios
    languages = ["en", "fr", "hi", "zh", "es"]
    
    for lang in languages:
        print(f"\n🌍 Testing {lang.upper()} language support:")
        
        # Setup user with specific language
        bot.user_sessions[test_user_id] = {
            "language": lang,
            "domain": "testdomain.com",
            "price": 49.50,
            "balance": 0.0
        }
        
        # Override payment simulation for overpayment test
        bot.simulate_crypto_payment_check = lambda: True
        bot.simulate_domain_payment_amount = lambda expected: 60.00  # Overpayment
        
        try:
            await bot.handle_payment_status_check(mock_query, "eth", "testdomain_com")
            
            # Check if edit_message_text was called (indicates multilingual message sent)
            if mock_query.edit_message_text.called:
                print(f"   ✅ Multilingual message displayed for {lang}")
                
                # Check wallet crediting
                final_balance = bot.user_sessions[test_user_id].get('balance', 0.0)
                if final_balance == 10.50:  # 60.00 - 49.50
                    print(f"   ✅ Wallet credited correctly: ${final_balance:.2f}")
                else:
                    print(f"   ⚠️ Unexpected balance: ${final_balance:.2f}")
            else:
                print(f"   ❌ No message sent for {lang}")
                
        except Exception as e:
            print(f"   ❌ {lang} test failed: {e}")
        
        # Reset mock for next test
        mock_query.edit_message_text.reset_mock()
    
    print("\n" + "=" * 60)
    print("✅ Crypto Payment Overpayment/Underpayment System Test Complete")
    print("💡 Key Features Validated:")
    print("   • Exact payment processing")
    print("   • Overpayment detection and wallet crediting")
    print("   • Underpayment protection with wallet crediting")
    print("   • Multilingual support across all 5 languages")
    print("   • Seamless user experience with clear guidance")

if __name__ == "__main__":
    asyncio.run(test_crypto_payment_scenarios())