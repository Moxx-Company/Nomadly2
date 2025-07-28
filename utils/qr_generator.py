"""
QR Code generator for cryptocurrency payment addresses
"""

import qrcode
import os
import logging

logger = logging.getLogger(__name__)


def generate_qr_code(address: str) -> str:
    """Generate QR code for cryptocurrency address"""
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        # Add data and make the QR code
        qr.add_data(address)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to temporary file
        qr_filename = f"qr_{address[:8]}.png"
        qr_path = os.path.join("/tmp", qr_filename)
        img.save(qr_path)

        logger.info(f"Generated QR code for address: {address[:10]}...")
        return qr_path

    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return None
