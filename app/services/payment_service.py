"""
Payment Service for Nomadly3 - Business Logic Layer
Pure Python layer handling payment verification and processing business logic
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum

from ..repositories.user_repo import UserRepository
from ..repositories.external_integration_repo import (
    FastForexIntegrationRepository, APIUsageLogRepository
)
from ..core.config import config

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    OVERPAID = "overpaid"
    UNDERPAID = "underpaid"

@dataclass
class PaymentVerificationRequest:
    """Payment verification request data"""
    order_id: str
    expected_amount: Decimal
    cryptocurrency: str
    payment_address: str
    user_telegram_id: int

@dataclass
class PaymentVerificationResult:
    """Result of payment verification"""
    order_id: str
    status: PaymentStatus
    expected_amount: Decimal
    received_amount: Decimal
    cryptocurrency: str
    overpaid_amount: Optional[Decimal] = None
    underpaid_amount: Optional[Decimal] = None
    confirmation_count: int = 0
    transaction_hash: Optional[str] = None
    error: Optional[str] = None

@dataclass
class WalletBalanceRequest:
    """Wallet balance operation request"""
    telegram_id: int
    amount: Decimal
    operation_type: str  # 'credit', 'debit'
    description: str
    reference_id: Optional[str] = None

class PaymentService:
    """Service for payment-related business logic"""
    
    def __init__(self, user_repo: UserRepository,
                 fastforex_repo: FastForexIntegrationRepository = None,
                 api_usage_repo: APIUsageLogRepository = None):
        self.user_repo = user_repo
        self.fastforex_repo = fastforex_repo or FastForexIntegrationRepository()
        self.api_usage_repo = api_usage_repo or APIUsageLogRepository()
        
        # Payment business logic constants
        self.SUPPORTED_CRYPTOCURRENCIES = ['BTC', 'ETH', 'LTC', 'DOGE']
        self.MINIMUM_CONFIRMATIONS = {
            'BTC': 1,
            'ETH': 12,
            'LTC': 6,
            'DOGE': 20
        }
        self.PAYMENT_EXPIRY_HOURS = 24
        self.OVERPAYMENT_THRESHOLD = Decimal('0.01')  # $0.01 minimum to credit
        self.UNDERPAYMENT_TOLERANCE = Decimal('0.05')  # 5% tolerance
    
    # Payment Verification
    
    def verify_payment(self, request: PaymentVerificationRequest) -> PaymentVerificationResult:
        """
        Verify cryptocurrency payment with business logic
        Pure business logic for payment validation
        """
        try:
            # Validate user exists
            user = self.user_repo.get_by_telegram_id(request.user_telegram_id)
            if not user:
                return PaymentVerificationResult(
                    order_id=request.order_id,
                    status=PaymentStatus.FAILED,
                    expected_amount=request.expected_amount,
                    received_amount=Decimal('0'),
                    cryptocurrency=request.cryptocurrency,
                    error="User not found"
                )
            
            # Validate cryptocurrency
            if request.cryptocurrency.upper() not in self.SUPPORTED_CRYPTOCURRENCIES:
                return PaymentVerificationResult(
                    order_id=request.order_id,
                    status=PaymentStatus.FAILED,
                    expected_amount=request.expected_amount,
                    received_amount=Decimal('0'),
                    cryptocurrency=request.cryptocurrency,
                    error=f"Unsupported cryptocurrency: {request.cryptocurrency}"
                )
            
            # This would integrate with actual blockchain verification
            # For now, implementing business logic structure
            received_amount = self._get_received_amount(request.payment_address, request.cryptocurrency)
            confirmations = self._get_confirmation_count(request.payment_address, request.cryptocurrency)
            
            # Determine payment status
            status = self._determine_payment_status(
                request.expected_amount, 
                received_amount, 
                confirmations, 
                request.cryptocurrency
            )
            
            # Calculate overpaid/underpaid amounts
            overpaid_amount = None
            underpaid_amount = None
            
            if status == PaymentStatus.OVERPAID:
                overpaid_amount = received_amount - request.expected_amount
            elif status == PaymentStatus.UNDERPAID:
                underpaid_amount = request.expected_amount - received_amount
            
            return PaymentVerificationResult(
                order_id=request.order_id,
                status=status,
                expected_amount=request.expected_amount,
                received_amount=received_amount,
                cryptocurrency=request.cryptocurrency,
                overpaid_amount=overpaid_amount,
                underpaid_amount=underpaid_amount,
                confirmation_count=confirmations
            )
            
        except Exception as e:
            logger.error(f"Error verifying payment for order {request.order_id}: {e}")
            return PaymentVerificationResult(
                order_id=request.order_id,
                status=PaymentStatus.FAILED,
                expected_amount=request.expected_amount,
                received_amount=Decimal('0'),
                cryptocurrency=request.cryptocurrency,
                error=f"Payment verification failed: {str(e)}"
            )
    
    def _determine_payment_status(self, expected: Decimal, received: Decimal, 
                                confirmations: int, cryptocurrency: str) -> PaymentStatus:
        """Determine payment status based on amounts and confirmations"""
        if received == Decimal('0'):
            return PaymentStatus.PENDING
        
        required_confirmations = self.MINIMUM_CONFIRMATIONS.get(cryptocurrency.upper(), 1)
        if confirmations < required_confirmations:
            return PaymentStatus.PENDING
        
        # Calculate tolerance
        tolerance_amount = expected * self.UNDERPAYMENT_TOLERANCE
        
        if received >= expected + self.OVERPAYMENT_THRESHOLD:
            return PaymentStatus.OVERPAID
        elif received < expected - tolerance_amount:
            return PaymentStatus.UNDERPAID
        elif received >= expected - tolerance_amount:
            return PaymentStatus.COMPLETED
        else:
            return PaymentStatus.FAILED
    
    def _get_received_amount(self, address: str, cryptocurrency: str) -> Decimal:
        """Get received amount for address (placeholder for blockchain integration)"""
        # This would integrate with actual blockchain APIs
        # For business logic structure, returning placeholder
        return Decimal('0')
    
    def _get_confirmation_count(self, address: str, cryptocurrency: str) -> int:
        """Get confirmation count for address (placeholder for blockchain integration)"""
        # This would integrate with actual blockchain APIs
        return 0
    
    # Wallet Balance Management
    
    def process_wallet_credit(self, request: WalletBalanceRequest) -> Dict[str, Any]:
        """
        Process wallet balance credit with business validations
        """
        try:
            if request.operation_type != 'credit':
                return {"success": False, "error": "Invalid operation type for credit"}
            
            if request.amount <= 0:
                return {"success": False, "error": "Credit amount must be positive"}
            
            # Get user
            user = self.user_repo.get_by_telegram_id(request.telegram_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Record previous balance for audit
            previous_balance = user.balance_usd
            
            # Add balance
            user.add_balance(request.amount)
            
            # Update user
            updated_user = self.user_repo.update_user(user)
            if not updated_user:
                return {"success": False, "error": "Failed to update user balance"}
            
            logger.info(f"Wallet credited: ${request.amount} for user {request.telegram_id}")
            
            return {
                "success": True,
                "previous_balance": previous_balance,
                "new_balance": updated_user.balance_usd,
                "credited_amount": request.amount,
                "description": request.description
            }
            
        except Exception as e:
            logger.error(f"Error processing wallet credit: {e}")
            return {"success": False, "error": f"Credit processing failed: {str(e)}"}
    
    def process_wallet_debit(self, request: WalletBalanceRequest) -> Dict[str, Any]:
        """
        Process wallet balance debit with business validations
        """
        try:
            if request.operation_type != 'debit':
                return {"success": False, "error": "Invalid operation type for debit"}
            
            if request.amount <= 0:
                return {"success": False, "error": "Debit amount must be positive"}
            
            # Get user
            user = self.user_repo.get_by_telegram_id(request.telegram_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Check sufficient balance
            if not user.has_sufficient_balance(request.amount):
                return {
                    "success": False, 
                    "error": f"Insufficient balance. Required: ${request.amount}, Available: ${user.balance_usd}"
                }
            
            # Record previous balance for audit
            previous_balance = user.balance_usd
            
            # Deduct balance
            success = user.deduct_balance(request.amount)
            if not success:
                return {"success": False, "error": "Failed to deduct balance"}
            
            # Update user
            updated_user = self.user_repo.update_user(user)
            if not updated_user:
                return {"success": False, "error": "Failed to update user balance"}
            
            logger.info(f"Wallet debited: ${request.amount} for user {request.telegram_id}")
            
            return {
                "success": True,
                "previous_balance": previous_balance,
                "new_balance": updated_user.balance_usd,
                "debited_amount": request.amount,
                "description": request.description
            }
            
        except Exception as e:
            logger.error(f"Error processing wallet debit: {e}")
            return {"success": False, "error": f"Debit processing failed: {str(e)}"}
    
    # Payment Processing Logic
    
    def process_payment_completion(self, verification_result: PaymentVerificationResult) -> Dict[str, Any]:
        """
        Process completed payment with business logic
        Handles overpayments, underpayments, and wallet crediting
        """
        try:
            # This would integrate with order repository to get user from order
            # For now, implementing business logic structure
            user = None  # Would be retrieved from order data
            
            if verification_result.status == PaymentStatus.COMPLETED:
                return {
                    "success": True,
                    "action": "order_fulfilled",
                    "message": "Payment completed successfully"
                }
            
            elif verification_result.status == PaymentStatus.OVERPAID:
                # Credit overpaid amount to wallet
                overpaid = verification_result.overpaid_amount
                if overpaid and overpaid >= self.OVERPAYMENT_THRESHOLD and user:
                    credit_request = WalletBalanceRequest(
                        telegram_id=user.telegram_id,
                        amount=overpaid,
                        operation_type='credit',
                        description=f"Overpayment credit for order {verification_result.order_id}"
                    )
                    
                    credit_result = self.process_wallet_credit(credit_request)
                    
                    return {
                        "success": True,
                        "action": "order_fulfilled_with_credit",
                        "overpaid_amount": overpaid,
                        "wallet_credited": credit_result.get("success", False),
                        "message": f"Payment completed with ${overpaid} credited to wallet"
                    }
            
            elif verification_result.status == PaymentStatus.UNDERPAID:
                underpaid = verification_result.underpaid_amount
                return {
                    "success": False,
                    "action": "payment_incomplete",
                    "underpaid_amount": underpaid,
                    "message": f"Payment incomplete. Missing ${underpaid}"
                }
            
            else:
                return {
                    "success": False,
                    "action": "payment_failed",
                    "message": f"Payment failed with status: {verification_result.status.value}"
                }
            
            return {
                "success": False,
                "action": "unknown_status", 
                "message": "Unknown payment status"
            }
                
        except Exception as e:
            logger.error(f"Error processing payment completion: {e}")
            return {"success": False, "error": f"Payment processing failed: {str(e)}"}
    
    # Payment Analytics & Management
    
    def get_user_payment_history(self, telegram_id: int, limit: int = 50) -> Dict[str, Any]:
        """Get user payment history with analytics"""
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {"error": "User not found"}
            
            # This would integrate with payment history repository in real implementation
            # For now, providing business logic structure
            
            return {
                "user_id": telegram_id,
                "total_payments": 0,  # Would be calculated from actual payment records
                "total_spent": user.get_total_spent(),
                "wallet_balance": user.balance_usd,
                "payment_methods_used": [],  # Would be from payment records
                "recent_payments": []  # Would be from payment records
            }
            
        except Exception as e:
            logger.error(f"Error getting payment history: {e}")
            return {"error": f"Failed to get payment history: {str(e)}"}
    
    def calculate_payment_statistics(self, telegram_id: int) -> Dict[str, Any]:
        """Calculate comprehensive payment statistics for user"""
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {"error": "User not found"}
            
            # Business logic for payment analytics
            total_spent = user.get_total_spent()
            current_balance = user.balance_usd
            
            # Determine user tier based on spending
            user_tier = self._determine_user_tier(total_spent)
            
            return {
                "user_id": telegram_id,
                "total_spent": total_spent,
                "current_balance": current_balance,
                "user_tier": user_tier,
                "is_premium_user": user.is_premium_user(),
                "lifetime_value": total_spent + current_balance
            }
            
        except Exception as e:
            logger.error(f"Error calculating payment statistics: {e}")
            return {"error": f"Failed to calculate statistics: {str(e)}"}
    
    def _determine_user_tier(self, total_spent: Decimal) -> str:
        """Determine user tier based on total spending"""
        if total_spent >= Decimal('1000'):
            return "diamond"
        elif total_spent >= Decimal('500'):
            return "platinum"
        elif total_spent >= Decimal('200'):
            return "gold"
        elif total_spent >= Decimal('100'):
            return "silver"
        else:
            return "bronze"
    
    # Payment Validation Helpers
    
    def validate_payment_amount(self, amount: Decimal, cryptocurrency: str) -> Dict[str, Any]:
        """Validate payment amount for cryptocurrency"""
        if amount <= 0:
            return {"valid": False, "error": "Payment amount must be positive"}
        
        # Cryptocurrency-specific minimums
        minimums = {
            'BTC': Decimal('0.0001'),
            'ETH': Decimal('0.001'),
            'LTC': Decimal('0.01'),
            'DOGE': Decimal('1.0')
        }
        
        minimum = minimums.get(cryptocurrency.upper(), Decimal('0.01'))
        if amount < minimum:
            return {"valid": False, "error": f"Minimum {cryptocurrency} payment: {minimum}"}
        
        return {"valid": True}
    
    def is_payment_expired(self, payment_created_at: datetime) -> bool:
        """Check if payment has expired"""
        expiry_time = payment_created_at + timedelta(hours=self.PAYMENT_EXPIRY_HOURS)
        return datetime.utcnow() > expiry_time
    
    def calculate_cryptocurrency_amount(self, usd_amount: Decimal, cryptocurrency: str, 
                                      exchange_rate: Decimal) -> Decimal:
        """Calculate cryptocurrency amount from USD amount"""
        if exchange_rate <= 0:
            raise ValueError("Exchange rate must be positive")
        
        crypto_amount = usd_amount / exchange_rate
        
        # Round to appropriate precision for cryptocurrency
        precision_map = {
            'BTC': 8,
            'ETH': 6,
            'LTC': 8,
            'DOGE': 2
        }
        
        precision = precision_map.get(cryptocurrency.upper(), 6)
        return crypto_amount.quantize(Decimal('0.1') ** precision)
    def initiate_domain_payment(self, telegram_id: int, domain_name: str, amount: Decimal, 
                               payment_method: str = "crypto") -> Dict[str, Any]:
        """
        Initiate payment for domain registration - UI workflow method
        """
        try:
            # Validate user
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Generate order ID
            order_id = f"domain_{telegram_id}_{int(datetime.utcnow().timestamp())}"
            
            # Validate amount
            if amount <= 0:
                return {"success": False, "error": "Invalid payment amount"}
            
            if payment_method == "wallet":
                # Check wallet balance
                current_balance = getattr(user, 'balance_usd', Decimal('0.00'))
                if current_balance < amount:
                    return {
                        "success": False,
                        "error": "Insufficient wallet balance",
                        "required_amount": float(amount),
                        "available_balance": float(current_balance),
                        "payment_method": "wallet"
                    }
                
                # Wallet payment can be processed immediately
                return {
                    "success": True,
                    "order_id": order_id,
                    "payment_method": "wallet",
                    "amount": float(amount),
                    "status": "ready_for_processing",
                    "domain_name": domain_name,
                    "immediate_processing": True
                }
                
            elif payment_method in self.SUPPORTED_CRYPTOCURRENCIES:
                # Generate cryptocurrency payment
                crypto_amount = self._calculate_crypto_amount(amount, payment_method)
                payment_address = self._generate_payment_address(order_id, payment_method)
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "payment_method": payment_method,
                    "amount_usd": float(amount),
                    "amount_crypto": crypto_amount,
                    "cryptocurrency": payment_method.upper(),
                    "payment_address": payment_address,
                    "expires_at": (datetime.utcnow() + timedelta(hours=self.PAYMENT_EXPIRY_HOURS)).isoformat(),
                    "domain_name": domain_name,
                    "status": "awaiting_payment",
                    "confirmation_required": self.MINIMUM_CONFIRMATIONS.get(payment_method.upper(), 1)
                }
            else:
                return {
                    "success": False,
                    "error": f"Unsupported payment method: {payment_method}",
                    "supported_methods": ["wallet"] + self.SUPPORTED_CRYPTOCURRENCIES
                }
                
        except Exception as e:
            logger.error(f"Error initiating domain payment: {e}")
            return {
                "success": False,
                "error": f"Payment initiation failed: {str(e)}",
                "order_id": None
            }
    
    def _calculate_crypto_amount(self, usd_amount: Decimal, cryptocurrency: str) -> float:
        """Calculate cryptocurrency amount from USD (placeholder implementation)"""
        # This would integrate with real exchange rate APIs
        exchange_rates = {
            "btc": Decimal("0.000025"),  # ~$40k per BTC
            "eth": Decimal("0.0004"),    # ~$2.5k per ETH  
            "ltc": Decimal("0.012"),     # ~$80 per LTC
            "doge": Decimal("15.0")      # ~$0.07 per DOGE
        }
        
        rate = exchange_rates.get(cryptocurrency.lower(), Decimal("1.0"))
        return float(usd_amount * rate)
    
    def _generate_payment_address(self, order_id: str, cryptocurrency: str) -> str:
        """Generate payment address (placeholder implementation)"""
        # This would integrate with actual cryptocurrency payment processors
        import hashlib
        address_hash = hashlib.md5(f"{order_id}_{cryptocurrency}".encode()).hexdigest()
        
        address_prefixes = {
            "btc": "bc1q",
            "eth": "0x",
            "ltc": "ltc1q",
            "doge": "D"
        }
        
        prefix = address_prefixes.get(cryptocurrency.lower(), "addr_")
        return f"{prefix}{address_hash[:26]}"
