"""QR Code generation utilities for cryptocurrency payments"""

import qrcode
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def generate_payment_qr_code(
    address: str, amount: float, coin: str = "bitcoin"
) -> Optional[bytes]:
    """
    Generate a QR code for cryptocurrency payment

    Args:
        address: Cryptocurrency wallet address
        amount: Payment amount in the cryptocurrency
        coin: Type of cryptocurrency (bitcoin, ethereum, etc.)

    Returns:
        QR code image as bytes, or None if generation fails
    """
    try:
        # Create payment URI format
        if coin.lower() in ["bitcoin", "btc"]:
            payment_uri = f"bitcoin:{address}?amount={amount}"
        elif coin.lower() in ["ethereum", "eth"]:
            payment_uri = f"ethereum:{address}?value={amount}"
        else:
            # Generic format for other cryptocurrencies
            payment_uri = f"{coin.lower()}:{address}?amount={amount}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(payment_uri)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        logger.info(f"Generated QR code for {coin} payment: {address}")
        return img_bytes.getvalue()

    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}")
        return None


def generate_simple_address_qr_code(address: str) -> Optional[bytes]:
    """
    Generate a simple QR code containing just the wallet address

    Args:
        address: Cryptocurrency wallet address

    Returns:
        QR code image as bytes, or None if generation fails
    """
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(address)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        logger.info(f"Generated simple QR code for address: {address}")
        return img_bytes.getvalue()

    except Exception as e:
        logger.error(f"Failed to generate simple QR code: {e}")
        return None


def generate_qr_code(address: str) -> str:
    """
    Generate QR code file for cryptocurrency address (compatibility function)

    Args:
        address: Cryptocurrency wallet address

    Returns:
        Path to generated QR code file, or None if generation fails
    """
    try:
        import os

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(address)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to temporary file
        qr_filename = f"qr_{address[:8]}.png"
        qr_path = os.path.join("/tmp", qr_filename)
        img.save(qr_path)

        logger.info(f"Generated QR code file for address: {address}")
        return qr_path

    except Exception as e:
        logger.error(f"Failed to generate QR code file: {e}")
        return None
