#!/usr/bin/env python3
"""
Manual Domain Registration Trigger - For completed payments that missed registration
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add current directory to path
sys.path.append('.')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def trigger_domain_registration():
    """Trigger domain registration for completed payment that missed automatic processing"""
    try:
        from database import get_db_manager
        from payment_service import PaymentService
        
        print("🔧 MANUAL DOMAIN REGISTRATION TRIGGER")
        print("=====================================")
        
        db_manager = get_db_manager()
        payment_service = PaymentService()
        
        # Get the completed order details
        order_id = "76a7c142-7cdf-4daf-bc2b-1d793b6dbdf5"
        domain_name = "helploma.sbs"
        telegram_id = 5590563715
        
        print(f"🎯 Order ID: {order_id}")
        print(f"🌐 Domain: {domain_name}")
        print(f"👤 User: {telegram_id}")
        print()
        
        # Check if domain is already registered
        with db_manager.get_session() as session:
            existing_domain = session.execute(
                "SELECT domain_name FROM registered_domains WHERE domain_name = %s",
                (domain_name,)
            ).fetchone()
            
            if existing_domain:
                print(f"⚠️  Domain {domain_name} already registered, skipping")
                return
        
        print("🚀 Triggering domain registration...")
        
        # Use payment service to trigger domain registration
        # Create mock webhook data that would trigger registration
        webhook_data = {
            'order_id': order_id,
            'value': '0.00266763',
            'value_coin': '0.00266763',
            'coin': 'eth',
            'result': 'sent',
            'confirmations': '10',
            'domain_name': domain_name
        }
        
        # Force domain registration by processing as if it's a new payment
        result = await payment_service._register_domain_with_openprovider(
            domain_name=domain_name,
            telegram_id=telegram_id,
            order_id=order_id,
            technical_email="onarrival21@gmail.com"
        )
        
        if result and result.get('success'):
            print("✅ DOMAIN REGISTRATION SUCCESSFUL!")
            print(f"   Domain: {domain_name}")
            print(f"   OpenProvider ID: {result.get('openprovider_domain_id', 'Unknown')}")
            print(f"   Cloudflare Zone: {result.get('cloudflare_zone_id', 'Unknown')}")
            print(f"   Nameservers: {result.get('nameservers', 'Unknown')}")
            print()
            print("🎉 Domain registration completed successfully!")
            print("📧 Email notification should be sent automatically")
            
            return True
        else:
            error_msg = result.get('error') if result else 'Unknown error'
            print(f"❌ DOMAIN REGISTRATION FAILED: {error_msg}")
            return False
            
    except Exception as e:
        logger.error(f"Registration trigger failed: {e}")
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(trigger_domain_registration())
    if success:
        print("\n✅ Registration completed successfully")
    else:
        print("\n❌ Registration failed - check logs for details")