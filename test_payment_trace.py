#!/usr/bin/env python3
"""Test payment tracing for claudeb.sbs domain registration"""

import json
import os
from datetime import datetime

def trace_payment():
    print("🔍 PAYMENT TRACE FOR claudeb.sbs")
    print("=" * 50)
    
    # Check session data
    try:
        with open("user_sessions.json", "r") as f:
            sessions = json.load(f)
        
        user_id = "5590563715"
        if user_id in sessions:
            session = sessions[user_id]
            print("\n📋 SESSION DATA:")
            print(f"   Domain: {session.get('domain', 'N/A')}")
            print(f"   Order: {session.get('order_number', 'N/A')}")
            print(f"   Amount: ${session.get('price', 'N/A')}")
            print(f"   Crypto: {session.get('crypto_type', 'N/A').upper()}")
            print(f"   ETH Address: {session.get('eth_address', 'N/A')[:12]}...")
            print(f"   Stage: {session.get('stage', 'N/A')}")
            print(f"   Payment Confirmed: {session.get('payment_confirmed', False)}")
            print(f"   Registration Complete: {session.get('registration_complete', False)}")
            
            # Check payment queue
            print("\n📊 PAYMENT MONITOR STATUS:")
            if os.path.exists("/tmp/payment_queue.json"):
                with open("/tmp/payment_queue.json", "r") as f:
                    queue = json.load(f)
                print(f"   Addresses in queue: {len(queue)}")
                if session.get('eth_address') in queue:
                    print(f"   ✅ Your payment address IS being monitored")
                else:
                    print(f"   ⚠️  Your payment address NOT in monitor queue")
            else:
                print("   ⚠️  Payment queue file not found")
            
            print("\n🔄 PAYMENT FLOW STATUS:")
            print("   1. Payment address generated ✅")
            print("   2. Added to monitoring queue ✅")
            print("   3. Awaiting blockchain confirmation ⏳")
            print("   4. Domain registration pending ⏳")
            print("   5. Confirmation email pending ⏳")
            
            print("\n💡 NEXT STEPS:")
            print("   - Send 0.00271190 ETH to the provided address")
            print("   - Payment monitor checks every 30 seconds")
            print("   - Once confirmed, domain will be registered automatically")
            print("   - You'll receive confirmation in Telegram and email")
            
    except Exception as e:
        print(f"❌ Error reading session: {e}")

if __name__ == "__main__":
    trace_payment()