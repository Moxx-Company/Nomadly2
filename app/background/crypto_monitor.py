"""
Crypto Monitor Daemon - Background Task for Transaction Detection
Monitors cryptocurrency payments using asyncio background tasks
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

@dataclass
class PaymentWatch:
    """Payment monitoring configuration"""
    order_id: str
    crypto_address: str
    expected_amount: float
    currency: str
    telegram_id: int
    created_at: datetime
    expires_at: datetime

@dataclass
class TransactionDetection:
    """Detected transaction data"""
    tx_hash: str
    address: str
    amount: float
    confirmations: int
    detected_at: datetime
    currency: str

class CryptoMonitorDaemon:
    """
    Background daemon for monitoring cryptocurrency transactions
    Uses asyncio for non-blocking operation
    """
    
    def __init__(self, payment_service=None, notification_service=None):
        self.payment_service = payment_service
        self.notification_service = notification_service
        self.active_watches: Dict[str, PaymentWatch] = {}
        self.running = False
        self.check_interval = 30  # seconds
        self.max_retries = 3
        
    async def start_monitoring(self):
        """Start the background monitoring daemon"""
        if self.running:
            logger.warning("Crypto monitor already running")
            return
            
        self.running = True
        logger.info("🚀 Starting Crypto Monitor Daemon")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._payment_monitor_loop()),
            asyncio.create_task(self._expired_payments_cleanup()),
            asyncio.create_task(self._health_check_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Crypto monitor daemon error: {e}")
        finally:
            self.running = False
            logger.info("❌ Crypto Monitor Daemon stopped")
    
    def stop_monitoring(self):
        """Stop the monitoring daemon gracefully"""
        self.running = False
        logger.info("🛑 Stopping Crypto Monitor Daemon")
    
    async def add_payment_watch(self, payment_watch: PaymentWatch):
        """Add a new payment to monitor"""
        self.active_watches[payment_watch.order_id] = payment_watch
        logger.info(
            f"📝 Added payment watch: {payment_watch.order_id} "
            f"({payment_watch.currency} {payment_watch.expected_amount})"
        )
    
    async def remove_payment_watch(self, order_id: str):
        """Remove payment watch"""
        if order_id in self.active_watches:
            del self.active_watches[order_id]
            logger.info(f"🗑️ Removed payment watch: {order_id}")
    
    async def _payment_monitor_loop(self):
        """Main payment monitoring loop"""
        logger.info("Starting payment monitor loop")
        
        while self.running:
            try:
                if not self.active_watches:
                    await asyncio.sleep(self.check_interval)
                    continue
                
                # Check each active payment
                for order_id, watch in list(self.active_watches.items()):
                    try:
                        await self._check_payment(order_id, watch)
                    except Exception as e:
                        logger.error(f"Error checking payment {order_id}: {e}")
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Payment monitor loop error: {e}")
                await asyncio.sleep(5)
    
    async def _check_payment(self, order_id: str, watch: PaymentWatch):
        """Check individual payment for transactions"""
        try:
            # Get transactions for address
            transactions = await self._get_address_transactions(
                watch.crypto_address, watch.currency
            )
            
            # Check for matching transactions
            for tx in transactions:
                if await self._is_valid_payment(tx, watch):
                    detection = TransactionDetection(
                        tx_hash=tx['hash'],
                        address=watch.crypto_address,
                        amount=tx['amount'],
                        confirmations=tx['confirmations'],
                        detected_at=datetime.now(),
                        currency=watch.currency
                    )
                    
                    await self._process_payment_detection(order_id, watch, detection)
                    break
                    
        except Exception as e:
            logger.error(f"Error checking payment {order_id}: {e}")
    
    async def _get_address_transactions(self, address: str, currency: str) -> List[Dict]:
        """Get transactions for a cryptocurrency address"""
        try:
            # This would typically call BlockBee or other crypto API
            # For now, return mock data for development
            mock_transactions = [
                {
                    'hash': 'mock_tx_hash_123',
                    'amount': 0.001,
                    'confirmations': 3,
                    'timestamp': datetime.now().isoformat()
                }
            ]
            
            # In production, implement real API calls:
            # if currency == 'BTC':
            #     return await self._get_bitcoin_transactions(address)
            # elif currency == 'ETH':
            #     return await self._get_ethereum_transactions(address)
            
            return mock_transactions
            
        except Exception as e:
            logger.error(f"Error getting transactions for {address}: {e}")
            return []
    
    async def _is_valid_payment(self, transaction: Dict, watch: PaymentWatch) -> bool:
        """Check if transaction is a valid payment for the watch"""
        try:
            tx_amount = float(transaction['amount'])
            expected_amount = watch.expected_amount
            
            # Check amount (allow 5% tolerance)
            amount_tolerance = 0.05
            min_amount = expected_amount * (1 - amount_tolerance)
            max_amount = expected_amount * (1 + amount_tolerance)
            
            if not (min_amount <= tx_amount <= max_amount * 2):  # Allow overpayment
                return False
            
            # Check confirmations based on currency
            min_confirmations = self._get_min_confirmations(watch.currency)
            if transaction['confirmations'] < min_confirmations:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating payment: {e}")
            return False
    
    def _get_min_confirmations(self, currency: str) -> int:
        """Get minimum confirmations required for currency"""
        confirmations = {
            'BTC': 1,
            'ETH': 12,
            'LTC': 6,
            'DOGE': 20
        }
        return confirmations.get(currency, 1)
    
    async def _process_payment_detection(self, order_id: str, watch: PaymentWatch, detection: TransactionDetection):
        """Process detected payment"""
        try:
            logger.info(
                f"💰 Payment detected! Order: {order_id}, "
                f"Amount: {detection.amount} {detection.currency}, "
                f"TX: {detection.tx_hash[:16]}..."
            )
            
            # Update payment status in database
            if self.payment_service:
                await self.payment_service.process_payment_confirmation(
                    order_id=order_id,
                    tx_hash=detection.tx_hash,
                    amount_received=detection.amount,
                    confirmations=detection.confirmations
                )
            
            # Send notification to user
            if self.notification_service:
                await self.notification_service.notify_payment_received(
                    telegram_id=watch.telegram_id,
                    order_id=order_id,
                    amount=detection.amount,
                    currency=detection.currency
                )
            
            # Remove from active watches
            await self.remove_payment_watch(order_id)
            
        except Exception as e:
            logger.error(f"Error processing payment detection: {e}")
    
    async def _expired_payments_cleanup(self):
        """Clean up expired payment watches"""
        logger.info("Starting expired payments cleanup loop")
        
        while self.running:
            try:
                current_time = datetime.now()
                expired_orders = []
                
                for order_id, watch in self.active_watches.items():
                    if current_time > watch.expires_at:
                        expired_orders.append(order_id)
                
                # Remove expired orders
                for order_id in expired_orders:
                    watch = self.active_watches[order_id]
                    logger.info(f"⏰ Payment expired: {order_id}")
                    
                    # Notify user of expiration
                    if self.notification_service:
                        await self.notification_service.notify_payment_expired(
                            telegram_id=watch.telegram_id,
                            order_id=order_id
                        )
                    
                    await self.remove_payment_watch(order_id)
                
                # Check every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Expired payments cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def _health_check_loop(self):
        """Periodic health check and status logging"""
        logger.info("Starting health check loop")
        
        while self.running:
            try:
                active_count = len(self.active_watches)
                logger.info(f"💚 Crypto Monitor Health: {active_count} active payments")
                
                # Log detailed status every 10 minutes
                await asyncio.sleep(600)
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current daemon status"""
        return {
            'running': self.running,
            'active_watches': len(self.active_watches),
            'check_interval': self.check_interval,
            'watches': [
                {
                    'order_id': watch.order_id,
                    'currency': watch.currency,
                    'amount': watch.expected_amount,
                    'expires_at': watch.expires_at.isoformat()
                }
                for watch in self.active_watches.values()
            ]
        }

# Global daemon instance
crypto_monitor = CryptoMonitorDaemon()

async def get_crypto_monitor():
    """Get the global crypto monitor instance"""
    return crypto_monitor

async def start_crypto_monitoring():
    """Start crypto monitoring as background task"""
    try:
        await crypto_monitor.start_monitoring()
    except Exception as e:
        logger.error(f"Failed to start crypto monitoring: {e}")

def stop_crypto_monitoring():
    """Stop crypto monitoring"""
    crypto_monitor.stop_monitoring()

# Utility functions for easy integration

async def monitor_payment(order_id: str, crypto_address: str, expected_amount: float, 
                         currency: str, telegram_id: int, expires_in_hours: int = 24):
    """Add a payment to monitoring queue"""
    expires_at = datetime.now() + timedelta(hours=expires_in_hours)
    
    payment_watch = PaymentWatch(
        order_id=order_id,
        crypto_address=crypto_address,
        expected_amount=expected_amount,
        currency=currency,
        telegram_id=telegram_id,
        created_at=datetime.now(),
        expires_at=expires_at
    )
    
    await crypto_monitor.add_payment_watch(payment_watch)

async def stop_monitoring_payment(order_id: str):
    """Stop monitoring a specific payment"""
    await crypto_monitor.remove_payment_watch(order_id)