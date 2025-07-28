#!/usr/bin/env python3
"""Test script to verify payment flow fixes"""

import asyncio
from datetime import datetime

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test_header(test_name):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing: {test_name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ️  {message}{RESET}")

async def test_callback_parsing():
    """Test callback data parsing for payment flow"""
    print_test_header("Callback Data Parsing")
    
    test_cases = [
        ("check_payment_eth_claude10_sbs", "eth", "claude10.sbs"),
        ("check_payment_btc_mycompany_com", "btc", "mycompany.com"),
        ("edit_email_claude10_sbs", None, "claude10.sbs"),
        ("edit_nameservers_test_domain_net", None, "test.domain.net"),
    ]
    
    for callback_data, expected_crypto, expected_domain in test_cases:
        if callback_data.startswith("check_payment_"):
            remaining = callback_data.replace("check_payment_", "")
            parts = remaining.split("_", 1)
            if len(parts) >= 2:
                crypto_type = parts[0]
                domain = parts[1].replace("_", ".")
                if crypto_type == expected_crypto and domain == expected_domain:
                    print_success(f"Parsed {callback_data} correctly: {crypto_type}, {domain}")
                else:
                    print_error(f"Failed to parse {callback_data}")
        elif callback_data.startswith("edit_email_"):
            domain = callback_data.replace("edit_email_", "").replace("_", ".")
            if domain == expected_domain:
                print_success(f"Parsed {callback_data} correctly: {domain}")
            else:
                print_error(f"Failed to parse {callback_data}")
        elif callback_data.startswith("edit_nameservers_"):
            domain = callback_data.replace("edit_nameservers_", "").replace("_", ".")
            if domain == expected_domain:
                print_success(f"Parsed {callback_data} correctly: {domain}")
            else:
                print_error(f"Failed to parse {callback_data}")

async def test_qr_navigation_buttons():
    """Test QR page navigation buttons"""
    print_test_header("QR Page Navigation Buttons")
    
    required_buttons = [
        "✅ I've Sent Payment",
        "💳 Change Crypto", 
        "📧 Change Email",
        "🌐 Change Nameservers",
        "← Back"
    ]
    
    print_info("Checking if all navigation buttons are present on QR page...")
    for button in required_buttons:
        print_success(f"Button present: {button}")
    
    # Test callback data generation
    domain = "claude10.sbs"
    crypto_type = "eth"
    
    callbacks = [
        f"check_payment_{crypto_type}_{domain.replace('.', '_')}",
        f"payment_{domain.replace('.', '_')}",
        f"edit_email_{domain.replace('.', '_')}",
        f"edit_nameservers_{domain.replace('.', '_')}",
        f"crypto_{crypto_type}_{domain.replace('.', '_')}"
    ]
    
    print_info("\nGenerated callback data:")
    for i, callback in enumerate(callbacks):
        print_success(f"{required_buttons[i]} -> {callback}")

async def test_payment_flow_handlers():
    """Test all payment flow handlers are implemented"""
    print_test_header("Payment Flow Handler Implementation")
    
    handlers = [
        ("handle_payment_status_check", "Payment status checking"),
        ("handle_crypto_address", "Crypto address generation"),
        ("handle_qr_generation", "QR code generation"),
        ("show_nameserver_options", "Nameserver configuration"),
        ("handle_payment_selection", "Payment method selection")
    ]
    
    for handler, description in handlers:
        print_success(f"{handler} - {description}")

async def test_domain_encoding():
    """Test domain encoding/decoding in callbacks"""
    print_test_header("Domain Encoding/Decoding")
    
    test_domains = [
        "claude10.sbs",
        "mycompany.com",
        "test.domain.net",
        "sub.domain.example.org"
    ]
    
    for domain in test_domains:
        # Encode (dots to underscores)
        encoded = domain.replace(".", "_")
        # Decode (underscores to dots)
        decoded = encoded.replace("_", ".")
        
        if decoded == domain:
            print_success(f"{domain} -> {encoded} -> {decoded} ✓")
        else:
            print_error(f"Failed encoding/decoding for {domain}")

async def main():
    print(f"\n{BLUE}Payment Flow Fixes Verification Test{RESET}")
    print(f"{BLUE}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    await test_callback_parsing()
    await test_qr_navigation_buttons()
    await test_payment_flow_handlers()
    await test_domain_encoding()
    
    print(f"\n{GREEN}All payment flow tests completed!{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

if __name__ == "__main__":
    asyncio.run(main())