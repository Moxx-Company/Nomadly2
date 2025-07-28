#!/usr/bin/env python3
"""
Complete rebuild of button system to fix all responsiveness issues
"""

import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_db_manager
import logging

logger = logging.getLogger(__name__)


class ButtonSystemRebuild:
    """Complete rebuild of button handling system"""

    def __init__(self):
        self.db = get_db_manager()

    async def handle_refresh_status(self, query, order_id: str):
        """Completely rebuilt refresh status handler"""
        try:
            logger.info(f"🔄 REFRESH STATUS: {order_id}")

            # Find order using robust lookup
            order = self._find_order_robust(query.from_user.id, order_id)

            if not order:
                await query.edit_message_text(
                    f"❌ **Order Not Found**\n\n"
                    f"Order `{order_id}` not found in your account.\n"
                    f"Please check your wallet for active orders.",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("💰 My Wallet", callback_data="wallet")]]
                    ),
                )
                return

            # Get order details with safe string handling
            status = getattr(order, "payment_status", "pending")
            amount = getattr(order, "amount_usd", 0)
            payment_method = getattr(order, "payment_method", "unknown")
            service_details = getattr(order, "service_details", "Domain registration")

            # Clean all text to prevent markdown parsing errors
            clean_service = (
                str(service_details)
                .replace("_", " ")
                .replace("`", "")
                .replace("*", "")[:40]
            )
            clean_payment_method = (
                str(payment_method).replace("_", " ").replace("`", "").replace("*", "")
            )
            clean_order_id = str(getattr(order, "order_id", order_id)).replace("_", "-")

            # Build unique message content to avoid "not modified" error
            import time

            timestamp = int(time.time())

            if status == "completed":
                status_icon = "✅"
                status_text = "Payment Confirmed!"
                color = "🟢"
                action_buttons = [
                    [InlineKeyboardButton("🌐 My Domains", callback_data="my_domains")],
                    [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                ]
            elif status == "pending":
                status_icon = "⏳"
                status_text = "Payment Pending..."
                color = "🟡"
                action_buttons = [
                    [
                        InlineKeyboardButton(
                            "📋 Copy Address",
                            callback_data=f"copy_addr_{clean_order_id[:8]}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🔄 Check Again",
                            callback_data=f"refresh_status_{clean_order_id[:8]}_{timestamp}",
                        ),
                        InlineKeyboardButton(
                            "🔄 Switch Payment",
                            callback_data=f"switch_crypto_{clean_order_id[:8]}",
                        ),
                    ],
                ]
            else:
                status_icon = "❌"
                status_text = f"Status: {status.title()}"
                color = "🔴"
                action_buttons = [
                    [
                        InlineKeyboardButton(
                            "🔄 Try Again",
                            callback_data=f"refresh_status_{clean_order_id}_{timestamp}",
                        )
                    ],
                    [InlineKeyboardButton("💬 Support", callback_data="support")],
                ]

            # Build unique message with safe text
            message_text = (
                f"{status_icon} **{status_text}**\n\n"
                f"🏷️ **Order:** {clean_order_id}\n"
                f"💰 **Amount:** ${amount:.2f} USD\n"
                f"🔹 **Method:** {clean_payment_method.title()}\n"
                f"📦 **Service:** {clean_service}\n"
                f"🕒 **Checked:** {timestamp}\n\n"
                f"{color} **Current Status:** {status.upper()}"
            )

            action_buttons.append(
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            )

            await query.edit_message_text(
                message_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(action_buttons),
            )

        except Exception as e:
            logger.error(f"❌ Refresh status error: {e}")
            await query.edit_message_text(
                f"⚠️ **Status Check Failed**\n\n"
                f"Unable to refresh status for order `{order_id}`.\n"
                f"Error: {str(e)[:50]}...\n\n"
                f"Please try again or contact support.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔄 Retry", callback_data=f"check_payment_{order_id}"
                            )
                        ],
                        [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                        [InlineKeyboardButton("💬 Support", callback_data="support")],
                    ]
                ),
            )

    async def handle_crypto_switch(self, query, order_id: str):
        """Completely rebuilt crypto switching handler"""
        try:
            logger.info(f"🔄 CRYPTO SWITCH: {order_id}")

            # Find order
            order = self._find_order_robust(query.from_user.id, order_id)

            if not order:
                await query.edit_message_text(
                    f"❌ **Order Not Found**\n\n"
                    f"Cannot switch payment for order `{order_id}`.\n"
                    f"Please check your wallet.",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("💰 Wallet", callback_data="wallet")]]
                    ),
                )
                return

            # Show crypto options with immediate callback
            amount = getattr(order, "amount_usd", 2.99)
            service_details = getattr(order, "service_details", "Domain registration")

            crypto_keyboard = [
                [
                    InlineKeyboardButton(
                        "₿ Bitcoin", callback_data=f"create_crypto_btc_{order_id}"
                    ),
                    InlineKeyboardButton(
                        "Ξ Ethereum", callback_data=f"create_crypto_eth_{order_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "💎 USDT", callback_data=f"create_crypto_usdt_{order_id}"
                    ),
                    InlineKeyboardButton(
                        "🥈 Litecoin", callback_data=f"create_crypto_ltc_{order_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🐕 Dogecoin", callback_data=f"create_crypto_doge_{order_id}"
                    ),
                    InlineKeyboardButton(
                        "⚡ TRON", callback_data=f"create_crypto_trx_{order_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "« Back to Payment",
                        callback_data=f"refresh_status_{order_id[:8]}_{int(__import__('time').time())}",
                    )
                ],
            ]

            # Clean service details to show proper domain registration info
            if isinstance(service_details, dict):
                domain_name = service_details.get("domain_name", "Unknown Domain")
                clean_service = f"Domain Registration: {domain_name}"
            else:
                clean_service = (
                    str(service_details)
                    .replace("_", " ")
                    .replace("`", "")
                    .replace("*", "")[:50]
                )

            clean_order_id = str(order_id).replace("_", "-")

            await query.edit_message_text(
                f"💳 **Switch Payment Method**\n\n"
                f"📦 **Service:** {clean_service}\n"
                f"💰 **Amount:** ${amount:.2f} USD\n"
                f"🏷️ **Order:** {clean_order_id}\n\n"
                f"Select new cryptocurrency:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(crypto_keyboard),
            )

        except Exception as e:
            logger.error(f"❌ Crypto switch error: {e}")
            await query.edit_message_text(
                f"❌ **Switch Failed**\n\n"
                f"Unable to load payment options.\n"
                f"Error: {str(e)[:50]}...",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔄 Retry", callback_data=f"switch_crypto_{order_id}"
                            )
                        ],
                        [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                    ]
                ),
            )

    async def handle_create_crypto_payment(self, query, crypto: str, order_id: str):
        """Completely rebuilt crypto payment creation"""
        try:
            logger.info(f"💰 CREATE CRYPTO: {crypto} for {order_id}")

            # Find original order
            order = self._find_order_robust(query.from_user.id, order_id)

            if not order:
                await query.edit_message_text(
                    f"❌ **Order Not Found**\n\n"
                    f"Cannot create payment for order `{order_id}`.",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("💰 Wallet", callback_data="wallet")]]
                    ),
                )
                return

            # Create new crypto payment
            from payment_service import PaymentService

            payment_service = PaymentService()

            # Crypto mapping (BlockBee API format)
            crypto_names = {
                "btc": "btc",
                "eth": "eth",
                "usdt": "usdt",
                "ltc": "ltc",
                "doge": "doge",
                "trx": "trx",
            }

            crypto_name = crypto_names.get(crypto, crypto)
            
            # 🔧 FIX: Get proper domain pricing instead of hardcoded fallback
            amount = getattr(order, "amount_usd", None)
            service_details = getattr(order, "service_details", "Domain registration")
            
            # If no amount in order, calculate real pricing from domain
            if amount is None:
                try:
                    # Extract domain from service details
                    domain = None
                    if isinstance(service_details, dict):
                        domain = service_details.get("domain_name") or service_details.get("domain")
                    elif isinstance(service_details, str) and "." in service_details:
                        domain = service_details
                    
                    if domain:
                        from domain_service import get_domain_service
                        domain_service = get_domain_service()
                        
                        # Try real-time pricing first
                        try:
                            domain_info = await domain_service.get_domain_info(domain)
                            amount = domain_info.get("price") if domain_info else None
                        except:
                            pass
                        
                        # Fallback to cached pricing
                        if amount is None:
                            amount = domain_service.get_domain_price(domain)
                    else:
                        # Ultimate fallback with 3.3x multiplier
                        amount = 9.87  # $2.99 * 3.3
                        
                except Exception as e:
                    logger.warning(f"Could not get domain pricing: {e}, using fallback")
                    amount = 9.87  # $2.99 * 3.3

            # Create payment with correct parameter names
            payment_result = await payment_service.create_crypto_payment(
                telegram_id=query.from_user.id,
                amount=amount,
                crypto_currency=crypto_name,
                service_type="domain_registration",
                service_details={
                    "domain": service_details,
                    "type": "domain_registration",
                },
            )

            if payment_result and payment_result.get("payment_address"):
                payment_address = payment_result["payment_address"]
                crypto_amount = payment_result.get("crypto_amount", "N/A")
                new_order_id = payment_result.get("order_id", order_id)

                # Generate QR code for mobile wallets
                qr_data = f"{crypto}:{payment_address}"
                if crypto == "btc":
                    qr_data = f"bitcoin:{payment_address}?amount={crypto_amount}"
                elif crypto == "eth":
                    qr_data = f"ethereum:{payment_address}?value={crypto_amount}"

                # Clean all text to prevent markdown errors
                clean_crypto_amount = str(crypto_amount).replace("_", "")
                clean_address = str(payment_address)[:42]  # Limit length
                clean_order_id = str(new_order_id).replace("_", "-")

                # Make address tap-to-copy by showing it in monospace format
                formatted_message = (
                    f"💰 **New {crypto.upper()} Payment**\n\n"
                    f"⚡ **Send exactly:** {clean_crypto_amount} {crypto.upper()}\n\n"
                    f"📍 **Payment Address (Tap to Copy):**\n"
                    f"`{clean_address}`\n\n"
                    f"• Touch address above and select 'Copy'\n"
                    f"• Payment auto-confirms within minutes\n"
                    f"• Address valid for 24 hours"
                )

                await query.edit_message_text(
                    formatted_message,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "📋 Copy Address",
                                    callback_data=f"copy_addr_{clean_order_id[:8]}",
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "📊 Check Status",
                                    callback_data=f"refresh_status_{clean_order_id[:8]}_{int(__import__('time').time())}",
                                ),
                                InlineKeyboardButton(
                                    "🔄 Switch Payment",
                                    callback_data=f"switch_crypto_{clean_order_id[:8]}",
                                ),
                            ],
                            [
                                InlineKeyboardButton(
                                    "💰 Wallet", callback_data="wallet"
                                ),
                                InlineKeyboardButton(
                                    "🏠 Menu", callback_data="main_menu"
                                ),
                            ],
                        ]
                    ),
                )

            else:
                raise Exception("Payment creation returned no address")

        except Exception as e:
            logger.error(f"❌ Create crypto payment error: {e}")
            await query.edit_message_text(
                f"❌ **Payment Creation Failed**\n\n"
                f"Unable to create {crypto.upper()} payment.\n"
                f"Error: {str(e)[:50]}...\n\n"
                f"Please try again or contact support.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔄 Try Again",
                                callback_data=f"create_crypto_{crypto}_{order_id}",
                            )
                        ],
                        [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                        [InlineKeyboardButton("💬 Support", callback_data="support")],
                    ]
                ),
            )

    def _find_order_robust(self, user_id: int, order_id: str):
        """Robust order lookup with multiple strategies - sync method"""
        try:
            # Strategy 1: Direct lookup with enhanced logging
            logger.info(f"🔍 Strategy 1: Direct lookup for {order_id}")
            if len(order_id) > 8:
                try:
                    order = self.db.get_order(order_id)
                    if order:
                        logger.info(f"✅ Direct lookup successful: {order.order_id}")
                        return order
                except Exception as e:
                    logger.debug(f"Direct lookup failed: {e}")

            # Strategy 1b: Try cleaned order ID (underscores to dashes handling)
            clean_id = order_id.replace("-", "_")
            if clean_id != order_id:
                try:
                    order = self.db.get_order(clean_id)
                    if order:
                        logger.info(f"✅ Cleaned lookup successful: {order.order_id}")
                        return order
                except Exception as e:
                    logger.debug(f"Cleaned lookup failed: {e}")

            # Strategy 2: Partial match with enhanced logging
            logger.info(f"🔍 Strategy 2: Partial match for {order_id[:8]}")
            try:
                all_orders = self.db.get_user_orders(user_id)
                logger.info(f"Found {len(all_orders)} user orders to check")
                for order in all_orders:
                    if (
                        hasattr(order, "order_id")
                        and str(order.order_id)[:8] == order_id[:8]
                    ):
                        logger.info(f"✅ Partial match found: {order.order_id}")
                        return order
            except Exception as e:
                logger.debug(f"Partial match failed: {e}")

            # Strategy 3: Production order IDs from monitoring logs
            production_mappings = {
                "f5d79497": "f5d79497-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "9b1476c5": "9b1476c5-xxxx-xxxx-xxxx-xxxxxxxxxxxx", 
                "7fe2f6ff": "7fe2f6ff-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "52c2d823": "52c2d823-3ad8-4f89-9e1a-8645a0737356",  # Known working order
            }

            # Try to find full order by matching partial ID from database
            if order_id[:8] in production_mappings or len(order_id) == 8:
                try:
                    all_orders = self.db.get_user_orders(user_id)
                    for order in all_orders:
                        order_str = str(getattr(order, "order_id", ""))
                        if order_str.startswith(order_id[:8]):
                            logger.info(f"✅ Production match found: {order_str}")
                            return order
                except Exception as e:
                    logger.debug(f"Production match failed: {e}")

            return None

        except Exception as e:
            logger.error(f"Order lookup error: {e}")
            return None


# Global instance
button_system = ButtonSystemRebuild()


# Export functions for use in main bot
async def handle_rebuilt_refresh_status(query, order_id):
    await button_system.handle_refresh_status(query, order_id)


async def handle_rebuilt_crypto_switch(query, order_id):
    await button_system.handle_crypto_switch(query, order_id)


async def handle_rebuilt_create_crypto(query, crypto, order_id):
    await button_system.handle_create_crypto_payment(query, crypto, order_id)
