#!/usr/bin/env python3
"""Simulate payment confirmation for testing"""

import asyncio
import json
from datetime import datetime

async def simulate_payment_confirmation():
    """Simulate a payment confirmation from BlockBee webhook"""
    
    # Load current session data
    with open('user_sessions.json', 'r') as f:
        sessions = json.load(f)
    
    user_id = 5590563715
    session = sessions.get(str(user_id), {})
    
    if not session:
        print("❌ No active session found")
        return
    
    eth_address = session.get('eth_address')
    order_number = session.get('order_number')
    domain = session.get('domain')
    expected_amount = session.get('payment_amount_usd', 0)
    
    print(f"🔍 Simulating payment confirmation for:")
    print(f"   Order: {order_number}")
    print(f"   Domain: {domain}")
    print(f"   ETH Address: {eth_address}")
    print(f"   Amount: ${expected_amount}")
    print()
    
    # Import required modules
    import sys
    import os
    
    # Since this is a test script, we'll simulate the confirmations
    print("⚡ Simulating payment confirmation workflow...")
    
    # Simulate the payment data that would come from BlockBee
    payment_data = {
        'address_in': eth_address,
        'value_coin': 0.00270900,  # ETH amount
        'value_coin_convert': expected_amount,  # USD value
        'txid_in': '0x' + 'a' * 64,  # Simulated transaction ID
        'confirmations': 3,
        'result': 'success'
    }
    
    print("💰 Simulating payment received...")
    print(f"   Transaction ID: {payment_data['txid_in']}")
    print(f"   ETH Amount: {payment_data['value_coin']}")
    print(f"   USD Value: ${payment_data['value_coin_convert']}")
    print()
    
    # Update order status in database
    print("📊 Updating order status...")
    order = db.get_order_by_order_number(order_number)
    if order:
        db.update_order_status(order.id, 'payment_confirmed')
        db.update_order_payment_details(order.id, {
            'txid': payment_data['txid_in'],
            'amount_received': payment_data['value_coin'],
            'confirmations': payment_data['confirmations']
        })
        print("✅ Order status updated to 'payment_confirmed'")
    
    # Send user notification
    print("\n📱 Sending Telegram notification...")
    try:
        await notification_service.send_payment_confirmed_notification(
            user_id=user_id,
            domain=domain,
            order_number=order_number,
            crypto_type='eth',
            amount=payment_data['value_coin'],
            txid=payment_data['txid_in']
        )
        print("✅ User notified via Telegram")
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
    
    # Send email confirmation
    print("\n📧 Sending email confirmation...")
    try:
        email = session.get('technical_email', 'cloakhost@tutamail.com')
        if email != 'cloakhost@tutamail.com':  # Only send if custom email
            await confirmation_service.send_payment_confirmation(
                email=email,
                domain=domain,
                order_number=order_number,
                amount_usd=expected_amount,
                crypto_type='ETH',
                crypto_amount=payment_data['value_coin'],
                txid=payment_data['txid_in']
            )
            print(f"✅ Email sent to {email}")
        else:
            print("⏭️  Skipping email (default privacy email)")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
    
    # Trigger domain registration
    print("\n🌐 Starting domain registration...")
    try:
        result = await domain_service.register_domain_with_payment(
            user_id=user_id,
            domain=domain,
            payment_confirmed=True
        )
        
        if result['success']:
            print("✅ Domain registration initiated successfully!")
            
            # Send completion notification
            await notification_service.send_domain_registered_notification(
                user_id=user_id,
                domain=domain,
                order_number=order_number
            )
            
            # Send completion email
            if email != 'cloakhost@tutamail.com':
                await confirmation_service.send_domain_registration_complete(
                    email=email,
                    domain=domain,
                    order_number=order_number,
                    nameservers=session.get('custom_nameservers', []),
                    expiry_date=(datetime.utcnow().year + 1)
                )
        else:
            print(f"❌ Domain registration failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during domain registration: {e}")
    
    print("\n✅ Payment simulation complete!")
    print("Check your Telegram bot for notifications.")

# Run the simulation
if __name__ == "__main__":
    asyncio.run(simulate_payment_confirmation())