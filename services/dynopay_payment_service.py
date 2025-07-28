"""
Enhanced Payment Service with Dynopay Integration
Provides comprehensive payment processing through multiple providers
"""

import logging
import uuid
from decimal import Decimal
from typing import Dict, Optional, List, Any, Union
from datetime import datetime, timedelta
from apis.dynopay import DynopayAPI
from database import get_db_manager
from database import User

logger = logging.getLogger(__name__)


class DynopayPaymentService:
    """Enhanced payment service with Dynopay integration"""

    def __init__(self):
        self.dynopay = DynopayAPI()
        self.db = get_db_manager()
        
        # Payment methods available
        self.payment_methods = {
            "dynopay_wallet": "Dynopay Wallet",
            "dynopay_payment": "Dynopay Payment Link",
            "dynopay_crypto": "Dynopay Cryptocurrency",
            "dynopay_funds": "Dynopay Add Funds"
        }
    
    async def ensure_dynopay_user(self, telegram_id: int) -> Dict[str, Any]:
        """Ensure user exists in both local and Dynopay systems"""
        try:
            logger.info(f"👤 Ensuring Dynopay user for Telegram ID: {telegram_id}")
            
            # Get or create local user
            local_user = self.db.get_user_by_telegram_id(telegram_id)
            if not local_user:
                logger.error(f"❌ Local user not found for Telegram ID: {telegram_id}")
                return {"success": False, "error": "Local user not found"}
            
            # Check if user already has Dynopay credentials
            if hasattr(local_user, 'dynopay_token') and local_user.dynopay_token:
                logger.info(f"✅ User already has Dynopay credentials")
                return {
                    "success": True,
                    "token": local_user.dynopay_token,
                    "customer_id": getattr(local_user, 'dynopay_customer_id', None),
                    "existing_user": True
                }
            
            # Create Dynopay user
            user_email = getattr(local_user, 'email', None) or f"user{telegram_id}@nomadly.temp"
            user_name = getattr(local_user, 'name', f"User {telegram_id}")
            user_mobile = getattr(local_user, 'phone', None)
            
            dynopay_result = await self.dynopay.create_user(
                email=user_email,
                name=user_name,
                mobile=user_mobile
            )
            
            if dynopay_result["success"]:
                # Store Dynopay credentials in local database
                await self._update_user_dynopay_credentials(
                    telegram_id,
                    dynopay_result["token"],
                    dynopay_result["customer_id"]
                )
                
                logger.info(f"✅ Dynopay user created and linked")
                return {
                    "success": True,
                    "token": dynopay_result["token"],
                    "customer_id": dynopay_result["customer_id"],
                    "existing_user": False,
                    "message": dynopay_result.get("message")
                }
            else:
                logger.error(f"❌ Failed to create Dynopay user: {dynopay_result['error']}")
                return {"success": False, "error": dynopay_result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Ensure Dynopay user error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _update_user_dynopay_credentials(
        self, 
        telegram_id: int, 
        token: str, 
        customer_id: str
    ):
        """Update user with Dynopay credentials"""
        try:
            # This would need to be implemented based on your database structure
            # For now, we'll use a simple approach
            user = self.db.get_user_by_telegram_id(telegram_id)
            if user:
                # Store credentials (implementation depends on your database schema)
                # You might need to add these fields to your User model
                setattr(user, 'dynopay_token', token)
                setattr(user, 'dynopay_customer_id', customer_id)
                
                # Update in database
                self.db.session.commit()
                logger.info(f"✅ Updated user Dynopay credentials")
            
        except Exception as e:
            logger.error(f"❌ Error updating Dynopay credentials: {str(e)}")
    
    async def create_payment_link(
        self,
        telegram_id: int,
        amount: float,
        service_type: str,
        service_details: Dict,
        redirect_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create Dynopay payment link for service purchase"""
        try:
            logger.info(f"💳 Creating Dynopay payment link: ${amount} for {service_type}")
            
            # Ensure user exists in Dynopay
            user_result = await self.ensure_dynopay_user(telegram_id)
            if not user_result["success"]:
                return user_result
            
            # Create order in local database
            order = self.db.create_order(
                telegram_id=telegram_id,
                service_type=service_type,
                service_details=service_details,
                amount=amount,
                payment_method="dynopay_payment"
            )
            
            # Set redirect URI (default to success page if not provided)
            if not redirect_uri:
                redirect_uri = f"https://nomadly.com/payment/success?order_id={order.order_id}"
            
            # Prepare metadata for the payment
            meta_data = {
                "product_name": service_details.get("domain_name", service_type),
                "order_id": order.order_id,
                "telegram_id": str(telegram_id),
                "service_type": service_type,
                "timestamp": datetime.now().isoformat()
            }
            
            # Create payment with Dynopay
            payment_result = await self.dynopay.create_payment(
                user_token=user_result["token"],
                amount=amount,
                redirect_uri=redirect_uri,
                meta_data=meta_data
            )
            
            if payment_result["success"]:
                # Update order with payment details
                order.payment_reference = payment_result.get("payment_id", "dynopay_payment")
                order.status = "payment_pending"
                self.db.session.commit()
                
                logger.info(f"✅ Dynopay payment link created successfully")
                return {
                    "success": True,
                    "order_id": order.order_id,
                    "payment_url": payment_result["redirect_url"],
                    "amount": amount,
                    "currency": "USD",
                    "message": payment_result.get("message")
                }
            else:
                logger.error(f"❌ Dynopay payment creation failed: {payment_result['error']}")
                return {"success": False, "error": payment_result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Create payment link error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def add_funds_to_wallet(
        self,
        telegram_id: int,
        amount: float,
        redirect_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add funds to user's Dynopay wallet"""
        try:
            logger.info(f"💰 Adding ${amount} to Dynopay wallet for user {telegram_id}")
            
            # Ensure user exists in Dynopay
            user_result = await self.ensure_dynopay_user(telegram_id)
            if not user_result["success"]:
                return user_result
            
            # Set redirect URI
            if not redirect_uri:
                redirect_uri = f"https://nomadly.com/wallet/success?telegram_id={telegram_id}"
            
            # Add funds with Dynopay
            funds_result = await self.dynopay.add_funds(
                user_token=user_result["token"],
                amount=amount,
                redirect_uri=redirect_uri
            )
            
            if funds_result["success"]:
                # Record balance transaction in local database
                self.db.create_balance_transaction(
                    telegram_id=telegram_id,
                    amount=amount,
                    transaction_type="add_funds_dynopay",
                    description=f"Dynopay wallet funding: ${amount}",
                    status="pending"
                )
                
                logger.info(f"✅ Dynopay funds addition link created")
                return {
                    "success": True,
                    "payment_url": funds_result["redirect_url"],
                    "amount": amount,
                    "currency": "USD",
                    "message": funds_result.get("message")
                }
            else:
                logger.error(f"❌ Dynopay add funds failed: {funds_result['error']}")
                return {"success": False, "error": funds_result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Add funds error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_balance(self, telegram_id: int) -> Dict[str, Any]:
        """Get user's Dynopay wallet balance"""
        try:
            logger.info(f"💰 Getting Dynopay balance for user {telegram_id}")
            
            # Ensure user exists in Dynopay
            user_result = await self.ensure_dynopay_user(telegram_id)
            if not user_result["success"]:
                return user_result
            
            # Get balance from Dynopay
            balance_result = await self.dynopay.get_user_balance(
                user_token=user_result["token"]
            )
            
            if balance_result["success"]:
                logger.info(f"✅ Balance retrieved: {balance_result['amount']} {balance_result['currency']}")
                return {
                    "success": True,
                    "amount": balance_result["amount"],
                    "currency": balance_result["currency"],
                    "message": balance_result.get("message")
                }
            else:
                logger.error(f"❌ Balance retrieval failed: {balance_result['error']}")
                return {"success": False, "error": balance_result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Get balance error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_transactions(self, telegram_id: int) -> Dict[str, Any]:
        """Get user's Dynopay transaction history"""
        try:
            logger.info(f"📊 Getting Dynopay transactions for user {telegram_id}")
            
            # Ensure user exists in Dynopay
            user_result = await self.ensure_dynopay_user(telegram_id)
            if not user_result["success"]:
                return user_result
            
            # Get transactions from Dynopay
            transactions_result = await self.dynopay.get_user_transactions(
                user_token=user_result["token"]
            )
            
            if transactions_result["success"]:
                transactions = transactions_result["transactions"]
                logger.info(f"✅ Retrieved {len(transactions)} transactions")
                return {
                    "success": True,
                    "transactions": transactions,
                    "count": len(transactions),
                    "message": transactions_result.get("message")
                }
            else:
                logger.error(f"❌ Transactions retrieval failed: {transactions_result['error']}")
                return {"success": False, "error": transactions_result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Get transactions error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_crypto_payment(
        self,
        telegram_id: int,
        amount: float,
        currency: str,
        service_type: str,
        service_details: Dict
    ) -> Dict[str, Any]:
        """Create cryptocurrency payment through Dynopay"""
        try:
            logger.info(f"₿ Creating Dynopay crypto payment: {currency} ${amount}")
            
            # Ensure user exists in Dynopay
            user_result = await self.ensure_dynopay_user(telegram_id)
            if not user_result["success"]:
                return user_result
            
            # Create order in local database
            order = self.db.create_order(
                telegram_id=telegram_id,
                service_type=service_type,
                service_details=service_details,
                amount=amount,
                payment_method=f"dynopay_crypto_{currency}"
            )
            
            # Generate callback URL for webhooks
            callback_url = f"https://nomadly2-webhook.replit.app/webhook/dynopay/{order.order_id}"
            
            # Prepare metadata
            meta_data = {
                "product_name": service_details.get("domain_name", service_type),
                "order_id": order.order_id,
                "telegram_id": str(telegram_id),
                "service_type": service_type,
                "timestamp": datetime.now().isoformat()
            }
            
            # Create crypto payment with Dynopay
            crypto_result = await self.dynopay.create_crypto_payment(
                user_token=user_result["token"],
                amount=amount,
                currency=currency,
                callback_url=callback_url,
                meta_data=meta_data
            )
            
            if crypto_result["success"]:
                payment_data = crypto_result["payment_data"]
                
                # Update order with payment details
                order.payment_reference = payment_data.get("payment_id", f"dynopay_crypto_{currency}")
                order.status = "payment_pending"
                self.db.session.commit()
                
                logger.info(f"✅ Dynopay crypto payment created successfully")
                return {
                    "success": True,
                    "order_id": order.order_id,
                    "payment_address": payment_data.get("address"),
                    "qr_code": payment_data.get("qr_code"),
                    "amount": amount,
                    "currency": currency,
                    "payment_data": payment_data,
                    "message": crypto_result.get("message")
                }
            else:
                logger.error(f"❌ Dynopay crypto payment failed: {crypto_result['error']}")
                return {"success": False, "error": crypto_result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Create crypto payment error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_supported_currencies(self) -> Dict[str, Any]:
        """Get supported cryptocurrencies from Dynopay"""
        try:
            logger.info(f"💱 Getting supported currencies from Dynopay")
            
            currencies_result = await self.dynopay.get_supported_currencies()
            
            if currencies_result["success"]:
                currencies = currencies_result["currencies"]
                logger.info(f"✅ Retrieved {len(currencies)} supported currencies")
                return {
                    "success": True,
                    "currencies": currencies,
                    "count": len(currencies),
                    "message": currencies_result.get("message")
                }
            else:
                logger.error(f"❌ Currencies retrieval failed: {currencies_result['error']}")
                return {"success": False, "error": currencies_result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Get currencies error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_webhook_notification(self, order_id: str, webhook_data: Dict) -> Dict[str, Any]:
        """Process webhook notification from Dynopay"""
        try:
            logger.info(f"🔔 Processing Dynopay webhook for order: {order_id}")
            
            # Get order from database
            order = self.db.get_order_by_id(order_id)
            if not order:
                logger.error(f"❌ Order not found: {order_id}")
                return {"success": False, "error": "Order not found"}
            
            # Process webhook based on status
            status = webhook_data.get("status", "unknown").lower()
            transaction_id = webhook_data.get("transaction_id")
            amount = webhook_data.get("amount")
            currency = webhook_data.get("currency", "USD")
            
            logger.info(f"📊 Webhook status: {status}, Amount: {amount} {currency}")
            
            if status in ["completed", "confirmed", "success"]:
                # Payment successful
                order.status = "payment_completed"
                order.payment_reference = transaction_id or order.payment_reference
                order.updated_at = datetime.now()
                self.db.session.commit()
                
                # Trigger service fulfillment
                await self._fulfill_order(order)
                
                logger.info(f"✅ Payment completed for order: {order_id}")
                return {"success": True, "message": "Payment processed successfully"}
                
            elif status in ["failed", "cancelled", "expired"]:
                # Payment failed
                order.status = "payment_failed"
                order.updated_at = datetime.now()
                self.db.session.commit()
                
                logger.warning(f"⚠️ Payment failed for order: {order_id}")
                return {"success": True, "message": "Payment failure processed"}
                
            else:
                # Unknown status, log for investigation
                logger.warning(f"⚠️ Unknown webhook status: {status} for order: {order_id}")
                return {"success": True, "message": "Webhook processed"}
                
        except Exception as e:
            logger.error(f"❌ Webhook processing error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _fulfill_order(self, order):
        """Fulfill order after successful payment"""
        try:
            logger.info(f"🚀 Fulfilling order: {order.order_id}")
            
            # This would integrate with your existing fulfillment system
            # For example, trigger domain registration, hosting setup, etc.
            
            if order.service_type == "domain_registration":
                # Trigger domain registration
                from domain_service import DomainService
                domain_service = DomainService()
                await domain_service.register_domain(order)
                
            elif order.service_type == "hosting":
                # Trigger hosting setup
                from apis.cpanel import CpanelAPI
                cpanel = CpanelAPI()
                await cpanel.create_account(order)
                
            # Add more service types as needed
            
            logger.info(f"✅ Order fulfillment initiated: {order.order_id}")
            
        except Exception as e:
            logger.error(f"❌ Order fulfillment error: {str(e)}")
    
    async def test_dynopay_connection(self) -> Dict[str, Any]:
        """Test Dynopay API connection"""
        return await self.dynopay.test_connection()
    
    def get_payment_methods(self) -> Dict[str, str]:
        """Get available payment methods"""
        return self.payment_methods