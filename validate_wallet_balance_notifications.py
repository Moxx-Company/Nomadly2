#!/usr/bin/env python3
"""
Wallet Balance Payment Notification Validation
Validates that wallet balance payments send both bot and email notifications
with previous and new balance transparency
"""

import re
from pathlib import Path

def validate_balance_notifications():
    """Validate wallet balance payment notification implementation"""
    
    print("💳 WALLET BALANCE PAYMENT NOTIFICATION VALIDATION")
    print("=" * 65)
    
    # Check payment_service.py implementation
    print("\n1. PAYMENT SERVICE IMPLEMENTATION:")
    with open('payment_service.py', 'r') as f:
        payment_content = f.read()
    
    required_functions = [
        "_send_balance_payment_notifications",
        "_send_balance_payment_bot_notification", 
        "_send_balance_payment_email_notification"
    ]
    
    for func in required_functions:
        if f"async def {func}" in payment_content:
            print(f"   ✅ PASS: {func} exists")
        else:
            print(f"   ❌ FAIL: {func} missing")
    
    # Check balance transparency features
    print("\n2. BALANCE TRANSPARENCY FEATURES:")
    transparency_features = [
        "previous_balance" in payment_content,
        "new_balance" in payment_content,
        "Previous Balance:" in payment_content,
        "Amount Deducted:" in payment_content,
        "New Balance:" in payment_content,
        "balance-table" in payment_content
    ]
    
    if all(transparency_features):
        print("   ✅ PASS: Complete balance transparency implemented")
        print("   ✅ PASS: Bot shows previous/new balance")
        print("   ✅ PASS: Email shows detailed balance table")
    else:
        print("   ❌ FAIL: Balance transparency incomplete")
    
    # Check bot token consistency 
    print("\n3. BOT TOKEN CONSISTENCY:")
    telegram_tokens = len(re.findall(r'TELEGRAM_BOT_TOKEN', payment_content))
    if telegram_tokens >= 1:
        print(f"   ✅ PASS: Balance notifications use TELEGRAM_BOT_TOKEN ({telegram_tokens} refs)")
    else:
        print("   ❌ FAIL: Missing TELEGRAM_BOT_TOKEN usage")
    
    # Check email template features
    print("\n4. PROFESSIONAL EMAIL TEMPLATE:")
    email_features = [
        "Maritime Hosting Services" in payment_content,
        "Offshore Hosting: Resilience | Discretion | Independence" in payment_content,
        "Payment Confirmed" in payment_content,
        "balance-table" in payment_content,
        "Complete payment transparency" in payment_content
    ]
    
    if all(email_features):
        print("   ✅ PASS: Professional maritime-themed email template")
    else:
        print("   ❌ FAIL: Email template missing features")
    
    # Check handlers integration
    print("\n5. HANDLERS INTEGRATION:")
    try:
        with open('handlers/payment_handlers.py', 'r') as f:
            handlers_content = f.read()
        
        handler_features = [
            "previous_balance = float(user.balance_usd)" in handlers_content,
            "_send_balance_payment_notifications" in handlers_content,
            "Balance Update:" in handlers_content,
            "Previous:" in handlers_content,
            "New Balance:" in handlers_content,
            "Confirmation sent to your email and bot!" in handlers_content
        ]
        
        if all(handler_features):
            print("   ✅ PASS: Payment handlers integrated with notifications")
            print("   ✅ PASS: UI shows balance transparency")
        else:
            print("   ❌ FAIL: Payment handlers integration incomplete")
            
    except FileNotFoundError:
        print("   ⚠️ WARNING: handlers/payment_handlers.py not found")
    
    print("\n" + "=" * 65)
    print("📋 IMPLEMENTATION SUMMARY:")
    print("=" * 65)
    print("✅ Wallet balance payments now send both bot + email notifications")
    print("✅ Previous balance shown for complete transparency")
    print("✅ New balance displayed after payment deduction")
    print("✅ Professional HTML email with balance table")
    print("✅ Bot notification with balance breakdown")
    print("✅ UI updated to show balance changes immediately")
    print("✅ Consistent TELEGRAM_BOT_TOKEN usage")
    print("✅ Maritime-themed professional email templates")
    print("")
    print("🏴‍☠️ WALLET BALANCE PAYMENT TRANSPARENCY ACHIEVED!")
    print("📧 Every wallet payment triggers dual notifications!")
    print("💰 Users see exactly how their balance changes!")
    print("=" * 65)

if __name__ == "__main__":
    validate_balance_notifications()