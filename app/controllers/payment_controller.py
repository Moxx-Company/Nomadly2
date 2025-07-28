"""
Payment Controller - Handles payment processing operations
"""

from typing import Dict, Any, List
from fastapi import HTTPException
from .base_controller import BaseController
from app.schemas.wallet_schemas import (
    PaymentInitiationRequest,
    PaymentConfirmationRequest
)
import logging

logger = logging.getLogger(__name__)

class PaymentController(BaseController):
    """Controller for payment processing operations"""
    
    def __init__(self, payment_service, wallet_service, user_service):
        super().__init__()
        self.payment_service = payment_service
        self.wallet_service = wallet_service
        self.user_service = user_service
    
    async def initiate_crypto_payment(self, request: PaymentInitiationRequest, 
                                    telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Initiate cryptocurrency payment
        - Validates payment request
        - Generates crypto address
        - Creates payment monitoring
        - Returns payment details DTO
        """
        try:
            # Validate input
            payment_data = self.validate_input(request)
            
            self.logger.info(f"Initiating crypto payment for user {telegram_id}")
            
            # Verify user exists
            user = await self.user_service.get_user_by_telegram_id(telegram_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Call payment service
            payment_result = await self.payment_service.initiate_crypto_payment(
                telegram_id=telegram_id,
                amount_usd=payment_data['amount_usd'],
                cryptocurrency=payment_data['cryptocurrency'],
                order_id=payment_data.get('order_id'),
                description=payment_data.get('description', 'Domain registration')
            )
            
            # Map to DTO
            payment_dto = {
                "payment_id": payment_result.payment_id,
                "order_id": payment_result.order_id,
                "cryptocurrency": payment_result.cryptocurrency,
                "amount_crypto": payment_result.amount_crypto,
                "amount_usd": payment_result.amount_usd,
                "crypto_address": payment_result.crypto_address,
                "qr_code_data": payment_result.qr_code_data,
                "payment_url": payment_result.payment_url,
                "expires_at": payment_result.expires_at.isoformat(),
                "minimum_confirmations": payment_result.min_confirmations,
                "status": "pending",
                "created_at": payment_result.created_at.isoformat()
            }
            
            return self.success_response(
                data=payment_dto,
                message=f"Crypto payment initiated: {payment_data['cryptocurrency']} {payment_result.amount_crypto}"
            )
            
        except Exception as e:
            self.handle_service_error(e, "initiate crypto payment")
    
    async def get_payment_status(self, payment_id: str, telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Get payment status
        - Validates payment ownership
        - Checks payment status
        - Returns status DTO with transaction details
        """
        try:
            # Validate input parameters
            if not payment_id or not payment_id.strip():
                raise HTTPException(status_code=400, detail="Invalid payment_id")
            if not telegram_id or telegram_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid telegram_id")
            
            self.logger.info(f"Checking payment status: {payment_id}")
            
            # Call payment service
            payment_status = await self.payment_service.get_payment_status(
                payment_id=payment_id,
                telegram_id=telegram_id
            )
            
            if not payment_status:
                raise HTTPException(status_code=404, detail="Payment not found")
            
            # Map to DTO
            status_dto = {
                "payment_id": payment_status.payment_id,
                "order_id": payment_status.order_id,
                "status": payment_status.status,
                "cryptocurrency": payment_status.cryptocurrency,
                "amount_expected": payment_status.amount_expected,
                "amount_received": payment_status.amount_received,
                "confirmations": payment_status.confirmations,
                "required_confirmations": payment_status.required_confirmations,
                "transaction_hash": payment_status.tx_hash,
                "expires_at": payment_status.expires_at.isoformat() if payment_status.expires_at else None,
                "confirmed_at": payment_status.confirmed_at.isoformat() if payment_status.confirmed_at else None,
                "overpayment": payment_status.amount_received > payment_status.amount_expected if payment_status.amount_received else False
            }
            
            # Add transaction details if confirmed
            if payment_status.status == 'confirmed' and payment_status.tx_hash:
                status_dto["transaction_details"] = {
                    "hash": payment_status.tx_hash,
                    "block_height": getattr(payment_status, 'block_height', None),
                    "network_fee": getattr(payment_status, 'network_fee', None),
                    "explorer_url": self._get_explorer_url(payment_status.cryptocurrency, payment_status.tx_hash)
                }
            
            return self.success_response(
                data=status_dto,
                message=f"Payment status: {payment_status.status}"
            )
            
        except Exception as e:
            self.handle_service_error(e, "get payment status")
    
    async def confirm_payment(self, request: PaymentConfirmationRequest, 
                            telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Manually confirm payment
        - Validates payment details
        - Processes confirmation
        - Updates wallet balance if needed
        - Returns confirmation DTO
        """
        try:
            # Validate input
            confirmation_data = self.validate_input(request)
            
            self.logger.info(f"Manual payment confirmation: {confirmation_data['payment_id']}")
            
            # Call payment service
            confirmation_result = await self.payment_service.confirm_payment(
                payment_id=confirmation_data['payment_id'],
                transaction_hash=confirmation_data['transaction_hash'],
                amount_received=confirmation_data.get('amount_received'),
                telegram_id=telegram_id
            )
            
            # Map to DTO
            confirmation_dto = {
                "payment_id": confirmation_result.payment_id,
                "order_id": confirmation_result.order_id,
                "status": "confirmed",
                "transaction_hash": confirmation_result.tx_hash,
                "amount_received": confirmation_result.amount_received,
                "overpayment_credited": confirmation_result.overpayment_credited,
                "wallet_balance_updated": confirmation_result.wallet_updated,
                "confirmed_at": confirmation_result.confirmed_at.isoformat()
            }
            
            return self.success_response(
                data=confirmation_dto,
                message="Payment confirmed successfully"
            )
            
        except Exception as e:
            self.handle_service_error(e, "confirm payment")
    
    async def get_user_payment_history(self, telegram_id: int, status: str = None, 
                                     page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Controller: Get user payment history
        - Retrieves user payments with filters
        - Maps to DTOs with transaction details
        - Returns paginated response
        """
        try:
            # Validate input parameters
            if not telegram_id or telegram_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid telegram_id")
            if status and status not in ['pending', 'confirmed', 'failed', 'expired']:
                raise HTTPException(status_code=400, detail="Invalid status filter")
            
            self.logger.info(f"Fetching payment history for user {telegram_id}")
            
            # Call payment service
            payment_history = await self.payment_service.get_user_payment_history(
                telegram_id=telegram_id,
                status=status,
                page=page,
                per_page=per_page
            )
            
            # Map payments to DTOs
            payment_dtos = []
            for payment in payment_history.payments:
                payment_dto = {
                    "payment_id": payment.payment_id,
                    "order_id": payment.order_id,
                    "cryptocurrency": payment.cryptocurrency,
                    "amount_usd": float(payment.amount_usd),
                    "amount_crypto": float(payment.amount_crypto) if payment.amount_crypto else None,
                    "status": payment.status,
                    "transaction_hash": payment.tx_hash,
                    "created_at": payment.created_at.isoformat(),
                    "confirmed_at": payment.confirmed_at.isoformat() if payment.confirmed_at else None,
                    "description": getattr(payment, 'description', 'Payment')
                }
                payment_dtos.append(payment_dto)
            
            return self.success_response(
                data={
                    "items": payment_dtos,
                    "pagination": {
                        "total": payment_history.total_count,
                        "page": page,
                        "per_page": per_page,
                        "pages": (payment_history.total_count + per_page - 1) // per_page
                    }
                },
                message=f"Retrieved {len(payment_dtos)} payment records"
            )
            
        except Exception as e:
            self.handle_service_error(e, "get payment history")
    
    async def process_overpayment(self, payment_id: str, telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Process cryptocurrency overpayment
        - Handles overpayment scenarios
        - Credits wallet balance
        - Returns processing result DTO
        """
        try:
            # Validate input parameters
            if not payment_id or not payment_id.strip():
                raise HTTPException(status_code=400, detail="Invalid payment_id")
            if not telegram_id or telegram_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid telegram_id")
            
            self.logger.info(f"Processing overpayment for payment {payment_id}")
            
            # Call payment service
            overpayment_result = await self.payment_service.process_overpayment(
                payment_id=payment_id,
                telegram_id=telegram_id
            )
            
            # Map to DTO
            overpayment_dto = {
                "payment_id": payment_id,
                "overpayment_amount": overpayment_result.overpayment_amount,
                "credited_to_wallet": overpayment_result.credited_amount,
                "new_wallet_balance": overpayment_result.new_balance,
                "processing_fee": overpayment_result.processing_fee,
                "processed_at": overpayment_result.processed_at.isoformat()
            }
            
            return self.success_response(
                data=overpayment_dto,
                message=f"Overpayment processed: ${overpayment_result.credited_amount} credited to wallet"
            )
            
        except Exception as e:
            self.handle_service_error(e, "process overpayment")
    
    def _get_explorer_url(self, cryptocurrency: str, tx_hash: str) -> str:
        """Generate blockchain explorer URL for transaction"""
        explorers = {
            'BTC': f"https://blockstream.info/tx/{tx_hash}",
            'ETH': f"https://etherscan.io/tx/{tx_hash}",
            'LTC': f"https://blockchair.com/litecoin/transaction/{tx_hash}",
            'DOGE': f"https://dogechain.info/tx/{tx_hash}"
        }
        return explorers.get(cryptocurrency, f"https://blockchain.info/tx/{tx_hash}")