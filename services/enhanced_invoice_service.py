"""
Enhanced Invoice Service with QR Codes for Nomadly2
Professional invoice generation with QR codes, multi-currency support, and branding
"""

import qrcode
import io
import base64
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from database import get_db_manager
from utils.translation_helper import t_user
from services.confirmation_service import get_confirmation_service
import os
import json

logger = logging.getLogger(__name__)


class EnhancedInvoiceService:
    """Enhanced invoice system with QR codes and professional features"""

    def __init__(self):
        self.db = get_db_manager()
        self.confirmation_service = get_confirmation_service()

        # Invoice configuration
        self.invoice_prefix = "NOM"
        self.qr_size = (200, 200)
        self.qr_border = 4

        # Currency symbols for display
        self.currency_symbols = {
            "bitcoin": "₿",
            "ethereum": "Ξ",
            "litecoin": "Ł",
            "dogecoin": "Ð",
            "tron": "TRX",
            "usdt": "₮",
            "usd": "$",
        }

        # Exchange rate cache (would typically come from API)
        self.exchange_rates = {
            "bitcoin": 43000.00,
            "ethereum": 2600.00,
            "litecoin": 75.00,
            "dogecoin": 0.08,
            "tron": 0.12,
            "usdt": 1.00,
        }

    async def generate_qr_payment_code(
        self, payment_address: str, amount: str, currency: str, memo: str = ""
    ) -> str:
        """Generate high-quality QR code for crypto payments"""
        try:
            # Create payment URI for mobile wallets
            if currency.lower() == "bitcoin" or currency.lower() == "btc":
                qr_data = f"bitcoin:{payment_address}?amount={amount}&label={memo}"
            elif currency.lower() == "ethereum" or currency.lower() == "eth":
                qr_data = f"ethereum:{payment_address}?value={amount}&label={memo}"
            else:
                # Generic format for other cryptocurrencies
                qr_data = (
                    f"{currency.lower()}:{payment_address}?amount={amount}&label={memo}"
                )

            # Generate high-quality QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=12,
                border=3,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64 for Telegram display
            buffer = io.BytesIO()
            qr_img.save(buffer, format="PNG", quality=95)
            qr_b64 = base64.b64encode(buffer.getvalue()).decode()

            return qr_b64

        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            return ""

    async def generate_payment_invoice(
        self, order_id: str, include_qr: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive payment invoice with QR codes

        Args:
            order_id: Order ID to generate invoice for
            include_qr: Whether to include QR code generation

        Returns:
            Invoice data with QR codes and formatting
        """
        try:
            # Get order details
            order = self.db.get_order(order_id)
            if not order:
                return {"success": False, "error": "Order not found"}

            # Generate invoice number
            invoice_number = self._generate_invoice_number(order_id)

            # Get user language for formatting
            user_language = "en"  # Default, could be retrieved from user preferences

            # Calculate amounts and fees
            amounts = await self._calculate_invoice_amounts(order)

            # Generate QR codes if requested
            qr_codes = {}
            if (
                include_qr
                and hasattr(order, "payment_address")
                and order.payment_address
            ):
                qr_codes = await self._generate_payment_qr_codes(order)

            # Build invoice data
            invoice_data = {
                "success": True,
                "invoice_number": invoice_number,
                "order_id": order_id,
                "created_at": datetime.now().isoformat(),
                "due_date": (datetime.now() + timedelta(hours=24)).isoformat(),
                # Order details
                "service_type": getattr(order, "service_type", "domain_registration"),
                "service_description": self._get_service_description(
                    order, user_language
                ),
                # Amount information
                "amounts": amounts,
                "payment_method": getattr(order, "crypto_currency", "cryptocurrency"),
                "payment_address": getattr(order, "payment_address", ""),
                # QR codes
                "qr_codes": qr_codes,
                # Branding and styling
                "branding": self._get_invoice_branding(),
                "styling": self._get_invoice_styling(),
                # Multi-language support
                "language": user_language,
                "translations": self._get_invoice_translations(
                    getattr(order, "telegram_id", 0), user_language
                ),
            }

            # Generate formatted invoice content
            invoice_data["formatted_content"] = self._format_invoice_content(
                invoice_data
            )

            # Generate payment links if applicable
            if hasattr(order, "payment_address") and order.payment_address:
                invoice_data["payment_links"] = self._generate_payment_links(order)

            return invoice_data

        except Exception as e:
            logger.error(f"Error generating invoice: {e}")
            return {"success": False, "error": str(e)}

    async def create_multi_currency_invoice(
        self, order_id: str, supported_currencies: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create invoice showing multiple cryptocurrency options

        Args:
            order_id: Order ID
            supported_currencies: List of supported cryptocurrencies

        Returns:
            Multi-currency invoice data
        """
        try:
            if not supported_currencies:
                supported_currencies = ["bitcoin", "ethereum", "usdt", "litecoin"]

            # Get base order
            order = self.db.get_order(order_id)
            if not order:
                return {"success": False, "error": "Order not found"}

            base_amount_usd = getattr(order, "amount_usd", 0)

            # Calculate amounts for each currency
            currency_options = []
            for currency in supported_currencies:
                crypto_amount = await self._convert_usd_to_crypto(
                    base_amount_usd, currency
                )

                currency_options.append(
                    {
                        "currency": currency,
                        "display_name": self._get_currency_display_name(currency),
                        "symbol": self.currency_symbols.get(currency, currency.upper()),
                        "amount": crypto_amount,
                        "formatted_amount": self._format_crypto_amount(
                            crypto_amount, currency
                        ),
                        "usd_rate": self.exchange_rates.get(currency, 1.0),
                        "network_fee_estimate": self._estimate_network_fee(
                            currency, crypto_amount
                        ),
                        "confirmation_time": self._get_confirmation_time_estimate(
                            currency
                        ),
                    }
                )

            # Sort by recommendation score
            currency_options.sort(
                key=lambda x: self._get_currency_score(x["currency"]), reverse=True
            )

            return {
                "success": True,
                "order_id": order_id,
                "base_amount_usd": base_amount_usd,
                "currency_options": currency_options,
                "recommended_currency": (
                    currency_options[0] if currency_options else None
                ),
                "valid_until": (datetime.now() + timedelta(hours=24)).isoformat(),
                "service_description": self._get_service_description(order, "en"),
            }

        except Exception as e:
            logger.error(f"Error creating multi-currency invoice: {e}")
            return {"success": False, "error": str(e)}

    async def generate_qr_payment_code(
        self, payment_address: str, amount: float, currency: str, label: str = None
    ) -> str:
        """
        Generate QR code for cryptocurrency payment

        Args:
            payment_address: Cryptocurrency wallet address
            amount: Amount to pay
            currency: Cryptocurrency type
            label: Optional payment label

        Returns:
            Base64 encoded QR code image
        """
        try:
            # Create payment URI based on currency
            payment_uri = self._create_payment_uri(
                payment_address, amount, currency, label
            )

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=self.qr_border,
            )
            qr.add_data(payment_uri)
            qr.make(fit=True)

            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64
            buffer = io.BytesIO()
            qr_image.save(buffer, format="PNG")
            buffer.seek(0)
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()

            return qr_base64

        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return ""

    def create_payment_link(
        self, payment_address: str, amount: float, currency: str
    ) -> str:
        """
        Create clickable payment link

        Args:
            payment_address: Wallet address
            amount: Payment amount
            currency: Cryptocurrency

        Returns:
            Payment link URL
        """
        try:
            if currency == "bitcoin":
                return f"bitcoin:{payment_address}?amount={amount}"
            elif currency == "ethereum":
                return f"ethereum:{payment_address}?value={amount}"
            elif currency == "litecoin":
                return f"litecoin:{payment_address}?amount={amount}"
            else:
                # Generic format
                return f"{currency}:{payment_address}?amount={amount}"

        except Exception as e:
            logger.error(f"Error creating payment link: {e}")
            return payment_address

    async def get_invoice_history(self, telegram_id: int) -> List[Dict[str, Any]]:
        """
        Get invoice history for user

        Args:
            telegram_id: User's Telegram ID

        Returns:
            List of invoice records
        """
        try:
            # This would typically query an invoices table
            # For now, get order history
            orders = self.db.get_user_orders(telegram_id)

            invoice_history = []
            for order in orders:
                invoice_history.append(
                    {
                        "order_id": order.order_id,
                        "invoice_number": self._generate_invoice_number(order.order_id),
                        "amount_usd": getattr(order, "amount_usd", 0),
                        "currency": getattr(order, "crypto_currency", "N/A"),
                        "status": getattr(order, "status", "unknown"),
                        "created_at": getattr(order, "created_at", datetime.now()),
                        "service_type": getattr(
                            order, "service_type", "domain_registration"
                        ),
                    }
                )

            return invoice_history

        except Exception as e:
            logger.error(f"Error getting invoice history: {e}")
            return []

    # Helper methods
    def _generate_invoice_number(self, order_id: str) -> str:
        """Generate formatted invoice number"""
        timestamp = datetime.now().strftime("%Y%m")
        order_suffix = order_id[-6:] if len(order_id) >= 6 else order_id
        return f"{self.invoice_prefix}-{timestamp}-{order_suffix.upper()}"

    async def _calculate_invoice_amounts(self, order) -> Dict[str, Any]:
        """Calculate all amounts for invoice"""
        base_usd = getattr(order, "amount_usd", 0)
        currency = getattr(order, "crypto_currency", "ethereum")
        crypto_amount = getattr(order, "crypto_amount", 0)

        if crypto_amount == 0 and base_usd > 0:
            crypto_amount = await self._convert_usd_to_crypto(base_usd, currency)

        network_fee = self._estimate_network_fee(currency, crypto_amount)

        return {
            "base_usd": base_usd,
            "crypto_amount": crypto_amount,
            "crypto_currency": currency,
            "network_fee": network_fee,
            "total_crypto": crypto_amount + network_fee,
            "formatted_crypto": self._format_crypto_amount(crypto_amount, currency),
            "formatted_total": self._format_crypto_amount(
                crypto_amount + network_fee, currency
            ),
        }

    async def _generate_payment_qr_codes(self, order) -> Dict[str, str]:
        """Generate QR codes for payment"""
        qr_codes = {}

        payment_address = getattr(order, "payment_address", "")
        crypto_amount = getattr(order, "crypto_amount", 0)
        currency = getattr(order, "crypto_currency", "ethereum")

        if payment_address and crypto_amount:
            # Main payment QR
            qr_codes["payment"] = await self.generate_qr_payment_code(
                payment_address,
                crypto_amount,
                currency,
                f"Nomadly Order {order.order_id}",
            )

            # Address-only QR
            qr_codes["address"] = await self.generate_qr_payment_code(
                payment_address, 0, currency, "Payment Address"
            )

        return qr_codes

    def _get_service_description(self, order, language: str) -> str:
        """Get human-readable service description"""
        service_type = getattr(order, "service_type", "domain_registration")

        if service_type == "domain_registration":
            return "Offshore Domain Registration Service"
        elif service_type == "hosting":
            return "Anonymous Hosting Service"
        elif service_type == "url_shortener":
            return "Premium URL Shortening Service"
        else:
            return "Nomadly Offshore Services"

    def _get_invoice_branding(self) -> Dict[str, str]:
        """Get branding information for invoice"""
        return {
            "company_name": "Nomadly2 Offshore Services",
            "tagline": "Resilience • Discretion • Independence",
            "logo_emoji": "🏴‍☠️",
            "website": "nomadly.com",
            "support_contact": "@nomadlysupport",
        }

    def _get_invoice_styling(self) -> Dict[str, str]:
        """Get styling configuration for invoice"""
        return {
            "primary_color": "#1a5d1a",
            "secondary_color": "#2d8f2d",
            "accent_color": "#4caf50",
            "text_color": "#333333",
            "background_color": "#f8f9fa",
            "border_color": "#dee2e6",
        }

    def _get_invoice_translations(
        self, telegram_id: int, language: str
    ) -> Dict[str, str]:
        """Get translation keys for invoice"""
        translations = {}

        keys = [
            "invoice",
            "invoice_number",
            "order_id",
            "amount",
            "payment_method",
            "payment_address",
            "due_date",
            "service_description",
            "total_amount",
            "network_fee",
            "scan_qr_code",
            "or_copy_address",
            "payment_instructions",
        ]

        for key in keys:
            try:
                translations[key] = (
                    t_user(key, telegram_id)
                    if telegram_id
                    else key.replace("_", " ").title()
                )
            except:
                translations[key] = key.replace("_", " ").title()

        return translations

    def _format_invoice_content(self, invoice_data: Dict[str, Any]) -> str:
        """Format invoice as text content"""
        branding = invoice_data["branding"]
        amounts = invoice_data["amounts"]
        translations = invoice_data["translations"]

        content = f"""
{branding['logo_emoji']} {branding['company_name']}
{branding['tagline']}

{translations.get('invoice', 'INVOICE')}: {invoice_data['invoice_number']}
{translations.get('order_id', 'Order ID')}: {invoice_data['order_id']}
Date: {datetime.fromisoformat(invoice_data['created_at']).strftime('%Y-%m-%d %H:%M UTC')}

{translations.get('service_description', 'Service')}: {invoice_data['service_description']}

{translations.get('amount', 'Amount')}: ${amounts['base_usd']:.2f} USD
{translations.get('payment_method', 'Payment Method')}: {amounts['crypto_currency'].upper()}
Crypto Amount: {amounts['formatted_crypto']}
{translations.get('network_fee', 'Network Fee')}: {self._format_crypto_amount(amounts['network_fee'], amounts['crypto_currency'])}
{translations.get('total_amount', 'Total')}: {amounts['formatted_total']}

{translations.get('payment_address', 'Payment Address')}:
{invoice_data['payment_address']}

{translations.get('payment_instructions', 'Instructions')}:
1. {translations.get('scan_qr_code', 'Scan QR code with wallet app')}
2. {translations.get('or_copy_address', 'Or copy payment address above')}
3. Send exact crypto amount shown
4. Payment confirmed automatically

Valid until: {datetime.fromisoformat(invoice_data['due_date']).strftime('%Y-%m-%d %H:%M UTC')}

Support: {branding['support_contact']}
"""
        return content.strip()

    def _generate_payment_links(self, order) -> Dict[str, str]:
        """Generate payment links for various wallets"""
        payment_address = getattr(order, "payment_address", "")
        crypto_amount = getattr(order, "crypto_amount", 0)
        currency = getattr(order, "crypto_currency", "ethereum")

        return {
            "universal": self.create_payment_link(
                payment_address, crypto_amount, currency
            ),
            "copy_address": payment_address,
            "amount_only": str(crypto_amount),
        }

    async def _convert_usd_to_crypto(self, usd_amount: float, currency: str) -> float:
        """Convert USD to cryptocurrency amount"""
        rate = self.exchange_rates.get(currency, 1.0)
        return round(usd_amount / rate, 8)

    def _format_crypto_amount(self, amount: float, currency: str) -> str:
        """Format cryptocurrency amount for display"""
        symbol = self.currency_symbols.get(currency, currency.upper())

        if currency in ["bitcoin", "ethereum", "litecoin"]:
            return f"{amount:.6f} {symbol}"
        elif currency in ["dogecoin", "tron"]:
            return f"{amount:.2f} {symbol}"
        else:
            return f"{amount:.4f} {symbol}"

    def _estimate_network_fee(self, currency: str, amount: float) -> float:
        """Estimate network fee for transaction"""
        fee_rates = {
            "bitcoin": 0.0002,
            "ethereum": 0.003,
            "litecoin": 0.001,
            "dogecoin": 1.0,
            "tron": 1.0,
            "usdt": 2.0,
        }
        return fee_rates.get(currency, 0.001)

    def _get_confirmation_time_estimate(self, currency: str) -> str:
        """Get confirmation time estimate"""
        times = {
            "bitcoin": "10-60 min",
            "ethereum": "2-15 min",
            "litecoin": "5-30 min",
            "dogecoin": "5-60 min",
            "tron": "1-10 min",
            "usdt": "2-15 min",
        }
        return times.get(currency, "10-30 min")

    def _get_currency_display_name(self, currency: str) -> str:
        """Get display name for currency"""
        names = {
            "bitcoin": "Bitcoin",
            "ethereum": "Ethereum",
            "litecoin": "Litecoin",
            "dogecoin": "Dogecoin",
            "tron": "TRON",
            "usdt": "Tether USDT",
        }
        return names.get(currency, currency.upper())

    def _get_currency_score(self, currency: str) -> float:
        """Get recommendation score for currency"""
        scores = {
            "usdt": 95,  # Stable, fast
            "ethereum": 90,  # Fast, reliable
            "bitcoin": 85,  # Reliable but slower
            "litecoin": 80,  # Good alternative
            "tron": 75,  # Fast but less common
            "dogecoin": 70,  # Fun but volatile
        }
        return scores.get(currency, 50)

    def _create_payment_uri(
        self, address: str, amount: float, currency: str, label: str = None
    ) -> str:
        """Create payment URI for QR code"""
        uri = f"{currency}:{address}"

        params = []
        if amount > 0:
            params.append(f"amount={amount}")
        if label:
            params.append(f"label={label}")

        if params:
            uri += "?" + "&".join(params)

        return uri


# Global enhanced invoice service instance
_enhanced_invoice_service = None


def get_enhanced_invoice_service() -> EnhancedInvoiceService:
    """Get global enhanced invoice service instance"""
    global _enhanced_invoice_service
    if _enhanced_invoice_service is None:
        _enhanced_invoice_service = EnhancedInvoiceService()
    return _enhanced_invoice_service
