#!/usr/bin/env python3
"""
Generate QR Code for ETH Payment Address
"""

import qrcode
from io import BytesIO
import base64

def generate_payment_qr():
    """Generate QR code for the test payment"""
    
    # Payment details from the test
    eth_address = "0x2eE1e4514a112EAc46A3B2Ef8e4E2d686F603086"
    amount_eth = "0.00115"
    domain = "ehobalpbwg.sbs"
    
    print("🎯 GENERATING QR CODE FOR ETH PAYMENT")
    print("=" * 40)
    
    # Create QR code with ETH address
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add the ETH address to QR code
    qr.add_data(eth_address)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code
    qr_img.save("eth_payment_qr.png")
    
    print(f"✅ QR Code saved as: eth_payment_qr.png")
    print(f"📱 Payment Address: {eth_address}")
    print(f"💎 Amount: ~{amount_eth} ETH ($2.99)")
    print(f"🌐 Domain: {domain}")
    
    # Create simple text QR for console display
    qr_simple = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr_simple.add_data(eth_address)
    qr_simple.make(fit=True)
    
    print(f"\n📱 QR CODE (scan with wallet):")
    qr_simple.print_ascii(invert=True)
    
    return "eth_payment_qr.png"

if __name__ == "__main__":
    qr_file = generate_payment_qr()
    print(f"\n✅ QR CODE READY")
    print(f"📋 Scan the QR code or send to: 0x2eE1e4514a112EAc46A3B2Ef8e4E2d686F603086")