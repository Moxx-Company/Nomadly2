"""
Utility functions for the hosting bot
"""

import re
import logging

logger = logging.getLogger(__name__)


def format_currency(amount: float) -> str:
    """Format currency amount to 2 decimal places"""
    return f"${amount:.2f}"


def validate_domain(domain: str) -> bool:
    """Validate domain name format"""
    if not domain:
        return False

    # Basic domain validation regex
    domain_pattern = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    )

    return bool(domain_pattern.match(domain.lower()))


def sanitize_username(username: str) -> str:
    """Sanitize username for database storage"""
    if not username:
        return "unknown"

    # Remove @ symbol and limit length
    username = username.replace("@", "").strip()
    return username[:50] if len(username) > 50 else username


def generate_order_reference(order_id: int) -> str:
    """Generate a human-readable order reference"""
    return f"Nomadly-{order_id:06d}"


def parse_crypto_amount(amount_str: str) -> float:
    """Parse cryptocurrency amount from string"""
    try:
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r"[^\d.]", "", amount_str)
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display"""
    try:
        from datetime import datetime

        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return timestamp_str


def validate_crypto_address(address: str, crypto_type: str) -> bool:
    """Basic validation for cryptocurrency addresses"""
    if not address:
        return False

    address_patterns = {
        "btc": r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$",
        "eth": r"^0x[a-fA-F0-9]{40}$",
        "ltc": r"^[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$",
        "doge": r"^D[5-9A-HJ-NP-U][1-9A-HJ-NP-Za-km-z]{32}$",
    }

    pattern = address_patterns.get(crypto_type.lower())
    if not pattern:
        return True  # Unknown crypto type, assume valid

    return bool(re.match(pattern, address))


async def safe_edit_message(query, text, reply_markup=None, parse_mode="HTML"):
    """Safely edit message text, handling photo messages properly"""
    try:
        # Try to edit the message text first
        await query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode=parse_mode
        )
        return True
    except Exception as e:
        # If editing fails (likely a photo message), send a new message
        logger.info(f"Couldn't edit message (likely photo), sending new message: {e}")
        try:
            await query.message.reply_text(
                text, reply_markup=reply_markup, parse_mode=parse_mode
            )
            # Try to delete the old message if possible
            try:
                await query.message.delete()
            except Exception as delete_error:
                logger.warning(f"Couldn't delete old message: {delete_error}")
            return True
        except Exception as send_error:
            logger.error(f"Failed to send new message: {send_error}")
            return False


def truncate_string(text: str, max_length: int = 50) -> str:
    """Truncate string to specified length"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def is_valid_email(email: str) -> bool:
    """Validate email address format"""
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return bool(email_pattern.match(email))
