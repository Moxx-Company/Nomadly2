#!/usr/bin/env python3
"""Test script to verify crypto amount calculation in QR code display"""

import asyncio
from nomadly3_clean_bot import NomadlyCleanBot

async def test_crypto_amounts():
    """Test crypto amount calculations"""
    bot = NomadlyCleanBot()
    
    test_amounts = [9.87, 49.50, 99.00, 299.00]
    cryptos = ['btc', 'eth', 'ltc', 'doge']
    
    print("Testing Crypto Amount Calculations for QR Display")
    print("="*50)
    
    for usd_amount in test_amounts:
        print(f"\nUSD Amount: ${usd_amount:.2f}")
        print("-"*30)
        
        for crypto in cryptos:
            crypto_amount, is_realtime = bot.get_crypto_amount(usd_amount, crypto)
            
            # Format display based on crypto type
            if crypto == 'doge' and crypto_amount >= 1:
                display = f"{crypto_amount:.2f} DOGE"
            else:
                display = f"{crypto_amount:.8f} {crypto.upper()}"
            
            status = "🟢 Live" if is_realtime else "🟡 Est"
            print(f"{crypto.upper():4} {status}: {display}")
    
    print("\n" + "="*50)
    print("All crypto amounts calculated successfully!")

if __name__ == "__main__":
    asyncio.run(test_crypto_amounts())