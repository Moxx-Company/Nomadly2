#!/usr/bin/env python3
"""
Production Callback Fix Validation Script
Validates that all callback fixes are working with real production data
"""

import asyncio
import logging
from fix_callback_database_queries import (
    get_order_payment_address_by_partial_id,
    get_order_details_for_switch
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_production_callbacks():
    """Test callback fixes with real production order data"""
    
    print("🔧 PRODUCTION CALLBACK FIX VALIDATION")
    print("=" * 50)
    
    # Test orders from production database
    test_order_ids = ["c8d7cca7", "5fe6f9aa", "6b621c9e", "84178e26"]
    user_id = 5590563715
    
    print(f"📋 Testing {len(test_order_ids)} production orders for user {user_id}")
    print()
    
    copy_address_results = []
    switch_payment_results = []
    
    for order_id in test_order_ids:
        print(f"🔄 Testing Order: {order_id}")
        
        # Test 1: Copy Address Functionality
        try:
            address_data = get_order_payment_address_by_partial_id(order_id, user_id)
            if address_data:
                payment_address = address_data.get('payment_address', 'N/A')
                crypto_currency = address_data.get('crypto_currency', 'N/A')
                
                # Validate that we get a proper cryptocurrency address, not order ID
                if payment_address != 'N/A' and len(payment_address) > 10 and payment_address != order_id:
                    copy_address_results.append({
                        'order_id': order_id,
                        'status': '✅ SUCCESS',
                        'address': payment_address[:20] + '...' if len(payment_address) > 20 else payment_address,
                        'crypto': crypto_currency
                    })
                    print(f"  ✅ Copy Address: {crypto_currency} - {payment_address[:20]}...")
                else:
                    copy_address_results.append({
                        'order_id': order_id,
                        'status': '❌ FAILED',
                        'error': f"Invalid address: {payment_address}"
                    })
                    print(f"  ❌ Copy Address: Invalid address - {payment_address}")
            else:
                copy_address_results.append({
                    'order_id': order_id,
                    'status': '❌ FAILED',
                    'error': "No address data found"
                })
                print(f"  ❌ Copy Address: No data found")
        except Exception as e:
            copy_address_results.append({
                'order_id': order_id,
                'status': '❌ ERROR',
                'error': str(e)
            })
            print(f"  ❌ Copy Address: Error - {e}")
        
        # Test 2: Switch Payment Functionality
        try:
            order_data = get_order_details_for_switch(order_id, user_id)
            if order_data:
                amount = order_data.get('amount_usd', 0)
                service = order_data.get('service_type', 'N/A')
                payment_status = order_data.get('payment_status', 'N/A')
                
                switch_payment_results.append({
                    'order_id': order_id,
                    'status': '✅ SUCCESS',
                    'amount': f"${amount:.2f}",
                    'service': service,
                    'payment_status': payment_status
                })
                print(f"  ✅ Switch Payment: ${amount:.2f} - {service} ({payment_status})")
            else:
                switch_payment_results.append({
                    'order_id': order_id,
                    'status': '❌ FAILED',
                    'error': "No order data found"
                })
                print(f"  ❌ Switch Payment: No data found")
        except Exception as e:
            switch_payment_results.append({
                'order_id': order_id,
                'status': '❌ ERROR',
                'error': str(e)
            })
            print(f"  ❌ Switch Payment: Error - {e}")
        
        print()
    
    # Summary Report
    print("📊 PRODUCTION CALLBACK TEST RESULTS")
    print("=" * 50)
    
    # Copy Address Results
    copy_success = len([r for r in copy_address_results if r['status'] == '✅ SUCCESS'])
    print(f"📋 Copy Address Functionality: {copy_success}/{len(test_order_ids)} successful")
    
    for result in copy_address_results:
        if result['status'] == '✅ SUCCESS':
            print(f"  ✅ {result['order_id']}: {result['crypto']} - {result['address']}")
        else:
            print(f"  ❌ {result['order_id']}: {result.get('error', 'Failed')}")
    
    print()
    
    # Switch Payment Results
    switch_success = len([r for r in switch_payment_results if r['status'] == '✅ SUCCESS'])
    print(f"🔄 Switch Payment Functionality: {switch_success}/{len(test_order_ids)} successful")
    
    for result in switch_payment_results:
        if result['status'] == '✅ SUCCESS':
            print(f"  ✅ {result['order_id']}: {result['amount']} - {result['service']} ({result['payment_status']})")
        else:
            print(f"  ❌ {result['order_id']}: {result.get('error', 'Failed')}")
    
    print()
    
    # Overall Status
    total_tests = len(test_order_ids) * 2  # 2 tests per order
    total_success = copy_success + switch_success
    success_rate = (total_success / total_tests) * 100
    
    print(f"🎯 OVERALL PRODUCTION TEST RESULTS")
    print(f"   Total Tests: {total_tests}")
    print(f"   Successful: {total_success}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"🎉 PRODUCTION CALLBACKS FULLY OPERATIONAL!")
        print(f"   All critical callback functionality working with real user data")
    elif success_rate >= 75:
        print(f"⚠️  PRODUCTION CALLBACKS MOSTLY WORKING")
        print(f"   Minor issues detected, most functionality operational")
    else:
        print(f"❌ PRODUCTION CALLBACKS NEED ATTENTION")
        print(f"   Significant issues detected, requires investigation")
    
    return success_rate >= 90

if __name__ == "__main__":
    asyncio.run(test_production_callbacks())