#!/usr/bin/env python3
"""Manually process the confirmed payment"""

import os
import sys
sys.path.append('.')

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import asyncio

# Setup database
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

async def process_payment():
    """Manually process the payment that's confirmed on blockchain"""
    session = Session()
    
    order_id = "c63030b2-e5c4-46c0-a241-5cfc37de7fbe"
    
    print("🔄 Processing confirmed blockchain payment...")
    print(f"Order ID: {order_id}")
    print(f"Domain: newlifeinpt.sbs")
    print()
    
    try:
        # Update order status in database
        from sqlalchemy import text
        
        # Mark order as completed
        result = session.execute(
            text("UPDATE orders SET status = 'completed', completed_at = :completed_at WHERE order_id = :order_id"),
            {"order_id": order_id, "completed_at": datetime.now()}
        )
        session.commit()
        
        print("✅ Order marked as completed!")
        
        # Send notification to bot to process domain registration
        print("📤 Triggering domain registration...")
        
        # Import bot instance to trigger registration
        from nomadly3_clean_bot import bot_instance
        if bot_instance:
            # Trigger domain registration
            await bot_instance.process_paid_order(order_id)
            print("✅ Domain registration triggered!")
        else:
            print("⚠️  Bot instance not available, please restart bot to complete registration")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("💳 MANUAL PAYMENT PROCESSING")
    print("=" * 50)
    print("Since BlockBee webhook didn't arrive but payment is confirmed on blockchain,")
    print("we'll manually process your payment...")
    print()
    
    asyncio.run(process_payment())