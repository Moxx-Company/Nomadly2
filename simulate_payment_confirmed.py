#!/usr/bin/env python3
"""Simulate payment confirmation and trigger domain registration"""

import json
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # First, let's add a payment to monitoring
    payment_info = {
        "0xE0B4D227C8df941920854b6A5b2C69aD33b9AB3E": {
            "user_id": 5590563715,
            "domain": "claudebaby.sbs",
            "crypto_type": "eth",
            "expected_amount": 9.87,
            "order_number": "ORD-27JP3",
            "created_at": "2025-07-24T12:00:00"
        }
    }
    
    # Save to monitoring queue
    with open('payment_monitor_queue.json', 'w') as f:
        json.dump(payment_info, f, indent=2)
    
    logger.info("✅ Added payment to monitoring queue")
    
    # Now create a payment confirmation
    confirmation = {
        "0xE0B4D227C8df941920854b6A5b2C69aD33b9AB3E": {
            "status": "success",
            "transaction_id": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "amount_received": 0.002709,
            "confirmations": 12,
            "confirmed_at": "2025-07-24T13:30:00"
        }
    }
    
    with open('payment_confirmations.json', 'w') as f:
        json.dump(confirmation, f, indent=2)
    
    logger.info("✅ Created payment confirmation")
    logger.info("⏳ Payment monitor should detect this within 30 seconds...")
    
    # Wait and check if it's processed
    await asyncio.sleep(35)
    
    # Check if confirmation was consumed
    with open('payment_confirmations.json', 'r') as f:
        remaining = json.load(f)
    
    if not remaining:
        logger.info("✅ Payment confirmation was processed!")
    else:
        logger.warning("⚠️ Payment confirmation not yet processed")

if __name__ == "__main__":
    asyncio.run(main())
