#!/usr/bin/env python3
"""
SECURE Payment Monitor - Only processes REAL blockchain confirmations
NO database-based false positives allowed
"""

import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurePaymentMonitor:
    """SECURE payment monitor - only accepts real BlockBee webhook confirmations"""
    
    def __init__(self):
        self.monitoring_interval = 30
        self.active_payments: Dict[str, Dict] = {}
        self.queue_file = 'payment_monitor_queue.json'
        
    async def start_monitoring(self):
        """Monitor payments - but ONLY process real webhook confirmations"""
        logger.info("🔒 Starting SECURE payment monitoring (webhook-only)")
        
        while True:
            try:
                self._load_from_queue()
                logger.info(f"📊 Monitoring {len(self.active_payments)} payment addresses")
                
                # Remove expired payments (24+ hours old)
                await self._cleanup_expired_payments()
                
                # DO NOT check database or create false confirmations
                # BlockBee will send webhooks when real payments arrive
                logger.debug("⏳ Waiting for real BlockBee webhook confirmations...")
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in secure monitoring loop: {e}")
                await asyncio.sleep(60)
    
    def _load_from_queue(self):
        """Load payment addresses from queue"""
        try:
            with open(self.queue_file, 'r') as f:
                queue_data = json.load(f)
                
            for address, info in queue_data.items():
                if address not in self.active_payments:
                    self.active_payments[address] = info
                    logger.info(f"📥 Monitoring {address[:20]}... for real blockchain payment")
                    
        except Exception as e:
            logger.debug(f"Queue file not found or empty: {e}")
    
    async def _cleanup_expired_payments(self):
        """Remove expired payment addresses"""
        expired_addresses = []
        
        for address, payment_info in self.active_payments.items():
            try:
                created_at = datetime.fromisoformat(payment_info['created_at'])
                if datetime.utcnow() - created_at > timedelta(hours=24):
                    expired_addresses.append(address)
            except Exception as e:
                logger.error(f"Error checking expiry for {address}: {e}")
                expired_addresses.append(address)
        
        for address in expired_addresses:
            logger.info(f"⏰ Payment expired for {address[:20]}...")
            del self.active_payments[address]
            
        if expired_addresses:
            self._save_to_queue()
    
    def _save_to_queue(self):
        """Save active payments to queue"""
        try:
            with open(self.queue_file, 'w') as f:
                json.dump(self.active_payments, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save queue: {e}")
    
    def add_payment_address(self, address: str, payment_info: Dict):
        """Add payment address to secure monitoring"""
        self.active_payments[address] = payment_info
        logger.info(f"🔒 Added {address[:20]}... to secure monitoring")
        self._save_to_queue()

async def main():
    """Start secure payment monitoring"""
    monitor = SecurePaymentMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())