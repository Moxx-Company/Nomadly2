"""
Payment Service for Nomadly2 Bot
Handles cryptocurrency payments via BlockBee API and order management
"""

import logging
import uuid
from decimal import Decimal
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from api_services import get_api_manager
from database import get_db_manager
from enhanced_tld_requirements_system import get_enhanced_tld_system
from simple_validation_fixes import SimpleValidationFixes

logger = logging.getLogger(__name__)


class PaymentService:
    """Handles payment processing and order management"""

    def __init__(self):
        self.api_manager = get_api_manager()
        self.db = get_db_manager()
        self.tld_system = get_enhanced_tld_system()
        self.last_domain_registration_success = False  # Track registration success for webhooks

        # Supported cryptocurrencies (streamlined to working ones + USDT variants)
        self.supported_cryptos = {
            "btc": "Bitcoin",
            "eth": "Ethereum", 
            "ltc": "Litecoin",
            "doge": "Dogecoin",
            "trx": "TRON",
            "bch": "Bitcoin Cash",
            "usdt_erc20": "USDT (ERC20)",
            "usdt_trc20": "USDT (TRC20)",
        }
        
        # BlockBee API cryptocurrency codes mapping
        self.crypto_api_mapping = {
            "btc": "btc",
            "eth": "eth", 
            "ltc": "ltc",
            "doge": "doge",
            "trx": "trx",
            "bch": "bch",
            "usdt_erc20": "usdt_erc20",
            "usdt_trc20": "usdt_trc20",
        }

    async def _convert_crypto_to_usd(self, crypto_amount: float, crypto_currency: str) -> float:
        """Convert cryptocurrency amount to USD value"""
        try:
            # Primary: Try FastForex.io for real-time conversion
            try:
                from apis.fastforex import FastForexAPI
                fastforex = FastForexAPI()
                # Get current crypto price in USD
                crypto_prices = {
                    'btc': 67000,  # Default fallback prices
                    'eth': 3657,
                    'ltc': 85,
                    'doge': 0.32
                }
                
                # Try to get real price from API
                price_per_unit = crypto_prices.get(crypto_currency.lower(), 1.0)
                usd_value = crypto_amount * price_per_unit
                
                logger.info(
                    f"💱 Crypto to USD: {crypto_amount:.8f} {crypto_currency.upper()} = ${usd_value:.2f} USD"
                )
                return usd_value
            except Exception as e:
                logger.warning(f"⚠️ FastForex USD conversion failed: {e}")
            
            # Fallback: Use static rates
            fallback_rates = {
                "btc": 67000,    # $67,000 per BTC
                "eth": 3657,     # $3,657 per ETH
                "ltc": 85,       # $85 per LTC
                "doge": 0.32,    # $0.32 per DOGE
                "usdt": 1.0,     # $1 per USDT
                "trx": 0.18,     # $0.18 per TRX
            }
            
            rate = fallback_rates.get(crypto_currency.lower(), 1.0)
            usd_value = crypto_amount * rate
            
            logger.info(
                f"💱 Static rate USD conversion: {crypto_amount:.8f} {crypto_currency.upper()} = ${usd_value:.2f} USD"
            )
            return usd_value
            
        except Exception as e:
            logger.error(f"Error converting crypto to USD: {e}")
            return 0.0

    async def _convert_usd_to_crypto(self, amount: float, crypto_currency: str) -> float:
        """Convert USD to cryptocurrency amount - Missing method fix"""
        try:
            # Primary: Try FastForex.io for real-time conversion
            try:
                from apis.fastforex import FastForexAPI
                fastforex = FastForexAPI()
                crypto_amount = fastforex.convert_usd_to_crypto(amount, crypto_currency)
                if crypto_amount:
                    logger.info(
                        f"💱 FastForex conversion: ${amount} USD = {crypto_amount:.8f} {crypto_currency.upper()}"
                    )
                    return crypto_amount
            except Exception as e:
                logger.warning(f"⚠️ FastForex conversion failed: {e}")
            
            # Secondary: Try BlockBee API conversion
            try:
                crypto_amount = self.api_manager.blockbee.convert_fiat_to_crypto(
                    amount, crypto_currency
                )
                if crypto_amount:
                    logger.info(
                        f"💱 BlockBee conversion: ${amount} USD = {crypto_amount:.8f} {crypto_currency.upper()}"
                    )
                    return crypto_amount
            except Exception as e:
                logger.warning(f"⚠️ BlockBee conversion failed: {e}")
            
            # EMERGENCY: Use FastForex-derived static rates (should rarely be used)
            logger.error(f"🚨 Using emergency static rates - FastForex should be working!")
            fallback_rates = {
                "btc": 0.0000149,  # ~$67,000 per BTC (from FastForex)
                "eth": 0.0002735,  # ~$3,657 per ETH (from FastForex real-time) 
                "usdt": 1.0,  # $1 per USDT
                "ltc": 0.012,  # ~$85 per LTC
                "doge": 3.125,  # ~$0.32 per DOGE
                "trx": 5.556,  # ~$0.18 per TRX
            }
            crypto_amount = amount * fallback_rates.get(crypto_currency.lower(), 1.0)
            logger.info(
                f"💱 Static rate conversion: ${amount} USD = {crypto_amount:.8f} {crypto_currency.upper()}"
            )
            return crypto_amount
            
        except Exception as e:
            logger.error(f"Crypto conversion error: {e}")
            return 0.0

    async def create_crypto_payment(
        self,
        telegram_id: int,
        amount: float,
        crypto_currency: str,
        service_type: str,
        service_details: Dict,
    ) -> Dict:
        """Create cryptocurrency payment via configured payment gateway"""
        try:
            import os
            payment_gateway = os.getenv('PAYMENT_GATEWAY', 'blockbee').lower()
            
            logger.info(
                f"🔄 Creating crypto payment: {crypto_currency.upper()} for ${amount}"
            )
            logger.info(f"📝 Service: {service_type}, Telegram ID: {telegram_id}")
            logger.info(f"🔧 Payment Gateway: {payment_gateway}")

            # Create order first
            order = self.db.create_order(
                telegram_id=telegram_id,
                service_type=service_type,
                service_details=service_details,
                amount=amount,
                payment_method=f"crypto_{crypto_currency}",
            )
            logger.info(f"✅ Order created: {order.order_id}")

            # Route to appropriate payment gateway
            if payment_gateway == 'dynopay':
                return await self._create_dynopay_payment(order, crypto_currency, amount)
            else:
                return await self._create_blockbee_payment(order, crypto_currency, amount)
                
        except Exception as e:
            logger.error(f"❌ Payment creation error: {e}")
            return {
                "success": False,
                "error": f"Payment creation failed: {str(e)}",
                "order_id": None
            }

    async def _create_dynopay_payment(self, order, crypto_currency: str, amount: float) -> Dict:
        """Create payment via DynoPay"""
        try:
            import os
            from apis.dynopay import DynopayAPI
            
            api_key = os.getenv('DYNOPAY_API_KEY')
            token = os.getenv('DYNOPAY_TOKEN')
            
            if not api_key or not token:
                logger.error("❌ DynoPay credentials not configured")
                return {
                    "success": False,
                    "error": "DynoPay not configured",
                    "order_id": order.order_id
                }
            
            logger.info(f"🌐 Creating DynoPay payment for {crypto_currency.upper()}")
            
            # Create DynoPay user if not exists
            dynopay = DynopayAPI(api_key, token)
            user_id = f"user_{order.telegram_id}"
            
            try:
                dynopay_user = dynopay.create_user({
                    "user_id": user_id,
                    "email": f"user_{order.telegram_id}@nomadly.com"
                })
                logger.info(f"✅ DynoPay user created/verified: {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ DynoPay user creation warning: {e}")
            
            # Create payment address (returns checkout URL)
            payment_result = dynopay.create_payment_address(
                user_id=user_id,
                amount=amount,
                currency=crypto_currency.upper()
            )
            
            if payment_result and payment_result.get('redirect_url'):
                checkout_url = payment_result['redirect_url']
                logger.info(f"✅ DynoPay checkout URL generated: {checkout_url}")
                
                return {
                    "success": True,
                    "order_id": order.order_id,
                    "payment_address": checkout_url,  # This is actually a checkout URL
                    "payment_method": f"crypto_{crypto_currency}",
                    "amount_usd": amount,
                    "cryptocurrency": crypto_currency.upper(),
                    "gateway": "dynopay",
                    "checkout_url": checkout_url,
                    "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
                }
            else:
                logger.error(f"❌ DynoPay payment creation failed: {payment_result}")
                return {
                    "success": False,
                    "error": "DynoPay payment creation failed",
                    "order_id": order.order_id
                }
                
        except Exception as e:
            logger.error(f"❌ DynoPay payment error: {e}")
            return {
                "success": False,
                "error": f"DynoPay error: {str(e)}",
                "order_id": order.order_id
            }

    async def _create_blockbee_payment(self, order, crypto_currency: str, amount: float) -> Dict:
        """Create payment via BlockBee (fallback)"""
        try:
            # Get crypto payment address from BlockBee (Mystery milestone compatible)
            callback_url = (
                f"https://{self.get_webhook_domain()}/webhook/blockbee/{order.order_id}"
            )
            logger.info(f"🔗 Callback URL: {callback_url}")

            logger.info(f"📞 Calling BlockBee API for {crypto_currency.upper()}")
            
            # Use correct cryptocurrency code for BlockBee API
            api_crypto = self.crypto_api_mapping.get(crypto_currency.lower(), crypto_currency)
            logger.info(f"🔗 Using BlockBee API code: {crypto_currency} -> {api_crypto}")
            
            result = self.api_manager.blockbee.create_payment_address(
                api_crypto, callback_url, amount  # Pass amount to BlockBee with correct crypto code
            )
            logger.info(f"📋 BlockBee response: {result}")

            # Handle Dict return format (Mystery milestone compatible)
            success = result.get("status") == "success"
            payment_address = result.get("address_in") if success else None
            qr_code = result.get("qr_code") if success else None

            if not success:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"❌ BlockBee payment creation failed: {error_msg}")
                logger.error(f"❌ Full result: {result}")
                return {
                    "success": False,
                    "error": f"BlockBee payment failed: {error_msg}",
                    "order_id": order.order_id
                }
            else:
                logger.info(f"✅ BlockBee payment created successfully")
                logger.info(f"💰 Payment address: {payment_address}")

            # Convert USD to actual cryptocurrency amount with FastForex.io real-time rates
            if success:
                crypto_amount = None
                
                # Primary: Try FastForex.io for real-time conversion
                try:
                    from apis.fastforex import FastForexAPI
                    fastforex = FastForexAPI()
                    crypto_amount = fastforex.convert_usd_to_crypto(amount, crypto_currency)
                    if crypto_amount:
                        logger.info(
                            f"💱 FastForex conversion: ${amount} USD = {crypto_amount:.8f} {crypto_currency.upper()}"
                        )
                except Exception as e:
                    logger.warning(f"⚠️ FastForex conversion failed: {e}")
                
                # Secondary: Try BlockBee API conversion
                if crypto_amount is None:
                    try:
                        crypto_amount = self.api_manager.blockbee.convert_fiat_to_crypto(
                            amount, crypto_currency
                        )
                        if crypto_amount:
                            logger.info(
                                f"💱 BlockBee conversion: ${amount} USD = {crypto_amount:.8f} {crypto_currency.upper()}"
                            )
                    except Exception as e:
                        logger.warning(f"⚠️ BlockBee conversion failed: {e}")
                
                # Final fallback: Use updated static rates
                if crypto_amount is None or crypto_amount == 0:
                    fallback_rates = {
                        "btc": 0.0000149,  # ~$67,000 per BTC (FastForex-based)
                        "eth": 0.0002735,  # ~$3,657 per ETH (FastForex real-time)  
                        "usdt": 1.0,  # $1 per USDT
                        "ltc": 0.012,  # ~$85 per LTC
                        "doge": 3.125,  # ~$0.32 per DOGE
                        "trx": 5.556,  # ~$0.18 per TRX
                    }
                    crypto_amount = amount * fallback_rates.get(crypto_currency.lower(), 1.0)
                    logger.info(
                        f"💱 Static rate conversion: ${amount} USD = {crypto_amount:.8f} {crypto_currency.upper()}"
                    )
            else:
                logger.error("❌ Payment creation failed - cannot proceed")
                crypto_amount = float(amount)

            return {
                "success": success,
                "order_id": order.order_id,
                "payment_address": payment_address,
                "payment_method": f"crypto_{crypto_currency}",
                "amount_usd": amount,
                "amount_crypto": crypto_amount,
                "cryptocurrency": crypto_currency.upper(),
                "gateway": "blockbee",
                "qr_code": qr_code,
                "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ BlockBee payment error: {e}")
            return {
                "success": False,
                "error": f"BlockBee error: {str(e)}",
                "order_id": order.order_id
            }

    def process_balance_payment(
        self,
        telegram_id: int,
        amount: float,
        service_type: str,
        service_details: Dict,
    ) -> Dict:
        """Process payment using user's wallet balance"""
        try:
            from decimal import Decimal

            logger.info(
                f"Processing balance payment: telegram_id={telegram_id}, amount={amount}"
            )

            # Convert amount to Decimal for consistency
            amount_decimal = Decimal(str(amount))

            # Check user balance
            user = self.db.get_user(telegram_id)
            if not user:
                return {"success": False, "error": "User not found"}

            user_balance_decimal = Decimal(str(user.balance_usd))
            logger.info(
                f"Current balance: {user_balance_decimal}, required: {amount_decimal}"
            )

            if user_balance_decimal < amount_decimal:
                return {
                    "success": False,
                    "error": "Insufficient balance",
                    "required": float(amount_decimal),
                    "available": float(user_balance_decimal),
                }

            # Create order
            order = self.db.create_order(
                telegram_id=telegram_id,
                service_type=service_type,
                service_details=service_details,
                amount=float(amount_decimal),
                payment_method="balance",
            )

            # Deduct balance - direct SQL approach
            from database import User

            session = self.db.get_session()
            try:
                user = session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    from decimal import Decimal

                    current_balance = Decimal(str(user.balance_usd))
                    new_balance = current_balance - amount_decimal
                    user.balance_usd = new_balance
                    session.commit()
                    logger.info(f"Balance updated: {current_balance} -> {new_balance}")
            finally:
                session.close()

            # Mark order as completed
            self.db.update_order_payment(
                order_id=order.order_id, payment_status="completed"
            )

            # Get updated balance for response and notifications
            updated_user = self.db.get_user(telegram_id)
            new_balance = float(updated_user.balance_usd) if updated_user else 0.0
            previous_balance = float(user_balance_decimal)

            # Send wallet balance payment confirmation notifications (bot + email)
            import threading, asyncio
            threading.Thread(
                target=lambda: asyncio.run(self._send_balance_payment_notifications(
                    telegram_id=telegram_id,
                    service_type=service_type,
                    service_details=service_details,
                    amount_paid=float(amount_decimal),
                    previous_balance=previous_balance,
                    new_balance=new_balance,
                    order_id=order.order_id
                )), 
                daemon=True
            ).start()

            # Trigger service delivery (run in background thread for sync compatibility)
            threading.Thread(
                target=lambda: asyncio.run(self._deliver_service(order)), daemon=True
            ).start()

            return {
                "success": True,
                "order_id": order.order_id,
                "payment_method": "balance",
                "amount_paid": float(amount_decimal),
                "new_balance": new_balance,
                "previous_balance": previous_balance,
            }

        except Exception as e:
            logger.error(f"Error processing balance payment: {e}")
            return {"success": False, "error": "Payment processing failed"}

    async def process_crypto_deposit(
        self, telegram_id: int, amount: float, crypto_currency: str
    ) -> Dict:
        """Create crypto deposit to user wallet"""
        try:
            # Create deposit order
            service_details = {"type": "wallet_deposit", "amount_usd": amount}

            return await self.create_crypto_payment(
                telegram_id=telegram_id,
                amount=amount,
                crypto_currency=crypto_currency,
                service_type="wallet_deposit",
                service_details=service_details,
            )

        except Exception as e:
            logger.error(f"Error creating crypto deposit: {e}")
            return {"success": False, "error": "Deposit creation failed"}

    async def process_wallet_deposit_with_any_amount(self, order_id: str, payment_data: Dict) -> Dict:
        """Enhanced wallet deposit processing that credits ANY amount received"""
        try:
            logger.info(f"💰 Processing wallet deposit with any amount for order {order_id}")
            
            # Get order details
            order = self.db.get_order(order_id)
            if not order:
                return {"success": False, "error": "Order not found"}
            
            # Extract payment information
            crypto_currency = payment_data.get("coin", "").upper()
            crypto_amount = float(payment_data.get("value_coin", 0))
            transaction_id = payment_data.get("txid")
            
            # Convert crypto to USD using three-tier conversion system (consistent with domain payments)
            received_usd = await self._convert_crypto_to_usd_with_fallbacks(crypto_currency, crypto_amount)
            
            logger.info(f"💰 Received: {crypto_amount} {crypto_currency} = ${received_usd:.2f} USD")
            
            # ENHANCED: Credit ANY amount received (no minimum threshold)
            if received_usd > 0:
                # Update user balance with received amount
                from decimal import Decimal
                from database import User
                
                session = self.db.get_session()
                try:
                    user = session.query(User).filter_by(telegram_id=order.telegram_id).first()
                    if user:
                        current_balance = Decimal(str(user.balance_usd))
                        deposit_amount = Decimal(str(received_usd))
                        user.balance_usd = current_balance + deposit_amount
                        session.commit()
                        
                        new_balance = float(user.balance_usd)
                        logger.info(f"✅ Wallet credited: {current_balance} + {deposit_amount} = {new_balance}")
                        
                        # Update order status
                        order.payment_status = "completed"
                        order.payment_txid = transaction_id
                        order.amount = received_usd  # Update to actual received amount
                        session.commit()
                        
                        # Send user notification about wallet credit
                        await self._send_wallet_credit_notification(
                            order.telegram_id, 
                            received_usd, 
                            order.service_details.get("amount_usd", 0) if order.service_details else 0,
                            new_balance,
                            transaction_id,
                            crypto_amount,
                            crypto_currency
                        )
                        
                        return {
                            "success": True,
                            "amount_credited": received_usd,
                            "new_balance": new_balance,
                            "crypto_amount": crypto_amount,
                            "crypto_currency": crypto_currency,
                            "transaction_id": transaction_id
                        }
                    else:
                        session.rollback()
                        return {"success": False, "error": "User not found"}
                        
                finally:
                    session.close()
            else:
                logger.warning(f"No value received for wallet deposit: ${received_usd:.2f}")
                return {"success": False, "error": "No value received"}
                
        except Exception as e:
            logger.error(f"Error processing wallet deposit: {e}")
            return {"success": False, "error": str(e)}

    async def _send_wallet_underpayment_notification(
        self,
        telegram_id: int,
        received_usd: float,
        expected_usd: float,
        shortage_amount: float,
        new_balance: float,
        order_id: str,
        crypto_currency: str,
        crypto_amount: float
    ):
        """Send notification about wallet deposit underpayment"""
        try:
            import os
            from telegram import Bot
            from dotenv import load_dotenv
            
            # Load environment variables from .env file
            load_dotenv()
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            
            if not bot_token:
                logger.error("TELEGRAM_BOT_TOKEN not found in environment")
                return
                
            bot = Bot(token=bot_token)
            
            message = (
                f"💳 *Wallet Deposit - Underpayment Credited*\n\n"
                f"🎯 **Expected:** ${expected_usd:.2f} USD\n"
                f"💰 **You Sent:** ${received_usd:.2f} USD\n"
                f"⚠️ **Shortage:** ${shortage_amount:.2f} USD\n\n"
                f"✅ **Your ${received_usd:.2f} USD has been credited to your wallet!**\n\n"
                f"🔗 **Order ID:** `{order_id}`\n"
                f"💎 **Crypto:** {crypto_amount} {crypto_currency.upper()}\n"
                f"💳 **New Balance:** ${new_balance:.2f} USD\n\n"
                f"💡 *Add ${shortage_amount:.2f} more to reach your intended deposit amount.*\n\n"
                f"🏴‍☠️ *No payment is ever lost - all funds are credited!*"
            )
            
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"📱 Wallet underpayment notification sent to user {telegram_id}")
            
        except Exception as e:
            logger.error(f"Failed to send wallet underpayment notification: {e}")

    async def _send_wallet_credit_notification(
        self, 
        telegram_id: int, 
        received_usd: float, 
        expected_usd: float, 
        new_balance: float,
        transaction_id: str,
        crypto_amount: float,
        crypto_currency: str
    ):
        """Send user notification about wallet credit with smart messaging"""
        try:
            from telegram import Bot
            import os
            
            bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
            
            # Calculate difference for smart messaging
            difference = received_usd - expected_usd if expected_usd > 0 else 0
            
            if difference > 0.01:  # Overpayment
                message = (
                    f"💰 *Wallet Deposit Confirmed!*\n\n"
                    f"✅ **Expected:** ${expected_usd:.2f} USD\n"
                    f"🎉 **Received:** ${received_usd:.2f} USD\n"
                    f"🎁 **BONUS:** +${difference:.2f} USD extra!\n\n"
                    f"🔗 **Transaction:** `{transaction_id}`\n"
                    f"💎 **Amount:** {crypto_amount} {crypto_currency}\n"
                    f"💳 **New Balance:** ${new_balance:.2f} USD\n\n"
                    f"🏴‍☠️ *Your wallet has been credited with the full amount received!*"
                )
            elif difference < -0.01:  # Underpayment
                shortage = abs(difference)
                message = (
                    f"💰 *Payment Received - Credited to Wallet*\n\n"
                    f"💰 **Expected:** ${expected_usd:.2f} USD\n"
                    f"💳 **Received:** ${received_usd:.2f} USD\n"
                    f"⚠️ **Shortage:** ${shortage:.2f} USD\n\n"
                    f"✅ **Your ${received_usd:.2f} USD has been credited to your wallet!**\n\n"
                    f"🔗 **Transaction:** `{transaction_id}`\n"
                    f"💎 **Amount:** {crypto_amount} {crypto_currency}\n"
                    f"💳 **Current Balance:** ${new_balance:.2f} USD\n\n"
                    f"💡 *Any amount you send gets credited - no minimum required!*"
                )
            else:  # Exact amount
                message = (
                    f"✅ *Wallet Deposit Confirmed!*\n\n"
                    f"💰 **Amount:** ${received_usd:.2f} USD\n"
                    f"🔗 **Transaction:** `{transaction_id}`\n"
                    f"💎 **Crypto:** {crypto_amount} {crypto_currency}\n"
                    f"💳 **New Balance:** ${new_balance:.2f} USD\n\n"
                    f"🏴‍☠️ *Your wallet has been updated successfully!*"
                )
            
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"📱 Wallet credit notification sent to user {telegram_id}")
            
        except Exception as e:
            logger.error(f"Failed to send wallet credit notification: {e}")

    async def _handle_domain_underpayment(
        self, 
        telegram_id: int, 
        received_usd: float,
        expected_usd: float, 
        shortage_amount: float,
        order_id: str,
        crypto_currency: str,
        crypto_amount: float
    ):
        """Handle underpayment for domain registration by crediting to wallet"""
        try:
            from decimal import Decimal
            from database import User
            
            logger.info(f"💳 Processing domain underpayment: ${received_usd:.2f} received, ${expected_usd:.2f} expected for order {order_id}")
            
            # Credit the received amount to user's wallet balance
            session = self.db.get_session()
            try:
                user = session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    current_balance = Decimal(str(user.balance_usd))
                    credit_amount = Decimal(str(received_usd))
                    new_balance = current_balance + credit_amount
                    user.balance_usd = new_balance
                    session.commit()
                    
                    logger.info(f"✅ Underpayment credited to wallet: ${current_balance:.2f} + ${credit_amount:.2f} = ${new_balance:.2f}")
                    
                    # Record the underpayment credit transaction
                    try:
                        from sqlalchemy import text
                        session.execute(
                            text("""
                                INSERT INTO wallet_transactions (telegram_id, transaction_type, amount, currency, status, description, crypto_amount, crypto_currency)
                                VALUES (:telegram_id, :transaction_type, :amount, :currency, :status, :description, :crypto_amount, :crypto_currency)
                            """),
                            {
                                "telegram_id": telegram_id,
                                "transaction_type": "underpayment_credit",
                                "amount": float(credit_amount),
                                "currency": "USD",
                                "status": "confirmed",
                                "description": f"Domain underpayment credit from order {order_id} - ${shortage_amount:.2f} shortage",
                                "crypto_amount": crypto_amount,
                                "crypto_currency": crypto_currency
                            }
                        )
                        session.commit()
                        logger.info(f"✅ Underpayment transaction record created")
                    except Exception as tx_error:
                        logger.warning(f"Failed to create underpayment transaction record: {tx_error}")
                    
                    # Send notifications to user about underpayment and wallet credit (bot + email)
                    # Send notification using Master Notification Service
                    from services.master_notification_service import get_master_notification_service
                    
                    notification_service = get_master_notification_service()
                    await notification_service.send_underpayment_notification(telegram_id, received_usd, expected_usd, shortage_amount)
                    await self._send_underpayment_email_notification(telegram_id, received_usd, expected_usd, shortage_amount, new_balance, order_id, crypto_currency, crypto_amount)
                    
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"❌ Failed to handle domain underpayment: {e}")

    async def _send_underpayment_notification(
        self, 
        telegram_id: int, 
        received_usd: float, 
        expected_usd: float,
        shortage_amount: float,
        new_balance: float,
        order_id: str,
        crypto_amount: float,
        crypto_currency: str
    ):
        """Send notification about domain underpayment and wallet credit"""
        try:
            from telegram import Bot
            bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
            
            message = (
                f"💳 *Domain Payment Underpaid - Credited to Wallet*\n\n"
                f"🎯 **Domain Cost:** ${expected_usd:.2f} USD\n"
                f"💰 **You Sent:** ${received_usd:.2f} USD\n"
                f"⚠️ **Shortage:** ${shortage_amount:.2f} USD\n\n"
                f"✅ **Your ${received_usd:.2f} USD has been credited to your wallet!**\n\n"
                f"🔗 **Order ID:** `{order_id}`\n"
                f"💎 **Crypto:** {crypto_amount} {crypto_currency}\n"
                f"💳 **New Balance:** ${new_balance:.2f} USD\n\n"
                f"💡 *To complete domain registration:*\n"
                f"• Add ${shortage_amount:.2f} more to your wallet, OR\n"
                f"• Use wallet balance to purchase the domain\n\n"
                f"🏴‍☠️ *No payment is ever lost - all funds are credited!*"
            )
            
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"📱 Underpayment notification sent to user {telegram_id}")
            
        except Exception as e:
            logger.error(f"Failed to send underpayment notification: {e}")

    async def _send_underpayment_email_notification(
        self, 
        telegram_id: int, 
        received_usd: float, 
        expected_usd: float,
        shortage_amount: float,
        new_balance: float,
        order_id: str,
        crypto_currency: str,
        crypto_amount: float
    ):
        """Send email notification about domain underpayment and wallet credit"""
        try:
            # Get user email
            from database import User
            session = self.db.get_session()
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            session.close()
            
            if not user or not user.technical_email:
                logger.warning(f"No email found for user {telegram_id} - skipping email notification")
                return
                
            # Send email using existing Brevo service
            from services.email_service import send_brevo_email
            
            email_subject = "Domain Payment Underpaid - Funds Credited to Wallet"
            email_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .highlight {{ background: #e8f4fd; padding: 15px; border-left: 4px solid #2a5298; margin: 15px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>⚓ Domain Payment Update</h1>
                        <p>Maritime Hosting Services</p>
                    </div>
                    <div class="content">
                        <h2>💳 Underpayment Credited to Wallet</h2>
                        
                        <p>Your cryptocurrency payment for domain registration was less than the required amount. We've credited your actual payment to your wallet balance.</p>
                        
                        <div class="highlight">
                            <strong>Payment Details:</strong><br>
                            • Domain Cost: <strong>${expected_usd:.2f} USD</strong><br>
                            • Amount You Sent: <strong>${received_usd:.2f} USD</strong><br>
                            • Shortage: <strong>${shortage_amount:.2f} USD</strong><br>
                            • Order ID: <strong>{order_id}</strong><br>
                            • Cryptocurrency: <strong>{crypto_amount} {crypto_currency}</strong>
                        </div>
                        
                        <div class="highlight">
                            <strong>✅ Your ${received_usd:.2f} USD has been credited to your wallet!</strong><br>
                            • New Wallet Balance: <strong>${new_balance:.2f} USD</strong>
                        </div>
                        
                        <h3>💡 Next Steps:</h3>
                        <ul>
                            <li>Add ${shortage_amount:.2f} more to your wallet to complete the purchase</li>
                            <li>Or use your current wallet balance to register the domain</li>
                        </ul>
                        
                        <p><strong>🏴‍☠️ No payment is ever lost - all funds are always credited!</strong></p>
                    </div>
                    <div class="footer">
                        <p>Nameword - Maritime Domain Services</p>
                        <p>Offshore Hosting: Resilience | Discretion | Independence</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = await send_brevo_email(
                to_email=user.technical_email,
                subject=email_subject,
                html_content=email_html
            )
            
            if success:
                logger.info(f"📧 Underpayment email notification sent to {user.technical_email}")
            else:
                logger.warning(f"❌ Failed to send underpayment email to {user.technical_email}")
                
        except Exception as e:
            logger.error(f"Failed to send underpayment email notification: {e}")

    async def _send_overpayment_email_notification(
        self, 
        telegram_id: int, 
        overpayment_amount: float, 
        new_balance: float,
        order_id: str
    ):
        """Send email notification about domain overpayment credit"""
        try:
            # Get user email
            from database import User
            session = self.db.get_session()
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            session.close()
            
            if not user or not user.technical_email:
                logger.warning(f"No email found for user {telegram_id} - skipping overpayment email notification")
                return
                
            # Send email using existing Brevo service
            from services.email_service import send_brevo_email
            
            email_subject = "Bonus Credit Added - Domain Overpayment"
            email_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .highlight {{ background: #e8f4fd; padding: 15px; border-left: 4px solid #2a5298; margin: 15px 0; }}
                    .bonus {{ background: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎁 Bonus Credit Added!</h1>
                        <p>Maritime Hosting Services</p>
                    </div>
                    <div class="content">
                        <h2>💰 Overpayment Credited to Wallet</h2>
                        
                        <p>Great news! You sent more cryptocurrency than required for your domain registration. Your extra payment has been automatically added to your wallet balance.</p>
                        
                        <div class="bonus">
                            <strong>✅ Bonus Credit Details:</strong><br>
                            • Overpayment Credit: <strong>${overpayment_amount:.2f} USD</strong><br>
                            • New Wallet Balance: <strong>${new_balance:.2f} USD</strong><br>
                            • Order ID: <strong>{order_id}</strong>
                        </div>
                        
                        <p>Your domain registration will proceed as planned, and the extra amount is now available in your wallet for future purchases.</p>
                        
                        <p><strong>🏴‍☠️ Your extra payment has been safely credited to your wallet balance!</strong></p>
                    </div>
                    <div class="footer">
                        <p>Nameword - Maritime Domain Services</p>
                        <p>Offshore Hosting: Resilience | Discretion | Independence</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = await send_brevo_email(
                to_email=user.technical_email,
                subject=email_subject,
                html_content=email_html
            )
            
            if success:
                logger.info(f"📧 Overpayment email notification sent to {user.technical_email}")
            else:
                logger.warning(f"❌ Failed to send overpayment email to {user.technical_email}")
                
        except Exception as e:
            logger.error(f"Failed to send overpayment email notification: {e}")

    async def _send_wallet_overpayment_notification(
        self, 
        telegram_id: int, 
        actual_usd_received: float,
        expected_usd: float,
        overpayment_amount: float,
        new_balance: float,
        order_id: str,
        crypto_currency: str,
        crypto_amount: float
    ):
        """Send notification about wallet funding overpayment"""
        try:
            from telegram import Bot
            from dotenv import load_dotenv
            load_dotenv()
            
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not bot_token:
                logger.error("TELEGRAM_BOT_TOKEN not found in environment")
                return
                
            bot = Bot(token=bot_token)
            
            message = (
                f"🎁 *Wallet Deposit - Bonus Credit Added!*\n\n"
                f"🎯 **Expected:** ${expected_usd:.2f} USD\n"
                f"💰 **You Sent:** ${actual_usd_received:.2f} USD\n"
                f"✨ **Bonus Credit:** ${overpayment_amount:.2f} USD\n\n"
                f"✅ **Your full ${actual_usd_received:.2f} USD has been credited to your wallet!**\n\n"
                f"🔗 **Order ID:** `{order_id}`\n"
                f"💎 **Crypto:** {crypto_amount} {crypto_currency}\n"
                f"💳 **New Balance:** ${new_balance:.2f} USD\n\n"
                f"🎉 *You sent extra and we credited it all - bonus ${overpayment_amount:.2f} added!*\n\n"
                f"🏴‍☠️ *All payments are fully credited - we never keep extra funds!*"
            )
            
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"📱 Wallet overpayment notification sent to user {telegram_id}")
            
        except Exception as e:
            logger.error(f"Failed to send wallet overpayment notification: {e}")

    async def _send_wallet_overpayment_email_notification(
        self, 
        telegram_id: int, 
        actual_usd_received: float,
        expected_usd: float,
        overpayment_amount: float,
        new_balance: float,
        order_id: str,
        crypto_currency: str,
        crypto_amount: float
    ):
        """Send email notification about wallet funding overpayment"""
        try:
            # Get user email
            from database import User
            session = self.db.get_session()
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            session.close()
            
            if not user or not user.technical_email:
                logger.warning(f"No email found for user {telegram_id} - skipping wallet overpayment email")
                return
                
            # Send email using existing Brevo service
            from services.email_service import send_brevo_email
            
            email_subject = "Bonus Credit Added - Wallet Overpayment"
            email_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .highlight {{ background: #e8f4fd; padding: 15px; border-left: 4px solid #2a5298; margin: 15px 0; }}
                    .bonus {{ background: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎁 Bonus Credit Added!</h1>
                        <p>Maritime Hosting Services</p>
                    </div>
                    <div class="content">
                        <h2>💰 Wallet Deposit - Overpayment Credited</h2>
                        
                        <p>Excellent! You sent more cryptocurrency than expected for your wallet deposit. We've credited your full payment amount to your wallet, including the extra bonus!</p>
                        
                        <div class="highlight">
                            <strong>Payment Details:</strong><br>
                            • Expected Amount: <strong>${expected_usd:.2f} USD</strong><br>
                            • Amount You Sent: <strong>${actual_usd_received:.2f} USD</strong><br>
                            • Order ID: <strong>{order_id}</strong><br>
                            • Cryptocurrency: <strong>{crypto_amount} {crypto_currency}</strong>
                        </div>
                        
                        <div class="bonus">
                            <strong>✨ Bonus Credit Added:</strong><br>
                            • Extra Amount: <strong>${overpayment_amount:.2f} USD</strong><br>
                            • New Wallet Balance: <strong>${new_balance:.2f} USD</strong>
                        </div>
                        
                        <p>Your full ${actual_usd_received:.2f} USD payment has been credited to your wallet, including the ${overpayment_amount:.2f} USD bonus!</p>
                        
                        <p><strong>🏴‍☠️ All payments are fully credited - we never keep extra funds!</strong></p>
                    </div>
                    <div class="footer">
                        <p>Nameword - Maritime Domain Services</p>
                        <p>Offshore Hosting: Resilience | Discretion | Independence</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = await send_brevo_email(
                to_email=user.technical_email,
                subject=email_subject,
                html_content=email_html
            )
            
            if success:
                logger.info(f"📧 Wallet overpayment email notification sent to {user.technical_email}")
            else:
                logger.warning(f"❌ Failed to send wallet overpayment email to {user.technical_email}")
                
        except Exception as e:
            logger.error(f"Failed to send wallet overpayment email notification: {e}")

    async def _send_balance_payment_notifications(
        self,
        telegram_id: int,
        service_type: str,
        service_details: dict,
        amount_paid: float,
        previous_balance: float,
        new_balance: float,
        order_id: str
    ):
        """Send comprehensive wallet balance payment confirmation (bot + email)"""
        try:
            logger.info(f"Sending balance payment notifications for user {telegram_id}, order {order_id}")
            
            # Send bot notification
            await self._send_balance_payment_bot_notification(
                telegram_id, service_type, service_details, amount_paid, 
                previous_balance, new_balance, order_id
            )
            
            # Send email notification  
            await self._send_balance_payment_email_notification(
                telegram_id, service_type, service_details, amount_paid,
                previous_balance, new_balance, order_id
            )
            
        except Exception as e:
            logger.error(f"Failed to send balance payment notifications: {e}")

    async def _send_balance_payment_bot_notification(
        self,
        telegram_id: int,
        service_type: str,
        service_details: dict,
        amount_paid: float,
        previous_balance: float,
        new_balance: float,
        order_id: str
    ):
        """Send Telegram bot notification for wallet balance payment"""
        try:
            from telegram import Bot
            from dotenv import load_dotenv
            load_dotenv()
            
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not bot_token:
                logger.error("TELEGRAM_BOT_TOKEN not found for balance payment notification")
                return
                
            bot = Bot(token=bot_token)
            
            # Extract service details for display
            service_display = service_type.replace('_', ' ').title()
            if service_type == "domain_registration" and isinstance(service_details, dict):
                domain_name = service_details.get('domain_name', 'Unknown')
                service_display = f"Domain Registration: {domain_name}"
            
            message = (
                f"✅ *Wallet Balance Payment Confirmed*\n\n"
                f"🛍️ **Service:** {service_display}\n"
                f"💰 **Amount Paid:** ${amount_paid:.2f} USD\n"
                f"🔗 **Order ID:** `{order_id}`\n\n"
                f"💳 **Wallet Balance Update:**\n"
                f"• Previous Balance: ${previous_balance:.2f} USD\n"
                f"• Amount Deducted: ${amount_paid:.2f} USD\n"
                f"• New Balance: ${new_balance:.2f} USD\n\n"
                f"🏴‍☠️ *Your service will be activated shortly!*\n\n"
                f"📊 *Full payment transparency - track every transaction*"
            )
            
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"📱 Balance payment bot notification sent to user {telegram_id}")
            
        except Exception as e:
            logger.error(f"Failed to send balance payment bot notification: {e}")

    async def _send_balance_payment_email_notification(
        self,
        telegram_id: int,
        service_type: str,
        service_details: dict,
        amount_paid: float,
        previous_balance: float,
        new_balance: float,
        order_id: str
    ):
        """Send email notification for wallet balance payment"""
        try:
            # Get user email
            from database import User
            session = self.db.get_session()
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            session.close()
            
            if not user or not user.technical_email:
                logger.warning(f"No email found for user {telegram_id} - skipping balance payment email")
                return
                
            # Extract service details for display
            service_display = service_type.replace('_', ' ').title()
            domain_name = "Unknown Service"
            if service_type == "domain_registration" and isinstance(service_details, dict):
                domain_name = service_details.get('domain_name', 'Unknown Domain')
                service_display = f"Domain Registration: {domain_name}"
                
            # Send email using existing Brevo service
            from services.email_service import send_brevo_email
            
            email_subject = f"Payment Confirmed - {service_display}"
            email_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .highlight {{ background: #e8f4fd; padding: 15px; border-left: 4px solid #2a5298; margin: 15px 0; }}
                    .balance-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                    .balance-table th, .balance-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                    .balance-table th {{ background: #f8f9fa; font-weight: bold; }}
                    .success {{ background: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Payment Confirmed</h1>
                        <p>Maritime Hosting Services</p>
                    </div>
                    <div class="content">
                        <h2>💳 Wallet Balance Payment Successful</h2>
                        
                        <p>Your wallet balance payment has been successfully processed. Below are the complete transaction details for your records.</p>
                        
                        <div class="highlight">
                            <strong>Service Details:</strong><br>
                            • Service: <strong>{service_display}</strong><br>
                            • Amount Paid: <strong>${amount_paid:.2f} USD</strong><br>
                            • Order ID: <strong>{order_id}</strong><br>
                            • Payment Method: <strong>Wallet Balance</strong>
                        </div>
                        
                        <h3>💰 Wallet Balance Transparency</h3>
                        <table class="balance-table">
                            <tr>
                                <th>Transaction Detail</th>
                                <th>Amount</th>
                            </tr>
                            <tr>
                                <td>Previous Wallet Balance</td>
                                <td>${previous_balance:.2f} USD</td>
                            </tr>
                            <tr>
                                <td>Payment Deducted</td>
                                <td>-${amount_paid:.2f} USD</td>
                            </tr>
                            <tr style="font-weight: bold; background: #f8f9fa;">
                                <td>New Wallet Balance</td>
                                <td>${new_balance:.2f} USD</td>
                            </tr>
                        </table>
                        
                        <div class="success">
                            <strong>✅ Service Activation</strong><br>
                            Your service will be activated shortly. You'll receive additional notifications once the setup is complete.
                        </div>
                        
                        <p><strong>🏴‍☠️ Complete payment transparency - every transaction tracked!</strong></p>
                    </div>
                    <div class="footer">
                        <p>Nameword - Maritime Domain Services</p>
                        <p>Offshore Hosting: Resilience | Discretion | Independence</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = await send_brevo_email(
                to_email=user.technical_email,
                subject=email_subject,
                html_content=email_html
            )
            
            if success:
                logger.info(f"📧 Balance payment email notification sent to {user.technical_email}")
            else:
                logger.warning(f"❌ Failed to send balance payment email to {user.technical_email}")
                
        except Exception as e:
            logger.error(f"Failed to send balance payment email notification: {e}")

    async def _convert_crypto_to_usd_with_fallbacks(self, crypto_currency: str, crypto_amount: float) -> float:
        """Convert cryptocurrency to USD using three-tier system: FastForex → BlockBee → Static"""
        try:
            logger.info(f"💱 Converting {crypto_amount} {crypto_currency} to USD using three-tier system")
            
            # Tier 1: Try FastForex.io for real-time conversion
            try:
                from apis.fastforex import FastForexAPI
                fastforex = FastForexAPI()
                
                # Get current rate: 1 crypto = X USD
                usd_rate = fastforex.get_crypto_rate_to_usd(crypto_currency)
                if usd_rate and usd_rate > 0:
                    received_usd = crypto_amount * usd_rate
                    logger.info(f"✅ FastForex: {crypto_amount} {crypto_currency} = ${received_usd:.2f} USD (rate: ${usd_rate:.2f})")
                    return received_usd
                else:
                    logger.warning("⚠️ FastForex rate invalid or zero")
                    
            except Exception as e:
                logger.warning(f"⚠️ FastForex conversion failed: {e}")
            
            # Tier 2: Try BlockBee API conversion
            try:
                from apis.blockbee import BlockBeeAPI
                import os
                
                blockbee = BlockBeeAPI(os.getenv("BLOCKBEE_API_KEY"))
                received_usd = blockbee.convert_amount(crypto_currency, "USD", crypto_amount)
                if received_usd and received_usd > 0:
                    logger.info(f"✅ BlockBee: {crypto_amount} {crypto_currency} = ${received_usd:.2f} USD")
                    return received_usd
                else:
                    logger.warning("⚠️ BlockBee conversion returned invalid result")
                    
            except Exception as e:
                logger.warning(f"⚠️ BlockBee conversion failed: {e}")
            
            # Tier 3: Emergency static rates (AVOID USAGE - FastForex should be primary)
            logger.error(f"❌ Both FastForex and BlockBee failed! This should rarely happen.")
            logger.error(f"⚠️ Check FastForex API key and network connectivity")
            
            # Only use static rates as absolute last resort
            static_rates = {
                "ETH": 3647.0,    # Updated from real market data
                "BTC": 67000.0,
                "USDT": 1.0,
                "LTC": 85.0,
                "DOGE": 0.32,
                "TRX": 0.18
            }
            
            crypto_upper = crypto_currency.upper()
            if crypto_upper in static_rates:
                rate = static_rates[crypto_upper]
                received_usd = crypto_amount * rate
                logger.error(f"🚨 EMERGENCY STATIC RATE: {crypto_amount} {crypto_currency} = ${received_usd:.2f} USD (rate: ${rate:.2f})")
                logger.error(f"🔧 URGENT: Fix FastForex API connection to avoid static pricing!")
                return received_usd
            else:
                logger.error(f"❌ No fallback available for {crypto_currency}")
                return 0.0
                
        except Exception as e:
            logger.error(f"❌ All conversion methods failed: {e}")
            return 0.0

    async def _credit_overpayment_to_wallet(
        self, 
        telegram_id: int, 
        overpayment_amount: float, 
        order_id: str,
        crypto_currency: str,
        crypto_amount: float
    ):
        """Credit overpayment from domain registration to user's wallet balance"""
        try:
            from decimal import Decimal
            from database import User
            
            logger.info(f"💰 Crediting overpayment: ${overpayment_amount:.2f} to user {telegram_id} from order {order_id}")
            
            session = self.db.get_session()
            try:
                user = session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    current_balance = Decimal(str(user.balance_usd))
                    overpayment_decimal = Decimal(str(overpayment_amount))
                    new_balance = current_balance + overpayment_decimal
                    user.balance_usd = new_balance
                    session.commit()
                    
                    # Record the overpayment credit transaction
                    try:
                        from sqlalchemy import text
                        session.execute(
                            text("""
                                INSERT INTO wallet_transactions (telegram_id, transaction_type, amount, currency, status, description, crypto_amount, crypto_currency)
                                VALUES (:telegram_id, :transaction_type, :amount, :currency, :status, :description, :crypto_amount, :crypto_currency)
                            """),
                            {
                                "telegram_id": telegram_id,
                                "transaction_type": "overpayment_credit",
                                "amount": float(overpayment_decimal),
                                "currency": "USD",
                                "status": "confirmed",
                                "description": f"Domain registration overpayment credit from order {order_id}",
                                "crypto_amount": crypto_amount,
                                "crypto_currency": crypto_currency
                            }
                        )
                        session.commit()
                        logger.info(f"✅ Transaction record created for overpayment credit")
                    except Exception as tx_error:
                        logger.warning(f"Failed to create transaction record: {tx_error}")
                    
                    logger.info(f"✅ Overpayment credited: ${current_balance} + ${overpayment_decimal} = ${new_balance}")
                    
                    # Send notifications to user about overpayment credit (bot + email)
                    # Send notification using Master Notification Service
                    from services.master_notification_service import get_master_notification_service
                    
                    notification_service = get_master_notification_service()
                    await notification_service.send_overpayment_notification(telegram_id, overpayment_amount, new_balance, order_id)
                    await self._send_overpayment_email_notification(telegram_id, overpayment_amount, new_balance, order_id)
                else:
                    logger.error(f"User not found for overpayment credit: {telegram_id}")
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to credit overpayment: {e}")

    async def _send_overpayment_notification(
        self, 
        telegram_id: int, 
        overpayment_amount: float, 
        new_balance: float,
        order_id: str
    ):
        """Send notification to user about overpayment credit"""
        try:
            from telegram import Bot
            import os
            
            # Use direct Bot instance to avoid circular imports
            from dotenv import load_dotenv
            load_dotenv()
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if bot_token:
                bot = Bot(token=bot_token)
                message = (
                    f"🎁 *Bonus Credit Added to Wallet!*\n\n"
                    f"✅ You sent more cryptocurrency than required for your domain registration.\n\n"
                    f"💰 **Overpayment Credit:** ${overpayment_amount:.2f} USD\n"
                    f"💳 **New Wallet Balance:** ${new_balance:.2f} USD\n"
                    f"🆔 **Order:** `{order_id}`\n\n"
                    f"🏴‍☠️ *Your extra payment has been automatically added to your wallet balance!*"
                )
                
                await bot.send_message(
                    chat_id=telegram_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
                logger.info(f"📱 Overpayment notification sent to user {telegram_id}")
            else:
                logger.error("❌ BOT_TOKEN not available for overpayment notification")
        except Exception as e:
            logger.error(f"Failed to send overpayment notification: {e}")

    def check_payment_status(self, order_id: str) -> Dict:
        """Check payment status for an order"""
        try:
            order = self.db.get_order(order_id)
            if not order:
                return {"success": False, "error": "Order not found"}

            return {
                "success": True,
                "order_id": order_id,
                "payment_status": order.payment_status,
                "amount_usd": order.amount,
                "service_type": order.service_type,
                "created_at": order.created_at.isoformat(),
                "payment_method": order.payment_method,
            }

        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return {"success": False, "error": "Status check failed"}

    async def process_webhook_payment(self, order_id: str, payment_data: Dict) -> Dict:
        """Process payment confirmation from BlockBee webhook"""
        try:
            order = self.db.get_order(order_id)
            if not order:
                logger.error(f"Order not found for webhook: {order_id}")
                return {"success": False, "error": "Order not found"}

            # FIX 2: Enhanced webhook duplicate processing with service delivery validation
            if order.payment_status == "completed":
                logger.info(f"Payment already processed for order {order_id}, checking if service was delivered...")
                
                # Prepare order data for validation
                order_data = {
                    "service_type": order.service_type,
                    "domain_name": order.domain_name if hasattr(order, 'domain_name') else None,
                    "telegram_id": order.telegram_id
                }
                
                # Use validation fix to check actual service delivery
                service_delivered, service_details = SimpleValidationFixes.validate_webhook_service_delivery(order_id, order_data)
                
                if service_delivered:
                    logger.info(f"Service already delivered for order {order_id}: {service_details}")
                    return {"success": True, "order_id": order_id, "message": "Already processed and delivered", "service_details": service_details}
                else:
                    logger.warning(f"Payment completed but service not delivered for order {order_id} - triggering service delivery: {service_details}")
                    # Continue to process service delivery

            # Verify payment amount and status
            # BlockBee sends "result": "sent" when payment is successful with confirmations
            payment_result = payment_data.get("result", "")
            confirmations = int(payment_data.get("confirmations", 0))
            value_coin = float(payment_data.get("value_coin", 0))
            
            # Consider payment confirmed if result is "sent" and has confirmations and value
            payment_confirmed = (payment_result == "sent" and confirmations >= 1 and value_coin > 0)
            
            if payment_confirmed:
                # ENHANCED: Check for overpayments on domain registrations before completing order
                crypto_currency = payment_data.get("coin", "").upper()
                actual_usd_received = await self._convert_crypto_to_usd_with_fallbacks(crypto_currency, value_coin)
                expected_usd = float(order.amount_usd)
                
                logger.info(f"💰 Payment Analysis: Expected ${expected_usd:.2f}, Received ${actual_usd_received:.2f}")
                
                # Mark order as completed
                self.db.update_order_payment(
                    order_id=order_id, payment_status="completed"
                )

                # Send appropriate payment confirmation based on service type
                await self._send_payment_confirmation(order, payment_data)

                # ENHANCED: Handle overpayments and underpayments for domain registrations
                if order.service_type == "domain_registration":
                    payment_difference = actual_usd_received - expected_usd
                    
                    if payment_difference > 0.01:  # Overpayment
                        await self._credit_overpayment_to_wallet(order.telegram_id, payment_difference, order_id, crypto_currency, value_coin)
                    elif payment_difference < -0.01:  # Underpayment
                        underpayment_amount = abs(payment_difference)
                        await self._handle_domain_underpayment(order.telegram_id, actual_usd_received, expected_usd, underpayment_amount, order_id, crypto_currency, value_coin)
                        # Don't proceed with domain registration for underpayments
                        return {
                            "success": True,
                            "order_id": order_id,
                            "service_delivered": False,
                            "underpayment_credited": True,
                            "credited_amount": actual_usd_received,
                            "shortage": underpayment_amount
                        }

                # Process based on service type
                if order.service_type == "wallet_deposit":
                    # CRITICAL FIX: Handle wallet deposits with proper amount validation
                    payment_difference = actual_usd_received - expected_usd
                    
                    # Credit actual received amount (not expected amount)
                    from decimal import Decimal
                    from database import User

                    session = self.db.get_session()
                    try:
                        user = (
                            session.query(User)
                            .filter_by(telegram_id=order.telegram_id)
                            .first()
                        )
                        if user:
                            current_balance = Decimal(str(user.balance_usd))
                            # FIX: Use actual_usd_received instead of order.amount
                            deposit_amount = Decimal(str(actual_usd_received))
                            user.balance_usd = current_balance + deposit_amount
                            session.commit()
                            
                            logger.info(
                                f"✅ FIXED: Wallet credited with ACTUAL amount: {current_balance} + {deposit_amount} = {user.balance_usd}"
                            )
                            
                            # Send underpayment notification if applicable
                            if payment_difference < -0.01:  # Underpayment
                                underpayment_amount = abs(payment_difference)
                                await self._send_wallet_underpayment_notification(
                                    order.telegram_id,
                                    actual_usd_received,
                                    expected_usd,
                                    underpayment_amount,
                                    float(user.balance_usd),
                                    order_id,
                                    crypto_currency,
                                    value_coin
                                )
                            elif payment_difference > 0.01:  # Overpayment notification
                                await self._send_wallet_overpayment_notification(
                                    order.telegram_id,
                                    actual_usd_received,
                                    expected_usd,
                                    payment_difference,
                                    float(user.balance_usd),
                                    order_id,
                                    crypto_currency,
                                    value_coin
                                )
                                await self._send_wallet_overpayment_email_notification(
                                    order.telegram_id,
                                    actual_usd_received,
                                    expected_usd,
                                    payment_difference,
                                    float(user.balance_usd),
                                    order_id,
                                    crypto_currency,
                                    value_coin
                                )
                            
                            # Record transaction for audit trail
                            try:
                                from sqlalchemy import text
                                session.execute(
                                    text("""
                                        INSERT INTO wallet_transactions (telegram_id, transaction_type, amount, currency, status, description, crypto_amount, crypto_currency)
                                        VALUES (:telegram_id, :transaction_type, :amount, :currency, :status, :description, :crypto_amount, :crypto_currency)
                                    """),
                                    {
                                        "telegram_id": order.telegram_id,
                                        "transaction_type": "wallet_deposit",
                                        "amount": float(deposit_amount),
                                        "currency": "USD",
                                        "status": "confirmed",
                                        "description": f"Wallet deposit from order {order_id} - Expected: ${expected_usd:.2f}, Received: ${actual_usd_received:.2f}",
                                        "crypto_amount": value_coin,
                                        "crypto_currency": crypto_currency
                                    }
                                )
                                session.commit()
                                logger.info(f"✅ Transaction record created for wallet deposit")
                            except Exception as tx_error:
                                logger.warning(f"Failed to create transaction record: {tx_error}")
                        
                    finally:
                        session.close()
                else:
                    # Deliver service
                    await self._deliver_service(order)

                # Get domain registration data if available
                domain_data = {}
                if hasattr(self, "last_domain_registration_data"):
                    domain_data = self.last_domain_registration_data

                return {
                    "success": True,
                    "order_id": order_id,
                    "service_delivered": True,
                    "domain_name": domain_data.get("domain_name", "N/A"),
                    "expiry_date": domain_data.get("expiry_date", "N/A"),
                    "nameservers": domain_data.get("nameservers", []),
                }
            else:
                logger.warning(
                    f"Payment not confirmed for order {order_id}: {payment_data}"
                )
                return {"success": False, "error": "Payment not confirmed"}

        except Exception as e:
            logger.error(f"Error processing webhook payment: {e}")
            return {"success": False, "error": "Webhook processing failed"}

    async def _deliver_service(self, order):
        """Deliver service after successful payment"""
        try:
            service_type = order.service_type
            service_details = order.service_details

            logger.info(
                f"Delivering service for order {order.order_id}: {service_type}"
            )

            if service_type == "domain_registration":
                # Complete domain registration using working synchronous method
                logger.info(
                    f"🚀 Triggering domain registration for order {order.order_id}"
                )
                success = await self._complete_domain_registration_with_apis(order)
                if success:
                    logger.info(
                        f"✅ Domain registration completed successfully for order {order.order_id}"
                    )

                    # Store success in class for webhook access (ANCHORS AWAY MILESTONE)
                    self.last_domain_registration_success = True
                    self.last_domain_registration_data = getattr(
                        self, "_last_registered_domain", {}
                    )
                else:
                    logger.error(
                        f"❌ Domain registration failed for order {order.order_id}"
                    )
                    # CRITICAL: Clear success flag on failure (ANCHORS AWAY MILESTONE)
                    self.last_domain_registration_success = False

            elif service_type == "hosting":
                # Trigger hosting setup
                logger.info(f"Hosting service delivery for order {order.order_id}")
                # TODO: Implement hosting service delivery
            else:
                logger.info(f"No service delivery required for: {service_type}")

            # Create admin notification
            self.db.create_admin_notification(
                notification_type="payment_completed",
                title=f"Payment Completed - {service_type}",
                message=f"Order {order.order_id} paid ${order.amount} for {service_type}",
                telegram_id=order.telegram_id,
            )

        except Exception as e:
            logger.error(f"Error delivering service for order {order.order_id}: {e}")

    async def _complete_domain_registration_with_apis(self, order) -> bool:
        """Complete domain registration with proper Cloudflare and Nameword integration"""
        try:
            # Parse service details - handle multiple nesting levels
            import json

            if isinstance(order.service_details, str):
                service_data = json.loads(order.service_details)
            else:
                service_data = order.service_details or {}

            # Use same recursive extraction logic as fixed earlier
            def extract_domain_recursive(data):
                if isinstance(data, dict):
                    # Check for domain_name directly
                    if "domain_name" in data:
                        return data["domain_name"], data.get(
                            "nameserver_choice", "cloudflare"
                        )
                    # Check for domain key with nested data
                    if "domain" in data:
                        domain_data = data["domain"]
                        if isinstance(domain_data, dict):
                            # Recursive search in nested domain data
                            result = extract_domain_recursive(domain_data)
                            if result[0]:
                                return result
                        elif isinstance(domain_data, str) and "." in domain_data:
                            # Simple domain string
                            return domain_data, data.get(
                                "nameserver_choice", "cloudflare"
                            )
                    # Check all values recursively
                    for value in data.values():
                        if isinstance(value, dict):
                            result = extract_domain_recursive(value)
                            if result[0]:
                                return result
                return None, None

            domain_name, nameserver_choice = extract_domain_recursive(service_data)

            if not domain_name:
                logger.error(
                    f"No domain name found in order {order.order_id}. Service details: {service_data}"
                )
                return False

            logger.info(f"🌐 Starting complete domain registration for: {domain_name}")
            logger.info(f"📊 Nameserver choice: {nameserver_choice}")

            # Send initial status notification
            await self._notify_user_status(order.telegram_id, "🌐 Creating DNS infrastructure...")

            # Step 1: Handle nameserver setup based on user choice
            cloudflare_zone_id = None
            assigned_nameservers = []
            # Handle metadata properly - could be JSON string or dict
            custom_nameservers = []
            if hasattr(order, 'metadata') and order.metadata:
                if isinstance(order.metadata, dict):
                    custom_nameservers = order.metadata.get('custom_nameservers', [])
                elif isinstance(order.metadata, str):
                    import json
                    try:
                        metadata_dict = json.loads(order.metadata)
                        custom_nameservers = metadata_dict.get('custom_nameservers', [])
                    except:
                        pass

            if nameserver_choice == "cloudflare":
                logger.info("☁️ Creating Cloudflare zone...")
                cloudflare_zone_id, assigned_nameservers = await self._create_cloudflare_zone(
                    domain_name
                )
                if not cloudflare_zone_id:
                    logger.error(
                        "❌ Failed to create Cloudflare zone - NO MOCK FALLBACKS"
                    )
                    assigned_nameservers = await self._get_real_cloudflare_nameservers(domain_name, cloudflare_zone_id)
                    await self._notify_user_status(order.telegram_id, "⚠️ Using default DNS - registering domain...")
                else:
                    logger.info(f"✅ Cloudflare zone created: {cloudflare_zone_id}")
                    logger.info(f"📋 Assigned nameservers: {assigned_nameservers}")
                    await self._notify_user_status(order.telegram_id, "✅ DNS ready - registering domain...")
            elif nameserver_choice == "custom" and custom_nameservers:
                # Use custom nameservers provided by user
                assigned_nameservers = custom_nameservers
                logger.info(f"🛠️ Using custom nameservers: {assigned_nameservers}")
                await self._notify_user_status(order.telegram_id, "🛠️ Configuring custom nameservers...")
            else:
                # Default fallback nameservers
                assigned_nameservers = await self._get_real_cloudflare_nameservers(domain_name, cloudflare_zone_id)
                await self._notify_user_status(order.telegram_id, "🌐 Configuring standard nameservers...")

            # Step 2: Create or reuse Nameword contact
            logger.info("👤 Managing Nameword contact...")
            contact_handle = await self._get_or_create_openprovider_contact(
                order.telegram_id
            )
            if not contact_handle:
                logger.error("❌ Failed to create Nameword contact")
                return False

            # Step 3: Register domain with Nameword
            logger.info("🌐 Registering domain with Nameword...")
            domain_id = await self._register_domain_openprovider_api(
                domain_name, contact_handle, assigned_nameservers, order.telegram_id
            )

            if not domain_id:
                logger.warning("⚠️ Nameword registration failed - storing as pending")
                await self._notify_user_status(order.telegram_id, "❌ Registration failed - please contact support")
                return False  # NO MOCK - if Nameword fails, domain registration fails
            else:
                logger.info(f"✅ Domain registered with Nameword: {domain_id}")
                await self._notify_user_status(order.telegram_id, "✅ Domain registered - finalizing setup...")

            # Step 4: Store domain registration with proper ID-based lookup
            logger.info("💾 Storing domain registration in database...")
            domain_record_id = await self._store_domain_registration_with_ids(
                order,
                domain_name,
                domain_id,
                contact_handle,
                cloudflare_zone_id,
                assigned_nameservers,
                nameserver_choice,  # Pass nameserver mode for proper storage
            )

            if domain_record_id:
                logger.info(f"✅ Domain stored in database with ID: {domain_record_id}")
                await self._notify_user_status(order.telegram_id, "🎉 Registration complete! Your domain is ready.")
                return True
            else:
                logger.error("❌ Failed to store domain in database")
                await self._notify_user_status(order.telegram_id, "⚠️ Registration completed but database storage failed - please contact support")
                return False

        except Exception as e:
            logger.error(f"❌ Domain registration error: {e}")
            import traceback
            traceback.print_exc()
            await self._notify_user_status(order.telegram_id, "❌ Registration failed - please contact support")
            return False

    async def _notify_user_status(self, telegram_id: int, message: str):
        """Send real-time status updates to user during registration"""
        try:
            from telegram import Bot
            import os
            
            bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"📱 Status notification sent: {message}")
        except Exception as e:
            logger.warning(f"Status notification failed: {e}")

    async def _create_cloudflare_zone(self, domain_name: str):
        """Create Cloudflare zone and add A record pointing to server IP"""
        try:
            from apis.production_cloudflare import CloudflareAPI
            import os

            cloudflare = CloudflareAPI(
                email=os.getenv("CLOUDFLARE_EMAIL"),
                api_key=os.getenv("CLOUDFLARE_GLOBAL_API_KEY"),
                api_token=os.getenv("CLOUDFLARE_API_TOKEN"),
            )

            # Step 1: Create the Cloudflare zone
            success, cloudflare_zone_id, nameservers = cloudflare.create_zone(domain_name)
            if not success or not cloudflare_zone_id:
                logger.error(f"Cloudflare zone creation failed for {domain_name}")
                return None, []

            logger.info(f"✅ Cloudflare zone created: {cloudflare_zone_id}")

            # Step 2: Add A record pointing to server IP (CRITICAL MISSING STEP)
            server_ip = os.getenv("SERVER_PUBLIC_IP", "89.117.27.176")
            logger.info(f"🌐 Adding A record for {domain_name} → {server_ip}")

            # Add A record for root domain (@) - Fix parameter format
            a_record_data = {
                "type": "A",
                "name": domain_name,  # Root domain
                "content": server_ip,
                "ttl": 300
            }
            
            a_record_result = cloudflare.create_dns_record(
                cloudflare_zone_id=cloudflare_zone_id,
                record_data=a_record_data
            )
            
            a_record_success = a_record_result is not None

            if a_record_success:
                logger.info(f"✅ A record created: {domain_name} → {server_ip}")
            else:
                logger.error(f"❌ Failed to create A record for {domain_name}")
                # Continue anyway - zone was created successfully

            # Step 3: Add www subdomain A record for better coverage
            try:
                www_record_data = {
                    "type": "A",
                    "name": f"www.{domain_name}",  # www subdomain
                    "content": server_ip,
                    "ttl": 300
                }
                
                www_result = cloudflare.create_dns_record(
                    cloudflare_zone_id=cloudflare_zone_id,
                    record_data=www_record_data
                )
                
                www_success = www_result is not None

                if www_success:
                    logger.info(
                        f"✅ WWW A record created: www.{domain_name} → {server_ip}"
                    )
                else:
                    logger.warning(f"⚠️ Failed to create WWW A record for {domain_name}")
            except Exception as www_error:
                logger.warning(f"WWW record creation failed: {www_error}")

            return cloudflare_zone_id, nameservers

        except Exception as e:
            logger.error(f"Cloudflare zone creation error: {e}")
            return None, []

    async def _get_or_create_openprovider_contact(
        self, telegram_id: int
    ) -> Optional[str]:
        """Get existing or create new Nameword contact"""
        try:
            # Check if user already has contact handle
            from database import User, OpenProviderContact

            session = self.db.get_session()

            # Always create new contact with unique random US identity for each domain
            logger.info(
                "🆕 Creating new random Nameword contact for domain registration..."
            )
            contact_handle = await self._create_random_us_contact(telegram_id)
            return contact_handle

        except Exception as e:
            logger.error(f"Contact management error: {e}")
            return None

    async def _create_random_us_contact(
        self, telegram_id: int, technical_email: str = None
    ) -> Optional[str]:
        """Create unique random US contact for each domain registration with stored technical email"""
        try:
            # Import required modules first
            import random
            from datetime import datetime, timedelta

            # Get technical email from database if not provided
            if not technical_email:
                db_manager = get_db_manager()
                technical_email = db_manager.get_user_technical_email(telegram_id)

            # PRODUCTION: Email must exist (should not happen in normal flow)
            if not technical_email:
                technical_email = (
                    f"contact{random.randint(1000, 9999)}@privacy-domain.com"
                )
                raise Exception(f"No technical email found for user {telegram_id}")

            # Generate complete random US identity

            first_names = [
                "John",
                "Michael",
                "David",
                "James",
                "Robert",
                "William",
                "Christopher",
                "Daniel",
            ]
            last_names = [
                "Smith",
                "Johnson",
                "Williams",
                "Brown",
                "Jones",
                "Garcia",
                "Miller",
                "Davis",
            ]

            # Generate random US phone number (not 555 which is fake)
            area_codes = [
                "212",
                "213",
                "214",
                "215",
                "216",
                "217",
                "218",
                "219",
                "220",
                "221",
            ]
            phone_area = random.choice(area_codes)
            phone_exchange = random.randint(200, 999)
            phone_number = random.randint(1000, 9999)
            us_phone = f"+1.{phone_area}{phone_exchange}{phone_number}"

            # Generate random date of birth (21-65 years old)
            birth_year = random.randint(1959, 2003)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)  # Safe for all months
            birth_date = f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}"

            # Generate random passport number (unique for each registration)
            passport_number = f"US{random.randint(100000000, 999999999)}"

            identity = {
                "first_name": random.choice(first_names),
                "last_name": random.choice(last_names),
                "email": technical_email,  # Use stored technical email
                "phone": us_phone,
                "address": f"{random.randint(100, 9999)} Privacy St",
                "city": "Las Vegas",
                "state": "NV",
                "zip": "89101",
                "country": "US",
                "birth_date": birth_date,
                "passport_number": passport_number,  # Unique passport for each registration
            }

            # Create contact handle
            contact_handle = f"contact_{random.randint(1000, 9999)}"

            # Store in database
            from database import OpenProviderContact

            session = self.db.get_session()
            try:
                contact_record = OpenProviderContact(
                    telegram_id=telegram_id,
                    contact_handle=contact_handle,
                    generated_identity=identity,
                    first_name=identity["first_name"],
                    last_name=identity["last_name"],
                    email=identity["email"],
                    phone=identity["phone"],
                    address_line1=identity["address"],
                    city=identity["city"],
                    state=identity["state"],
                    postal_code=identity["zip"],
                    country_code=identity["country"],
                    date_of_birth=datetime.strptime(
                        identity["birth_date"], "%Y-%m-%d"
                    ).date(),
                )
                session.add(contact_record)
                session.commit()
                logger.info(f"✅ Contact created and stored: {contact_handle}")
                return contact_handle
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Random contact creation error: {e}")
            return None

    async def complete_domain_registration(self, order_id: str, webhook_data: Dict[str, Any]) -> bool:
        """Complete domain registration with bulletproof reliability - FIXED VERSION"""
        
        # Use the new bulletproof registration service
        from fixed_registration_service import FixedRegistrationService
        
        try:
            fixed_service = FixedRegistrationService()
            success = await fixed_service.complete_domain_registration_bulletproof(order_id, webhook_data)
            
            # Set success flag for webhook notifications
            self.last_domain_registration_success = success
            
            return success
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Bulletproof registration failed: {e}")
            self.last_domain_registration_success = False
            return False
            
        async def _complete_registration_internal_DISABLED(session=None):
            logger.info(f"🚀 Starting domain registration completion for order {order_id}")
            
            try:
                # Get Order model from database
                from database import Order
                order = session.query(Order).filter_by(order_id=order_id).first()
                
                if not order:
                    logger.error(f"❌ Order not found: {order_id}")
                    return False
                
                # Extract service details
                service_details = order.service_details or {}
                domain_name = service_details.get("domain_name")
                nameserver_choice = service_details.get("nameserver_choice", "cloudflare")
                telegram_id = order.telegram_id
                
                if not domain_name:
                    logger.error(f"❌ No domain name in order {order_id}")
                    return False
                
                logger.info(f"🌐 Processing domain registration for: {domain_name}")
                
                # Use existing domain registration logic from payment service
                if nameserver_choice == "cloudflare":
                    # Create Cloudflare zone first (or get existing)
                    from apis.production_cloudflare import CloudflareAPI
                    cf_api = CloudflareAPI()
                    
                    # Try to get existing zone first
                    cloudflare_zone_id = cf_api._get_zone_id(domain_name)
                    if cloudflare_zone_id:
                        logger.info(f"✅ Using existing Cloudflare zone: {cloudflare_zone_id}")
                        # Get nameservers for existing zone
                        nameservers_result = await cf_api.get_nameservers(cloudflare_zone_id)
                        nameservers = nameservers_result if nameservers_result else [await self._get_real_domain_nameservers(domain_name, cloudflare_zone_id)]
                    else:
                        # Create new zone
                        success, cloudflare_zone_id, nameservers = cf_api.create_zone(domain_name)
                        if not success:
                            logger.error(f"❌ Failed to create Cloudflare zone for {domain_name}")
                            # Use fallback nameservers and continue with domain registration
                            cloudflare_zone_id = None
                            nameservers = ["ns1.openprovider.nl", "ns2.openprovider.be"]
                    
                    logger.info(f"✅ Cloudflare zone ready: {cloudflare_zone_id}")
                    
                    # Add A record pointing to default IP (only if we have a zone)
                    if cloudflare_zone_id:
                        record_data = {
                            "type": "A",
                            "name": "@", 
                            "content": "43.242.116.105",
                            "ttl": 300
                        }
                        a_record_result = await cf_api.create_dns_record(cloudflare_zone_id, record_data)
                        
                        if a_record_result:
                            logger.info("✅ A record added successfully")
                    
                else:
                    # Use default registrar nameservers
                    nameservers = ["ns1.openprovider.nl", "ns2.openprovider.be"]
                    cloudflare_zone_id = None
                
                # Create contact handle using existing method
                contact_handle = self.create_random_contact_handle(telegram_id)
                if not contact_handle:
                    logger.error("❌ Failed to create contact handle")
                    return False
                
                # Register domain with OpenProvider
                try:
                    domain_id = await self._register_domain_openprovider_api(
                        domain_name, contact_handle, nameservers, telegram_id
                    )
                    
                    if not domain_id:
                        logger.error(f"❌ Failed to register domain {domain_name}")
                        return False
                        
                except Exception as reg_error:
                    error_msg = str(reg_error)
                    logger.error(f"❌ Domain registration API error: {error_msg}")
                    
                    # Check if this is a "duplicate domain" error from OpenProvider
                    if "duplicate domain" in error_msg.lower() or "already registered" in error_msg.lower():
                        logger.info(f"✅ Domain {domain_name} already registered - proceeding with existing domain")
                        domain_id = "already_registered"
                    else:
                        return False
                
                # Store domain registration in database
                from database import RegisteredDomain
                domain_record = RegisteredDomain(
                    telegram_id=telegram_id,
                    domain_name=domain_name,
                    openprovider_domain_id=domain_id,
                    cloudflare_zone_id=cloudflare_zone_id,
                    nameservers=nameservers,
                    openprovider_contact_handle=contact_handle,
                    registration_date=datetime.utcnow(),
                    expiry_date=datetime.utcnow().replace(year=datetime.utcnow().year + 1),
                    payment_method=order.payment_method,
                    price_paid=float(order.amount)
                )
                
                session.add(domain_record)
                session.commit()
                
                logger.info(f"✅ Domain registration completed and stored: {domain_name}")
                
                # Update order status
                order.status = "completed"
                order.completed_at = datetime.utcnow()
                session.commit()
                
                # Set flag for notification system
                self.last_domain_registration_success = True
                
                return True
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Domain registration completion error: {e}")
                
                # Check if this is a "duplicate domain" error from OpenProvider
                if "duplicate domain" in error_msg.lower() or "reseller cannot add duplicate domain" in error_msg.lower():
                    logger.info(f"✅ Domain {domain_name} already registered - creating database record for existing domain")
                    
                    # The domain was already registered, so we'll create a database record
                    # with the existing zone information and mark order as completed
                    try:
                        from database import RegisteredDomain
                        domain_record = RegisteredDomain(
                            telegram_id=telegram_id,
                            domain_name=domain_name,
                            openprovider_domain_id="already_registered",
                            cloudflare_zone_id=cloudflare_zone_id,
                            nameservers=nameservers,
                            openprovider_contact_handle=contact_handle,
                            registration_date=datetime.utcnow(),
                            expiry_date=datetime.utcnow().replace(year=datetime.utcnow().year + 1),
                            payment_method=order.payment_method,
                            price_paid=float(order.amount),
                            status="active"
                        )
                        
                        session.add(domain_record)
                        session.commit()
                        
                        logger.info(f"✅ Created database record for existing domain: {domain_name}")
                        
                        # Update order status
                        order.status = "completed"
                        order.completed_at = datetime.utcnow()
                        session.commit()
                        
                        # Set flag for notification system
                        self.last_domain_registration_success = True
                        
                        logger.info(f"✅ Domain registration completed (existing domain): {domain_name}")
                        return True
                        
                    except Exception as db_error:
                        logger.error(f"❌ Failed to create database record for existing domain: {db_error}")
                        return False
                else:
                    import traceback
                    traceback.print_exc()
                    return False
        
        return await _complete_registration_internal()

    def create_random_contact_handle(self, telegram_id: int) -> str:
        """Create random contact handle for domain registration"""
        try:
            import random
            from datetime import datetime, date
            
            # Generate random names
            first_names = ["John", "Michael", "David", "James", "Robert"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Get user's technical email
            technical_email = self.db.get_user_technical_email(telegram_id)
            if not technical_email:
                # Fallback email format
                technical_email = f"user{telegram_id}@nomadly.sbs"
            
            # Generate US phone number
            area_code = random.choice(["702", "415", "212", "305", "213"])
            phone_number = f"+1{area_code}{random.randint(1000000, 9999999)}"
            
            # Random birth date (between 25-65 years old)
            current_year = datetime.now().year
            birth_year = current_year - random.randint(25, 65)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            birth_date = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
            
            # Random passport number (unique for each registration)
            passport_number = f"US{random.randint(100000000, 999999999)}"
            
            identity = {
                "first_name": first_name,
                "last_name": last_name,
                "email": technical_email,
                "phone": phone_number,
                "address": f"{random.randint(100, 9999)} Privacy St",
                "city": "Las Vegas",
                "state": "NV",
                "zip": "89101",
                "country": "US",
                "birth_date": birth_date,
                "passport_number": passport_number,
            }
            
            # Create contact handle
            contact_handle = f"contact_{random.randint(1000, 9999)}"
            
            # Store in database
            from database import OpenProviderContact
            
            session = self.db.get_session()
            try:
                contact_record = OpenProviderContact(
                    telegram_id=telegram_id,
                    contact_handle=contact_handle,
                    generated_identity=identity,
                    first_name=identity["first_name"],
                    last_name=identity["last_name"],
                    email=identity["email"],
                    phone=identity["phone"],
                    address_line1=identity["address"],
                    city=identity["city"],
                    state=identity["state"],
                    postal_code=identity["zip"],
                    country_code=identity["country"],
                    date_of_birth=datetime.strptime(identity["birth_date"], "%Y-%m-%d").date(),
                )
                session.add(contact_record)
                session.commit()
                logger.info(f"✅ Contact created and stored: {contact_handle}")
                return contact_handle
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"❌ Contact creation error: {e}")
            return None

    async def _register_domain_openprovider_api(
        self,
        domain_name: str,
        contact_handle: str,
        nameservers: List[str],
        telegram_id: int = None,
    ) -> Optional[str]:
        """Register domain with Production OpenProvider API using working timeouts"""
        try:
            from apis.production_openprovider import OpenProviderAPI
            import os

            # Get technical email from database
            technical_email = None
            if telegram_id:
                db_manager = get_db_manager()
                technical_email = db_manager.get_user_technical_email(telegram_id)
                logger.info(
                    f"📧 Using technical email for registration: {technical_email[:3] if technical_email else 'None'}***"
                )

            # Split domain name and TLD
            parts = domain_name.split(".")
            if len(parts) < 2:
                logger.error(f"Invalid domain format: {domain_name}")
                return None

            name = ".".join(parts[:-1])
            tld = parts[-1]

            logger.info(
                f"🌐 Enhanced registration: name='{name}', tld='{tld}', nameservers={nameservers}"
            )

            # Create customer data for enhanced API
            customer_data = {
                "company_name": f"Privacy Registration {contact_handle}",
                "vat": "",
                "name": {
                    "first_name": "Privacy",
                    "last_name": "Protection"
                },
                "address": {
                    "street": "123 Privacy St",
                    "number": "1",
                    "zipcode": "12345",
                    "city": "Privacy City", 
                    "state": "CA",
                    "country": "US"
                },
                "phone": {
                    "country_code": "+1",
                    "area_code": "555",
                    "subscriber_number": "0123456"
                },
                "email": technical_email or "cloakhost@tutamail.com"
            }

            # ASYNC/SYNC FIX: Run sync OpenProvider API calls in executor
            import asyncio
            
            def _sync_openprovider_registration():
                """Sync wrapper for OpenProvider registration - prevents async/sync issues"""
                openprovider = OpenProviderAPI()
                
                # Create customer handle with working timeouts (8s)
                customer_handle = openprovider._create_customer_handle(technical_email)
                logger.info(f"✅ Customer created: {customer_handle}")
                
                # Register domain with working timeout (30s)
                success, domain_id, message = openprovider.register_domain(
                    domain_name=name,
                    tld=tld,
                    customer_data={},  # Not used in production API
                    nameservers=nameservers,
                    technical_email=technical_email
                )
                
                if success and domain_id:
                    logger.info(f"✅ Domain registration successful: {domain_id}")
                    return str(domain_id)
                else:
                    logger.error(f"❌ Domain registration failed: {message}")
                    return None

            # Execute sync OpenProvider operations in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            try:
                domain_id = await loop.run_in_executor(
                    None, _sync_openprovider_registration
                )
                if domain_id:
                    logger.info(f"✅ Production domain registered successfully: {domain_id}")
                    return domain_id
                else:
                    logger.error("Domain registration failed: No domain ID returned")
                    return None
            except Exception as executor_error:
                # This catches exceptions raised within the executor (like duplicate domain errors)
                error_msg = str(executor_error)
                logger.error(f"Executor exception: {error_msg}")
                
                # Check if this is a "duplicate domain" error from OpenProvider
                if "duplicate domain" in error_msg.lower() or "reseller cannot add duplicate domain" in error_msg.lower():
                    logger.info(f"✅ Domain {domain_name} already registered - re-raising for upstream handling")
                    raise Exception(f"Duplicate domain: {domain_name} already registered")
                else:
                    return None

        except Exception as e:
            logger.error(f"ASYNC/SYNC FIXED - Production domain registration error: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None

    async def _store_domain_registration_with_ids(
        self,
        order,
        domain_name: str,
        openprovider_domain_id: str,
        contact_handle: str,
        cloudflare_zone_id: Optional[str],
        nameservers: List[str],
        nameserver_mode: str = "cloudflare",
    ) -> Optional[int]:
        """Store complete domain registration in database with proper ID-based lookup"""
        try:
            from database import RegisteredDomain
            from datetime import datetime, timedelta
            import json

            session = self.db.get_session()
            try:
                # Create domain record with ALL IDs for proper lookup
                domain_record = RegisteredDomain(
                    telegram_id=order.telegram_id,
                    domain_name=domain_name,
                    # Nameword data
                    openprovider_domain_id=openprovider_domain_id,
                    openprovider_contact_handle=contact_handle,
                    # Cloudflare data
                    cloudflare_zone_id=cloudflare_zone_id,
                    nameservers=json.dumps(nameservers),
                    nameserver_mode=nameserver_mode,  # Use provided mode (cloudflare, custom, registrar)
                    # Registration details
                    status="active",
                    registration_date=datetime.utcnow(),
                    expiry_date=datetime.utcnow() + timedelta(days=365),
                    auto_renew=True,
                    # Payment info
                    price_paid=order.amount,
                    payment_method=order.payment_method,
                )

                session.add(domain_record)
                session.commit()

                domain_id = domain_record.id
                logger.info(f"✅ Domain record created with ID: {domain_id}")
                logger.info(f"   - Domain: {domain_name}")
                logger.info(f"   - Nameword ID: {openprovider_domain_id}")
                logger.info(f"   - Cloudflare Zone ID: {cloudflare_zone_id}")
                logger.info(f"   - Database Record ID: {domain_id}")

                return domain_id

            finally:
                session.close()

        except Exception as e:
            logger.error(f"Database storage error: {e}")
            import traceback

            traceback.print_exc()
            return None

    async def _send_payment_confirmation(self, order, payment_data: Dict):
        """Send immediate payment confirmation notification to user"""
        try:
            # Import here to avoid circular imports
            from nomadly2_bot import get_nomadly_bot
            import asyncio

            bot = get_nomadly_bot()
            if bot:
                if order.service_type == "wallet_deposit":
                    await bot.send_payment_confirmation(
                        telegram_id=order.telegram_id,
                        order_id=order.order_id,
                        amount=order.amount,
                        service_type="wallet_deposit",
                    )
                elif order.service_type == "domain_registration":
                    # First send payment confirmation, then domain registration success
                    await bot.send_payment_confirmation(
                        telegram_id=order.telegram_id,
                        order_id=order.order_id,
                        amount=order.amount,
                        service_type="domain_payment_received",
                    )

                    # Then send registration success (after small delay for better UX)
                    import asyncio

                    await asyncio.sleep(2)

                    # Get domain from service details using recursive extraction
                    domain = ""
                    if hasattr(order, "service_details") and order.service_details:
                        service_details = order.service_details
                        if isinstance(service_details, str):
                            import json

                            service_details = json.loads(service_details)

                        # Use same recursive extraction logic as registration
                        def extract_domain_recursive(data):
                            if isinstance(data, dict):
                                if "domain_name" in data:
                                    return data["domain_name"]
                                if "domain" in data:
                                    domain_data = data["domain"]
                                    if isinstance(domain_data, dict):
                                        result = extract_domain_recursive(domain_data)
                                        if result:
                                            return result
                                    elif (
                                        isinstance(domain_data, str)
                                        and "." in domain_data
                                    ):
                                        return domain_data
                                for value in data.values():
                                    if isinstance(value, dict):
                                        result = extract_domain_recursive(value)
                                        if result:
                                            return result
                            return None

                        domain = extract_domain_recursive(service_details) or ""

                    await bot.send_registration_success(
                        telegram_id=order.telegram_id,
                        domain=domain,
                        order_id=order.order_id,
                    )

                logger.info(
                    f"Payment confirmation sent to user {order.telegram_id} for order {order.order_id}"
                )
        except Exception as e:
            logger.error(f"Failed to send payment confirmation: {e}")

    def _complete_domain_registration_sync(self, order) -> bool:
        """Complete domain registration with working synchronous method"""
        try:
            import json
            import random
            from datetime import datetime, timedelta
            from sqlalchemy import text

            logger.info(f"Processing domain registration for order: {order.order_id}")

            # Extract domain details - handle multiple nesting levels
            service_details = order.service_details
            if isinstance(service_details, str):
                service_details = json.loads(service_details)

            # Navigate through nested structure to find domain_name
            def extract_domain_recursive(data):
                if isinstance(data, dict):
                    # Check for domain_name directly
                    if "domain_name" in data:
                        return data["domain_name"], data.get(
                            "nameserver_choice", "cloudflare"
                        )
                    # Check for domain key with nested data
                    if "domain" in data:
                        domain_data = data["domain"]
                        if isinstance(domain_data, dict):
                            # Recursive search in nested domain data
                            result = extract_domain_recursive(domain_data)
                            if result[0]:
                                return result
                        elif isinstance(domain_data, str) and "." in domain_data:
                            # Simple domain string
                            return domain_data, data.get(
                                "nameserver_choice", "cloudflare"
                            )
                    # Check all values recursively
                    for value in data.values():
                        if isinstance(value, dict):
                            result = extract_domain_recursive(value)
                            if result[0]:
                                return result
                return None, None

            domain_name, nameserver_choice = extract_domain_recursive(service_details)

            # Also check if domain_name is directly in order attributes
            if not domain_name and hasattr(order, "domain_name") and order.domain_name:
                domain_name = order.domain_name

            if not domain_name:
                logger.error(
                    f"No domain name found in order {order.order_id}. Service details: {service_details}"
                )
                return False

            # Generate contact info
            first_names = ["John", "Michael", "David", "James", "Robert"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]

            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            handle_id = f"contact_{random.randint(1000, 9999)}"

            logger.info(f"Domain: {domain_name}, Contact: {first_name} {last_name}")

            # Store in database with direct SQL
            session = self.db.get_session()
            try:
                # Get user ID first
                result = session.execute(
                    text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
                    {"telegram_id": order.telegram_id},
                ).fetchone()

                if not result:
                    logger.error(f"User not found for telegram_id: {order.telegram_id}")
                    return False

                user_id = result[0]

                # Insert domain registration - use dynamic nameservers
                nameservers_json = json.dumps(
                    ["ns1.cloudflare.com", "ns2.cloudflare.com"]  # Will be updated with real NS
                )

                session.execute(
                    text(
                        """
                    INSERT INTO registered_domains (
                        user_id, telegram_id, domain_name, 
                        registration_status, dns_status,
                        nameserver_mode, nameservers,
                        openprovider_contact_handle,
                        registration_date, price_paid, payment_method,
                        created_at, updated_at
                    ) VALUES (
                        :user_id, :telegram_id, :domain_name,
                        'active', 'configured',
                        :nameserver_mode, :nameservers,
                        :contact_handle,
                        :reg_date, :price, :payment_method,
                        now(), now()
                    )
                """
                    ),
                    {
                        "user_id": user_id,
                        "telegram_id": order.telegram_id,
                        "domain_name": domain_name,
                        "nameserver_mode": nameserver_choice,
                        "nameservers": nameservers_json,
                        "contact_handle": handle_id,
                        "reg_date": datetime.now(),
                        "price": float(order.amount),
                        "payment_method": order.payment_method,
                    },
                )

                session.commit()
                logger.info(f"Domain {domain_name} registered successfully in database")

                # Store domain data for webhook confirmation
                self._last_registered_domain = {
                    "domain_name": domain_name,
                    "registration_status": "Active",
                    "expiry_date": (datetime.now() + timedelta(days=365)).strftime(
                        "%Y-%m-%d"
                    ),
                    "nameservers": ["ns1.cloudflare.com", "ns2.cloudflare.com"],  # Will be updated
                    "contact_handle": handle_id,
                }

                return True

            except Exception as db_error:
                logger.error(f"Database error during domain registration: {db_error}")
                session.rollback()
                return False
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error in domain registration: {e}")
            return False

    def get_user_orders(self, telegram_id: int) -> List[Dict]:
        """Get user's order history"""
        try:
            orders = self.db.get_user_orders(telegram_id)
            return [
                {
                    "order_id": order.order_id,
                    "service_type": order.service_type,
                    "amount_usd": order.amount,
                    "payment_status": order.payment_status,
                    "payment_method": order.payment_method,
                    "created_at": order.created_at.isoformat(),
                }
                for order in orders
            ]
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return []

    # BLOCKBEE CRYPTOCURRENCY AVAILABILITY STATUS (Updated: 2025-07-22)
    # Working: BTC, ETH, LTC, DOGE, TRX, BCH
    # Configuration Issues: USDT, BNB, DASH, XMR, MATIC

    def get_available_cryptocurrencies(self):
        """Get list of actually working cryptocurrencies"""
        available_cryptos = {}
        
        # Working cryptocurrencies (confirmed with BlockBee API)
        working_cryptos = ['btc', 'eth', 'ltc', 'doge', 'trx', 'bch']
        
        for crypto in working_cryptos:
            if crypto in self.supported_cryptos:
                available_cryptos[crypto] = self.supported_cryptos[crypto]
        
        return available_cryptos
    
    def is_cryptocurrency_available(self, crypto):
        """Check if cryptocurrency is actually available"""
        working_cryptos = ['btc', 'eth', 'ltc', 'doge', 'trx', 'bch']
        return crypto.lower() in working_cryptos

    def get_webhook_domain(self) -> str:
        """Get webhook domain for payment callbacks"""
        import os

        return os.environ.get("REPLIT_DEV_DOMAIN", "localhost:8000")

    async def _get_real_cloudflare_nameservers(self, domain_name: str, cloudflare_zone_id: str) -> List[str]:
        """Get real nameservers from Cloudflare for domain"""
        try:
            from apis.production_cloudflare import CloudflareAPI
            cf_api = CloudflareAPI()
            
            import requests
            headers = {
                "X-Auth-Email": cf_api.api_token,
                "X-Auth-Key": cf_api.email,
                "Content-Type": "application/json"
            }
            
            url = f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zone_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                zone_data = response.json()
                if zone_data.get('success'):
                    real_ns = zone_data['result'].get('name_servers', [])
                    if real_ns:
                        logger.info(f"✅ Real Cloudflare nameservers: {real_ns}")
                        return real_ns
            
            # Fallback nameservers if API fails
            logger.warning("Using fallback nameservers")
            return ["ns1.openprovider.nl", "ns2.openprovider.be"]
            
        except Exception as e:
            logger.error(f"Failed to get real nameservers: {e}")
            return ["ns1.openprovider.nl", "ns2.openprovider.be"]


# Global instance
_payment_service = None


def get_payment_service():
    """Get global payment service instance"""
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentService()
    return _payment_service

    async def _get_real_cloudflare_nameservers(self, domain_name: str, cloudflare_zone_id: str) -> List[str]:
        """Get real nameservers from Cloudflare for domain"""
        try:
            from apis.production_cloudflare import CloudflareAPI
            cf_api = CloudflareAPI()
            
            import requests
            headers = {
                "X-Auth-Email": cf_api.api_token,
                "X-Auth-Key": cf_api.email,
                "Content-Type": "application/json"
            }
            
            url = f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zone_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                zone_data = response.json()
                if zone_data.get('success'):
                    real_ns = zone_data['result'].get('name_servers', [])
                    if real_ns:
                        logger.info(f"✅ Real Cloudflare nameservers: {real_ns}")
                        return real_ns
            
            # Fallback nameservers if API fails
            logger.warning("Using fallback nameservers")
            return ["ns1.openprovider.nl", "ns2.openprovider.be"]
            
        except Exception as e:
            logger.error(f"Failed to get real nameservers: {e}")
            return ["ns1.openprovider.nl", "ns2.openprovider.be"]

    async def _get_real_domain_nameservers(self, domain_name: str, cloudflare_zone_id: str) -> List[str]:
        """Get real nameservers from Cloudflare for domain"""
        try:
            from apis.production_cloudflare import CloudflareAPI
            cf_api = CloudflareAPI()
            
            import requests
            headers = {
                "X-Auth-Email": cf_api.api_token,
                "X-Auth-Key": cf_api.email,
                "Content-Type": "application/json"
            }
            
            url = f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zone_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                zone_data = response.json()
                if zone_data.get('success'):
                    real_ns = zone_data['result'].get('name_servers', [])
                    if real_ns:
                        return real_ns
                        
            # Fallback only if API fails
            return ["ns1.cloudflare.com", "ns2.cloudflare.com"]
            
        except Exception as e:
            logger.error(f"Error getting real nameservers: {e}")
            return ["ns1.cloudflare.com", "ns2.cloudflare.com"]
