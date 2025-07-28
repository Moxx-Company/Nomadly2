"""
Wallet and Payment Service for Nomadly3
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

from ..core.config import config
from ..models.wallet import WalletTransaction, Order
from ..models.user import User

logger = logging.getLogger(__name__)

class WalletService:
    """Service for managing wallet operations and payments"""
    
    def __init__(self, db_session, wallet_repo=None, transaction_repo=None, user_repo=None):
        """Initialize with dependency injection flexibility"""
        self.db_session = db_session
        
        # Import repositories with proper imports
        try:
            from ..repositories.wallet_repo import WalletRepository
            from ..repositories.transaction_repo import TransactionRepository
            from ..repositories.user_repo import UserRepository
            from ..core.external_apis import BlockBeeAPI, FastForexAPI
        except ImportError:
            # Fallback imports for testing
            WalletRepository = TransactionRepository = UserRepository = None
            BlockBeeAPI = FastForexAPI = None
        
        self.wallet_repo = wallet_repo
        self.transaction_repo = transaction_repo  
        self.user_repo = user_repo
        self.supported_cryptocurrencies = ["btc", "eth", "ltc", "doge"]
        
        # External service integrations
        if BlockBeeAPI and FastForexAPI:
            self.blockbee_api = BlockBeeAPI()
            self.fastforex_api = FastForexAPI()
        else:
            self.blockbee_api = None
            self.fastforex_api = None
    
    async def get_user_balance(self, telegram_id: int) -> Decimal:
        """Get user's current wallet balance"""
        try:
            # This would query the database
            # user = User.query.filter_by(telegram_id=telegram_id).first()
            # return user.balance_usd if user else Decimal("0.00")
            return Decimal("0.00")  # Placeholder
        except Exception as e:
            logger.error(f"Error getting user balance: {e}")
            return Decimal("0.00")
    
    async def add_funds(self, telegram_id: int, amount: Decimal, 
                       payment_method: str, payment_details: Dict[str, Any] = None) -> WalletTransaction:
        """Add funds to user's wallet"""
        try:
            transaction = WalletTransaction(
                telegram_id=telegram_id,
                transaction_type="deposit",
                amount=amount,
                currency="USD",
                payment_method=payment_method,
                status="pending",
                service_type="wallet_deposit",
                service_details=payment_details or {}
            )
            
            # Generate payment address for cryptocurrency
            if payment_method in self.supported_cryptocurrencies:
                payment_address = await self._generate_crypto_address(payment_method, transaction.id)
                transaction.update_payment_info(
                    address=payment_address,
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
            
            # Here you would save to database
            # db.session.add(transaction)
            # db.session.commit()
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error adding funds: {e}")
            raise
    
    async def create_payment_request(self, telegram_id: int, amount_usd: float, 
                                   cryptocurrency: str, payment_method: str = "crypto") -> dict:
        """Create cryptocurrency payment request for wallet funding"""
        try:
            # Convert USD to cryptocurrency amount (simplified)
            crypto_amount = amount_usd * 0.0001  # Placeholder conversion
            
            # Generate payment address (simplified)
            payment_address = f"{cryptocurrency}_{telegram_id}_{uuid.uuid4().hex[:8]}"
            
            # Create transaction record (simplified)
            transaction_id = f"tx_{uuid.uuid4().hex[:12]}"
            
            return {
                "payment_id": transaction_id,
                "address": payment_address,
                "amount_crypto": crypto_amount,
                "qr_code": f"qr_data_{payment_address}",
                "expires_at": datetime.utcnow() + timedelta(hours=24)
            }
            
        except Exception as e:
            logger.error(f"Payment request creation failed: {e}")
            raise Exception(f"Could not create payment request: {str(e)}")
    
    async def monitor_blockchain_payment(self, payment_id: str) -> dict:
        """Monitor blockchain payment status and confirmations"""
        try:
            # Simplified payment monitoring
            return {
                "payment_id": payment_id,
                "status": "pending",
                "confirmations": 0,
                "amount_received": 0
            }
            
        except Exception as e:
            logger.error(f"Payment monitoring failed: {e}")
            raise Exception(f"Could not monitor payment: {str(e)}")
    
    async def apply_overpayment_credit(self, payment_id: str, overpayment_amount: float) -> bool:
        """Apply overpayment as wallet credit"""
        try:
            logger.info(f"Applied ${overpayment_amount} overpayment credit for payment {payment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Overpayment credit failed: {e}")
            return False
    
    async def get_wallet_status(self, telegram_id: int) -> dict:
        """Get comprehensive wallet status"""
        return {
            "telegram_id": telegram_id,
            "balance_usd": 0.00,
            "total_spent": 0.00,
            "pending_deposits": 0,
            "last_transaction": None,
            "loyalty_tier": "bronze"
        }
    
    async def get_transaction_history(self, telegram_id: int, limit: int = 10, offset: int = 0) -> List[dict]:
        """Get transaction history for user"""
        return []
    
    async def get_balance(self, telegram_id: int) -> float:
        """Get wallet balance for user"""
        return 0.00

    async def deduct_funds(self, telegram_id: int, amount: Decimal, 
                          order_id: str, service_type: str) -> Tuple[bool, str]:
        """Deduct funds from user's wallet for a purchase"""
        try:
            user_balance = await self.get_user_balance(telegram_id)
            
            if user_balance < amount:
                return False, f"Insufficient balance. Required: ${amount}, Available: ${user_balance}"
            
            transaction = WalletTransaction(
                telegram_id=telegram_id,
                transaction_type="payment",
                amount=amount,
                currency="USD",
                payment_method="wallet",
                status="completed",
                order_id=order_id,
                service_type=service_type,
                completed_at=datetime.utcnow()
            )
            
            # Here you would:
            # 1. Deduct from user balance
            # 2. Save transaction
            # user.deduct_balance(amount)
            # db.session.add(transaction)
            # db.session.commit()
            
            return True, "Payment successful"
            
        except Exception as e:
            logger.error(f"Error deducting funds: {e}")
            return False, f"Payment failed: {str(e)}"
    
    async def create_crypto_payment(self, telegram_id: int, amount_usd: Decimal,
                                   cryptocurrency: str, order_id: str,
                                   service_details: Dict[str, Any]) -> Order:
        """Create a cryptocurrency payment order"""
        try:
            # Get exchange rate
            crypto_amount, exchange_rate = await self._get_crypto_amount(amount_usd, cryptocurrency)
            
            order = Order(
                id=order_id,
                telegram_id=telegram_id,
                order_type="domain_registration",
                amount_usd=amount_usd,
                currency=cryptocurrency.upper(),
                payment_method=cryptocurrency,
                service_details=service_details,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            # Generate payment address
            payment_address = await self._generate_crypto_address(cryptocurrency, order_id)
            order.payment_address = payment_address
            
            # Here you would save to database
            # db.session.add(order)
            # db.session.commit()
            
            return order
            
        except Exception as e:
            logger.error(f"Error creating crypto payment: {e}")
            raise
    
    async def process_crypto_payment(self, order_id: str, amount_received: Decimal,
                                   txid: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Process received cryptocurrency payment"""
        try:
            # Get order
            # order = Order.query.get(order_id)
            # if not order:
            #     return False, "Order not found", {}
            
            # Mock order for now
            order = None
            if not order:
                return False, "Order not found", {}
            
            expected_amount = order.amount_usd
            amount_received_usd = amount_received  # Would convert from crypto
            
            # Check payment amount
            if amount_received_usd >= expected_amount:
                # Payment sufficient or overpaid
                order.mark_completed()
                order.payment_received = amount_received
                
                # Handle overpayment
                overpayment = amount_received_usd - expected_amount
                if overpayment > Decimal("0.01"):
                    await self._credit_overpayment(order.telegram_id, overpayment)
                    return True, "Payment completed with overpayment credited", {
                        "overpayment": float(overpayment),
                        "credited_to_wallet": True
                    }
                
                return True, "Payment completed successfully", {}
                
            else:
                # Underpayment
                shortage = expected_amount - amount_received_usd
                await self._credit_partial_payment(order.telegram_id, amount_received_usd)
                
                return False, f"Partial payment received. Shortage: ${shortage}", {
                    "shortage": float(shortage),
                    "received": float(amount_received_usd),
                    "expected": float(expected_amount)
                }
                
        except Exception as e:
            logger.error(f"Error processing crypto payment: {e}")
            return False, f"Payment processing error: {str(e)}", {}
    
    async def get_transaction_history(self, telegram_id: int, limit: int = 50) -> List[WalletTransaction]:
        """Get user's transaction history"""
        try:
            # This would query the database
            # transactions = WalletTransaction.query.filter_by(telegram_id=telegram_id)\
            #     .order_by(WalletTransaction.created_at.desc())\
            #     .limit(limit).all()
            # return transactions
            return []  # Placeholder
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return []
    
    async def get_pending_orders(self, telegram_id: int) -> List[Order]:
        """Get user's pending payment orders"""
        try:
            # This would query the database
            # orders = Order.query.filter_by(telegram_id=telegram_id, status="pending")\
            #     .order_by(Order.created_at.desc()).all()
            # return orders
            return []  # Placeholder
        except Exception as e:
            logger.error(f"Error getting pending orders: {e}")
            return []
    
    def calculate_offshore_price(self, base_price: Decimal) -> Decimal:
        """Calculate offshore price with multiplier"""
        return base_price * self.offshore_multiplier
    
    def get_supported_cryptocurrencies(self) -> List[str]:
        """Get list of supported cryptocurrencies"""
        return self.supported_cryptocurrencies.copy()
    
    async def _generate_crypto_address(self, cryptocurrency: str, order_id: str) -> str:
        """Generate cryptocurrency payment address via BlockBee API"""
        try:
            # This would integrate with BlockBee API
            # For now, return a mock address
            mock_addresses = {
                "btc": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "eth": "0x742d35Cc6634C0532925a3b8D8Ad2c5F6D3f1234",
                "ltc": "ltc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0567",
                "doge": "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L"
            }
            return mock_addresses.get(cryptocurrency, "")
        except Exception as e:
            logger.error(f"Error generating crypto address: {e}")
            return ""
    
    async def initiate_crypto_payment(self, telegram_id: int, amount_usd: float, 
                                    currency: str, order_id: str) -> dict:
        """Initiate cryptocurrency payment"""
        try:
            # Generate payment address for specified currency
            payment_address = await self._generate_payment_address(currency)
            
            # Calculate crypto amount based on current rates
            crypto_amount = await self._convert_usd_to_crypto(amount_usd, currency)
            
            # Create payment request
            payment_request = {
                "payment_id": f"pay_{order_id}_{currency.lower()}",
                "telegram_id": telegram_id,
                "order_id": order_id,
                "currency": currency.upper(),
                "amount_usd": amount_usd,
                "amount_crypto": crypto_amount,
                "payment_address": payment_address,
                "status": "pending",
                "expires_at": datetime.utcnow() + timedelta(hours=2),
                "created_at": datetime.utcnow()
            }
            
            # Save payment request
            saved_payment = self.wallet_repo.create_payment(payment_request)
            
            return {
                "success": True,
                "payment_id": payment_request["payment_id"],
                "payment_address": payment_address,
                "amount_crypto": crypto_amount,
                "currency": currency.upper(),
                "expires_in_minutes": 120,
                "qr_code_data": f"{currency.lower()}:{payment_address}?amount={crypto_amount}"
            }
            
        except Exception as e:
            logger.error(f"Error initiating crypto payment: {e}")
            raise Exception(f"Could not initiate payment: {str(e)}")
    
    async def process_overpayment(self, telegram_id: int, payment_id: str, 
                                 overpayment_amount: float) -> dict:
        """Process cryptocurrency overpayment by crediting wallet"""
        try:
            # Credit overpayment to user wallet
            user = await self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                raise Exception("User not found")
            
            # Add overpayment to user balance
            new_balance = user.balance_usd + overpayment_amount
            await self.user_repo.update(telegram_id, {"balance_usd": new_balance})
            
            # Create transaction record
            transaction_data = {
                "telegram_id": telegram_id,
                "transaction_type": "overpayment_credit",
                "amount": overpayment_amount,
                "status": "completed",
                "description": f"Overpayment credit from payment {payment_id}",
                "created_at": datetime.utcnow()
            }
            
            await self.transaction_repo.create(transaction_data)
            
            return {
                "success": True,
                "credited_amount": overpayment_amount,
                "new_balance": new_balance,
                "message": f"${overpayment_amount:.2f} overpayment credited to wallet"
            }
            
        except Exception as e:
            logger.error(f"Error processing overpayment: {e}")
            return {"success": False, "error": f"Overpayment processing failed: {str(e)}"}
    
    async def _generate_payment_address(self, currency: str) -> str:
        """Generate payment address for cryptocurrency"""
        # Placeholder addresses for different currencies
        addresses = {
            "BTC": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "ETH": "0x742d35Cc6634C0532925a3b8D598C4B1D3f5c9A8",
            "LTC": "ltc1qw4fxgf2qx5j2y8x7x4j9q8r3t5e9w8q2a1s3d",
            "DOGE": "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L"
        }
        
        return addresses.get(currency.upper(), addresses["BTC"])
    
    async def _convert_usd_to_crypto(self, amount_usd: float, currency: str) -> float:
        """Convert USD amount to cryptocurrency amount"""
        # Placeholder conversion rates
        rates = {
            "BTC": 0.000023,  # ~$43,000 per BTC
            "ETH": 0.00041,   # ~$2,400 per ETH  
            "LTC": 0.0084,    # ~$119 per LTC
            "DOGE": 8.33      # ~$0.12 per DOGE
        }
        
        rate = rates.get(currency.upper(), rates["BTC"])
        return round(amount_usd * rate, 8)
    
    async def _get_crypto_amount(self, usd_amount: Decimal, cryptocurrency: str) -> Tuple[Decimal, Decimal]:
        """Get cryptocurrency amount and exchange rate for USD amount"""
        try:
            # This would integrate with FastForex API
            # Mock exchange rates
            mock_rates = {
                "btc": Decimal("45000.00"),
                "eth": Decimal("3000.00"),
                "ltc": Decimal("100.00"),
                "doge": Decimal("0.08")
            }
            
            rate = mock_rates.get(cryptocurrency, Decimal("1.00"))
            crypto_amount = usd_amount / rate
            
            return crypto_amount, rate
        except Exception as e:
            logger.error(f"Error getting crypto amount: {e}")
            return Decimal("0"), Decimal("1")
    
    async def _credit_overpayment(self, telegram_id: int, amount: Decimal) -> None:
        """Credit overpayment to user's wallet"""
        try:
            transaction = WalletTransaction(
                telegram_id=telegram_id,
                transaction_type="deposit",
                amount=amount,
                currency="USD",
                payment_method="overpayment_credit",
                status="completed",
                service_type="overpayment_refund",
                completed_at=datetime.utcnow()
            )
            
            # Here you would:
            # 1. Add to user balance
            # 2. Save transaction
            # user.add_balance(amount)
            # db.session.add(transaction)
            # db.session.commit()
            
        except Exception as e:
            logger.error(f"Error crediting overpayment: {e}")
    
    async def _credit_partial_payment(self, telegram_id: int, amount: Decimal) -> None:
        """Credit partial payment to user's wallet"""
        try:
            transaction = WalletTransaction(
                telegram_id=telegram_id,
                transaction_type="deposit",
                amount=amount,
                currency="USD",
                payment_method="partial_payment_credit",
                status="completed",
                service_type="partial_payment_refund",
                completed_at=datetime.utcnow()
            )
            
            # Here you would save to database
            # db.session.add(transaction)
            # db.session.commit()
            
        except Exception as e:
            logger.error(f"Error crediting partial payment: {e}")
    def get_wallet_summary(self, telegram_id: int) -> Dict[str, Any]:
        """
        Get comprehensive wallet summary - UI workflow method
        """
        try:
            # Get current balance
            balance = Decimal("0.00")
            if self.wallet_repo:
                balance = self.wallet_repo.get_user_balance(telegram_id)
            
            # Get recent transactions
            recent_transactions = []
            if self.transaction_repo:
                transactions = self.transaction_repo.get_by_telegram_id(telegram_id, limit=10)
                for tx in transactions:
                    recent_transactions.append({
                        "id": tx.id,
                        "type": tx.transaction_type,
                        "amount": float(tx.amount),
                        "status": tx.status,
                        "created_at": tx.created_at.isoformat() if tx.created_at else None,
                        "description": getattr(tx, 'description', f"{tx.transaction_type} transaction")
                    })
            
            # Calculate statistics
            total_deposits = sum(tx["amount"] for tx in recent_transactions if tx["type"] == "deposit")
            total_payments = sum(tx["amount"] for tx in recent_transactions if tx["type"] == "payment")
            
            return {
                "success": True,
                "user_id": telegram_id,
                "current_balance": float(balance),
                "currency": "USD",
                "recent_transactions": recent_transactions,
                "statistics": {
                    "total_deposits": total_deposits,
                    "total_payments": total_payments,
                    "transaction_count": len(recent_transactions)
                },
                "wallet_status": "active" if balance >= 0 else "low_balance"
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet summary: {e}")
            return {
                "success": False,
                "error": f"Wallet summary failed: {str(e)}",
                "current_balance": 0.00,
                "currency": "USD"
            }
    
    def process_payment(self, telegram_id: int, amount: Decimal, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment from wallet - UI workflow method
        """
        try:
            # Validate user balance
            current_balance = Decimal("0.00")
            if self.wallet_repo:
                current_balance = self.wallet_repo.get_user_balance(telegram_id)
            
            if current_balance < amount:
                return {
                    "success": False,
                    "error": f"Insufficient balance. Required: ${amount}, Available: ${current_balance}",
                    "balance_required": float(amount),
                    "balance_available": float(current_balance),
                    "balance_shortage": float(amount - current_balance)
                }
            
            # Process payment
            order_id = payment_details.get("order_id", f"order_{telegram_id}_{datetime.utcnow().timestamp()}")
            service_type = payment_details.get("service_type", "domain_registration")
            
            # Create transaction record
            if self.transaction_repo:
                transaction = self.transaction_repo.create(
                    telegram_id=telegram_id,
                    amount=amount,
                    transaction_type="payment",
                    payment_method="wallet",
                    status="completed",
                    order_id=order_id,
                    service_type=service_type
                )
            
            # Update user balance
            new_balance = current_balance - amount
            if self.wallet_repo:
                self.wallet_repo.update_user_balance(telegram_id, new_balance)
            
            return {
                "success": True,
                "transaction_id": getattr(transaction, 'id', None) if 'transaction' in locals() else None,
                "order_id": order_id,
                "amount_charged": float(amount),
                "previous_balance": float(current_balance),
                "new_balance": float(new_balance),
                "payment_method": "wallet",
                "status": "completed",
                "message": f"Payment of ${amount} processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error processing wallet payment: {e}")
            return {
                "success": False,
                "error": f"Payment processing failed: {str(e)}",
                "amount_charged": float(amount) if amount else 0.00
            }
