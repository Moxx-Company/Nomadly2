#!/usr/bin/env python3
"""
BlockBee Cryptocurrency Status Investigation
==========================================

This script tests which cryptocurrency payment methods are working with BlockBee API.
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
load_dotenv()

BLOCKBEE_API_KEY = os.getenv('BLOCKBEE_API_KEY')

async def test_crypto_payment(crypto_code):
    """Test if a cryptocurrency is available via BlockBee API"""
    try:
        url = f"https://api.blockbee.io/{crypto_code}/create/"
        
        params = {
            'callback': 'https://example.com/webhook',
            'address': 'test-address-check-availability',
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
                elif 'not found' in str(result).lower() or status_code == 404:
                    return 'NOT_SUPPORTED'
                else:
                    return f'ERROR: {result}'
                    
    except Exception as e:
        return f'CONNECTION_ERROR: {e}'

async def main():
    """Test all cryptocurrency methods"""
    
    # Current crypto methods from the bot
    crypto_methods = {
        'btc': 'Bitcoin',
        'eth': 'Ethereum', 
        'usdt_erc20': 'USDT (ERC20)',
        'usdt_trc20': 'USDT (TRC20)',
        'ltc': 'Litecoin',
        'doge': 'Dogecoin',
        'trx': 'TRON',
        'bch': 'Bitcoin Cash',
        'bnb_bsc': 'Binance Coin',
        'dash': 'Dash',
        'monero': 'Monero',
        'polygon': 'Polygon'
    }
    
    print("🔍 BLOCKBEE CRYPTOCURRENCY STATUS INVESTIGATION")
    print("=" * 60)
    print()
    
    working = []
    needs_config = []
    not_working = []
    
    for code, name in crypto_methods.items():
        print(f"Testing {name} ({code})...", end=' ')
        status = await test_crypto_payment(code)
        
        if status == 'WORKING':
            print("✅ WORKING")
            working.append(f"{name} ({code})")
        elif status == 'NEEDS_ADMIN_CONFIG':
            print("⚠️ NEEDS ADMIN CONFIG")
            needs_config.append(f"{name} ({code})")
        else:
            print(f"❌ {status}")
            not_working.append(f"{name} ({code}): {status}")
    
    print()
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ WORKING ({len(working)}):")
    for item in working:
        print(f"   • {item}")
    
    print(f"\n⚠️ NEEDS ADMIN CONFIG ({len(needs_config)}):")
    for item in needs_config:
        print(f"   • {item}")
        
    print(f"\n❌ NOT WORKING ({len(not_working)}):")
    for item in not_working:
        print(f"   • {item}")
    
    print()
    print("🎯 RECOMMENDATION:")
    if working:
        print(f"Keep these {len(working)} working cryptocurrencies in the bot interface")
    if needs_config:
        print(f"Contact BlockBee admin to configure these {len(needs_config)} cryptocurrencies")
    if not_working:
        print(f"Remove or fix these {len(not_working)} non-working cryptocurrencies")

if __name__ == "__main__":
    asyncio.run(main())