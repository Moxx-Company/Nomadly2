#!/usr/bin/env python3
"""Test script to verify QR code ASCII art display in Nomadly bot"""

import asyncio
from nomadly3_clean_bot import NomadlyCleanBot
import hashlib

def test_qr_generation():
    """Test the QR code ASCII art generation"""
    bot = NomadlyCleanBot()
    
    # Test addresses for different cryptocurrencies
    test_addresses = {
        'btc': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
        'eth': '0xB000B4Ca93042936110d495a1D791E17ce28d52B',
        'ltc': 'LZ6Q3x5y8z9X5v4K3w2J1r8S7t9P5a2b',
        'doge': 'DBXu2kgc3xtvCUWFcxFE3r9hEYgmuaaCyD'
    }
    
    print("Testing QR Code ASCII Art Generation\n" + "="*40)
    
    for crypto, address in test_addresses.items():
        print(f"\n{crypto.upper()} QR Code for: {address}")
        print("-" * 40)
        qr_ascii = bot.generate_payment_qr_ascii(address)
        print(qr_ascii)
        print()
    
    # Test the display format
    print("\nTesting Complete QR Display Format")
    print("="*40)
    
    # Simulate a payment display
    crypto_type = 'btc'
    domain = 'example.com'
    address = test_addresses['btc']
    usd_amount = 49.50
    crypto_amount = 0.00156789
    
    crypto_info = {
        'btc': {'name': 'Bitcoin', 'symbol': '₿'},
        'eth': {'name': 'Ethereum', 'symbol': 'Ξ'},
        'ltc': {'name': 'Litecoin', 'symbol': 'Ł'},
        'doge': {'name': 'Dogecoin', 'symbol': 'Ð'}
    }
    
    crypto_details = crypto_info.get(crypto_type, crypto_info['btc'])
    qr_ascii = bot.generate_payment_qr_ascii(address)
    crypto_display = f"{crypto_amount:.8f} {crypto_type.upper()}"
    
    # Format as it would appear in Telegram
    qr_text = (
        f"📱 QR Code - {crypto_details['name']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{domain}\n"
        f"Amount: ${usd_amount:.2f} ({crypto_display})\n\n"
        f"{qr_ascii}\n\n"
        f"Payment Address:\n"
        f"{address}\n\n"
        f"📲 Scan QR or copy address"
    )
    
    print(qr_text)
    
    # Count lines for mobile optimization check
    lines = qr_text.split('\n')
    print(f"\nTotal lines: {len(lines)}")
    print(f"Mobile optimization: {'✅ Good' if len(lines) <= 25 else '❌ Too many lines'}")

if __name__ == "__main__":
    test_qr_generation()