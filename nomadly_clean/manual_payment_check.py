#!/usr/bin/env python3
"""Manually check and process payment for order"""

import os
import sys
sys.path.append('.')

from apis.blockbee import BlockBeeAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Order
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_payment():
    """Check BlockBee logs for payment confirmation"""
    order_id = "c63030b2-e5c4-46c0-a241-5cfc37de7fbe"
    
    # Get order from database
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    order = session.query(Order).filter_by(order_id=order_id).first()
    
    if not order:
        print(f"❌ Order {order_id} not found")
        return
        
    print(f"📋 Order Details:")
    print(f"  Domain: {order.domain_name}")
    print(f"  Status: {order.status}")
    print(f"  ETH Address: {order.crypto_address}")
    print(f"  Expected Amount: {order.crypto_amount} ETH")
    print()
    
    # Check BlockBee logs
    blockbee = BlockBeeAPI()
    webhook_url = f"https://nomadly2-onarrival.replit.app/webhook/blockbee/{order_id}"
    
    print(f"🔍 Checking BlockBee logs for webhook URL:")
    print(f"  {webhook_url}")
    print()
    
    logs = blockbee.check_logs("eth", webhook_url)
    
    if logs:
        print(f"📊 BlockBee Log Response:")
        print(f"  Status: {logs.get('status')}")
        if logs.get('status') == 'success':
            addresses = logs.get('address_in', [])
            if addresses:
                print(f"  Found {len(addresses)} payment(s)")
                for addr_info in addresses:
                    print(f"  - Address: {addr_info.get('address')}")
                    print(f"    Received: {addr_info.get('value')} ETH")
                    print(f"    Confirmations: {addr_info.get('confirmations')}")
                    print(f"    Callback Status: {addr_info.get('callback_response')}")
            else:
                print("  No payments found for this webhook URL")
        else:
            print(f"  Error: {logs.get('message', 'Unknown error')}")
    else:
        print("❌ Failed to retrieve BlockBee logs")
    
    # Manual payment confirmation prompt
    print()
    print("💡 If payment was confirmed on blockchain but webhook didn't arrive:")
    print("   The webhook URL may have been misconfigured during order creation")
    print("   BlockBee needs the exact webhook URL when creating the payment address")
    
    session.close()

if __name__ == "__main__":
    check_payment()