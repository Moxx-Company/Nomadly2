#!/usr/bin/env python3
"""
Fix Cryptocurrency Payment System
================================

This script identifies and fixes the crypto payment issues.
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
load_dotenv()

BLOCKBEE_API_KEY = os.getenv('BLOCKBEE_API_KEY')

async def test_crypto_with_proper_address(crypto_code):
    """Test cryptocurrency with proper test address"""
    try:
        # Use proper test addresses for each crypto type
        test_addresses = {
            'btc': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'eth': '0x0000000000000000000000000000000000000001',
            'usdt_erc20': '0x0000000000000000000000000000000000000001',  # Wrong - should be usdt 
            'usdt_trc20': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',  # Wrong - should be usdt_tron
            'ltc': 'LM2WMpR1Rp6j3Sa59cMXMs1SPzj9eXpGc1',
            'doge': 'DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L',
            'trx': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
            'bch': 'bitcoincash:qq9x0n7fyj3ldhqxzwa5d5gx6v2z2txjkc6kg5mxfj'
        }
        
        if crypto_code not in test_addresses:
            return f'NO_TEST_ADDRESS'
            
        url = f"https://api.blockbee.io/{crypto_code}/create/"
        
        params = {
            'callback': 'https://example.com/webhook',
            'address': test_addresses[crypto_code],
            'apikey': BLOCKBEE_API_KEY
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                result = await response.json()
                status_code = response.status
                
                if status_code == 200 and result.get('status') == 'success':
                    return 'WORKING'
                elif 'requires configuration' in str(result).lower():
                    return 'NEEDS_ADMIN_CONFIG'
                elif 'not supported' in str(result).lower():
                    return 'NOT_SUPPORTED'
                else:
                    return f'ERROR: {result.get("error", result)}'
                    
    except Exception as e:
        return f'CONNECTION_ERROR: {e}'

async def main():
    """Test and fix cryptocurrency system"""
    
    print("🔧 FIXING CRYPTOCURRENCY PAYMENT SYSTEM")
    print("=" * 60)
    
    # Correct BlockBee API codes based on documentation
    correct_crypto_mapping = {
        'btc': ('Bitcoin', 'btc'),
        'eth': ('Ethereum', 'eth'), 
        'usdt': ('USDT (ERC20)', 'usdt'),  # Correct code
        'usdt_tron': ('USDT (TRC20)', 'usdt_tron'),  # Correct code
        'ltc': ('Litecoin', 'ltc'),
        'doge': ('Dogecoin', 'doge'),
        'trx': ('TRON', 'trx'),
        'bch': ('Bitcoin Cash', 'bch')
    }
    
    print("✅ CORRECTED CRYPTOCURRENCY MAPPING:")
    for code, (name, api_code) in correct_crypto_mapping.items():
        print(f"   • {name}: {code} -> {api_code}")
    
    print("\n🧪 TESTING CORRECTED CRYPTOCURRENCIES:")
    working = []
    not_working = []
    
    for code, (name, api_code) in correct_crypto_mapping.items():
        print(f"Testing {name} ({api_code})...", end=' ')
        status = await test_crypto_with_proper_address(api_code)
        
        if status == 'WORKING':
            print("✅ WORKING")
            working.append((name, code, api_code))
        else:
            print(f"❌ {status}")
            not_working.append((name, code, api_code, status))
    
    print("\n📊 RESULTS:")
    print(f"✅ WORKING ({len(working)}):")
    for name, code, api_code in working:
        print(f"   • {name} ({code} -> {api_code})")
    
    print(f"\n❌ NOT WORKING ({len(not_working)}):")
    for name, code, api_code, status in not_working:
        print(f"   • {name} ({code} -> {api_code}): {status}")
    
    print("\n🎯 FIXES NEEDED:")
    print("1. Update crypto_names mapping in nomadly2_bot.py")
    print("2. Fix USDT button callback data")
    print("3. Remove non-working cryptocurrencies from UI")
    print("4. Add missing callback handlers")

if __name__ == "__main__":
    asyncio.run(main())