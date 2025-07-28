#!/usr/bin/env python3
"""
Live Transaction Monitor - Real-time tracking of pending cryptocurrency payments
"""

import os
import time
import asyncio
import logging
import requests
from datetime import datetime
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveTransactionMonitor:
    def __init__(self):
        self.db_manager = get_db_manager()
        self.blockbee_api_key = os.getenv("BLOCKBEE_API_KEY")
        
    def get_pending_orders(self, telegram_id=5590563715):
        """Get pending orders for user"""
        with self.db_manager.get_session() as session:
            query = """
            SELECT order_id, amount, payment_address, payment_status, created_at
            FROM orders 
            WHERE telegram_id = %s AND payment_status = 'pending'
            ORDER BY created_at DESC
            LIMIT 10
            """
            result = session.execute(query, (telegram_id,))
            return result.fetchall()
    
    def check_eth_transaction(self, address):
        """Check ETH transaction status via blockchain API"""
        try:
            # Use Etherscan API for real transaction checking
            etherscan_api = "https://api.etherscan.io/api"
            params = {
                "module": "account",
                "action": "balance",
                "address": address,
                "tag": "latest",
                "apikey": "YourApiKeyToken"  # Free tier available
            }
            
            response = requests.get(etherscan_api, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                balance_wei = int(data.get('result', 0))
                balance_eth = balance_wei / 10**18
                return balance_eth
            return 0
        except Exception as e:
            logger.error(f"ETH balance check error: {e}")
            return 0
    
    def check_blockbee_status(self, order_id):
        """Check payment status via BlockBee"""
        try:
            url = f"https://api.blockbee.io/eth/info/"
            params = {
                "apikey": self.blockbee_api_key,
                "callback": f"https://your-webhook-url/webhook/blockbee/{order_id}"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"BlockBee check error: {e}")
            return None
    
    async def monitor_transactions(self):
        """Main monitoring loop"""
        print("🚀 LIVE TRANSACTION MONITOR STARTED")
        print("==================================================")
        print("⏱️  Real-time cryptocurrency payment tracking")
        print("💰 Monitoring ETH payments for User 5590563715")
        print("==================================================")
        
        while True:
            try:
                pending_orders = self.get_pending_orders()
                
                if pending_orders:
                    print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - PENDING TRANSACTIONS")
                    print("-" * 50)
                    
                    for order in pending_orders:
                        order_id, amount, payment_address, status, created = order
                        
                        print(f"🔍 Order: {order_id[:8]}...")
                        print(f"   💵 Amount: ${amount} USD")
                        print(f"   📍 Address: {payment_address[:20]}...")
                        print(f"   📅 Created: {created}")
                        
                        # Check actual blockchain balance
                        if payment_address and payment_address.startswith('0x'):
                            balance = self.check_eth_transaction(payment_address)
                            if balance > 0:
                                print(f"   ✅ PAYMENT RECEIVED: {balance:.6f} ETH")
                                print(f"   🎉 TRANSACTION DETECTED!")
                            else:
                                print(f"   ⏳ Waiting for payment... (0 ETH)")
                        
                        print()
                
                else:
                    print(f"📊 {datetime.now().strftime('%H:%M:%S')} - No pending transactions")
                
                # Wait 15 seconds before next check
                await asyncio.sleep(15)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    monitor = LiveTransactionMonitor()
    asyncio.run(monitor.monitor_transactions())