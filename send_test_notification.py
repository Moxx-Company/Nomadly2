#!/usr/bin/env python3
"""
Send Test Notification to User
Test the fixed notification system
"""

import asyncio
import logging
from services.confirmation_service import get_confirmation_service
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_test_notification():
    """Send test notification to user 5590563715"""
    
    print("🧪 TESTING FIXED NOTIFICATION SYSTEM")
    print("=" * 40)
    
    try:
        # Get confirmation service
        confirmation_service = get_confirmation_service()
        
        # Test data for user 5590563715
        test_order_data = {
            "order_id": "test_notification_072125", 
            "amount_usd": 9.87,
            "payment_method": "cryptocurrency",
            "service_type": "domain_registration",
            "domain_name": "ontest072248xyz.sbs",  # Your latest domain
            "contact_email": "test@example.com",
            "txid": "test_transaction_id_123",
            "status": "Test notification - System working!"
        }
        
        # Send test payment confirmation
        await confirmation_service.send_payment_confirmation(
            5590563715,  # Your Telegram ID
            test_order_data
        )
        
        print("✅ Test notification sent successfully!")
        print(f"   User ID: 5590563715")
        print(f"   Domain: {test_order_data['domain_name']}")
        print(f"   Amount: ${test_order_data['amount_usd']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test notification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(send_test_notification())