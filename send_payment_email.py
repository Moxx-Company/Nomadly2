#!/usr/bin/env python3
"""
Send Payment Details via Brevo (Sendinblue)
==========================================

Sends crypto payment information to customer email using Brevo API.
"""

import requests
import json
import os
from datetime import datetime

def send_payment_email_brevo():
    """Send payment details to customer via Brevo"""
    
    # Payment details from the order we created
    order_details = {
        'order_id': '4064c994-e2fb-4dc1-8570-727f1303ad68',
        'domain': 'ontest072248xyz.sbs',
        'price_usd': '9.87',
        'eth_amount': '0.00261469',
        'eth_address': '0xDCCf22CBEe0df2E9d298e02fdDC0D991c39A0Ff5',
        'customer_email': 'onarrival21@gmail.com'
    }
    
    # Email content
    subject = f"Payment Instructions - Domain Registration Order {order_details['order_id'][:8]}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c5aa0;">🌊 Nomadly2 Domain Registration</h2>
            <h3 style="color: #1a472a;">Payment Instructions</h3>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4>Order Details:</h4>
                <ul>
                    <li><strong>Domain:</strong> {order_details['domain']}</li>
                    <li><strong>Price:</strong> ${order_details['price_usd']} USD</li>
                    <li><strong>Order ID:</strong> {order_details['order_id']}</li>
                </ul>
            </div>
            
            <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4 style="color: #1a472a;">💰 Payment Instructions:</h4>
                <p><strong>Cryptocurrency:</strong> Ethereum (ETH)</p>
                <p><strong>Amount to Send:</strong> <span style="font-family: monospace; background: #fff; padding: 2px 4px; border: 1px solid #ddd;">{order_details['eth_amount']} ETH</span></p>
                <p><strong>Payment Address:</strong></p>
                <div style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 3px; font-family: monospace; word-break: break-all;">
                    {order_details['eth_address']}
                </div>
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h4>⚡ Important Notes:</h4>
                <ul>
                    <li>Send <strong>exactly</strong> {order_details['eth_amount']} ETH to the address above</li>
                    <li>Payment must be received within 24 hours</li>
                    <li>Domain registration will begin automatically upon payment confirmation</li>
                    <li>You will receive confirmation once registration is complete</li>
                </ul>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                <p style="color: #666; font-size: 14px;">
                    <strong>Nomadly2 Offshore Domain Services</strong><br>
                    Privacy-focused domain registration with cryptocurrency payments<br>
                    Order created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    NOMADLY2 DOMAIN REGISTRATION - PAYMENT INSTRUCTIONS
    
    Order Details:
    - Domain: {order_details['domain']}
    - Price: ${order_details['price_usd']} USD
    - Order ID: {order_details['order_id']}
    
    PAYMENT INSTRUCTIONS:
    Cryptocurrency: Ethereum (ETH)
    Amount: {order_details['eth_amount']} ETH
    Address: {order_details['eth_address']}
    
    IMPORTANT:
    - Send exactly {order_details['eth_amount']} ETH to the address above
    - Payment window: 24 hours
    - Registration starts automatically upon confirmation
    
    Nomadly2 Offshore Domain Services
    Order created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
    """
    
    # Brevo API configuration
    brevo_api_key = os.getenv('BREVO_API_KEY')
    
    if not brevo_api_key:
        print("⚠️ BREVO_API_KEY not found in environment")
        print("📧 Email content prepared but cannot send without API key")
        print(f"Subject: {subject}")
        print(f"To: {order_details['customer_email']}")
        print("\nEmail content:")
        print("="*50)
        print(text_content)
        return False
    
    # Brevo API request
    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        'accept': 'application/json',
        'api-key': brevo_api_key,
        'content-type': 'application/json'
    }
    
    # Get sender email from environment (securely stored)
    sender_email = os.getenv('SENDER_EMAIL', 'noreply@cloakhost.ru')
    
    payload = {
        'sender': {
            'name': 'Nomadly2 Domain Services',
            'email': sender_email
        },
        'to': [
            {
                'email': order_details['customer_email'],
                'name': 'Domain Customer'
            }
        ],
        'subject': subject,
        'htmlContent': html_content,
        'textContent': text_content
    }
    
    try:
        print(f"📧 Sending payment instructions to {order_details['customer_email']}")
        print(f"🔗 API URL: {url}")
        print(f"📝 Payload size: {len(json.dumps(payload))} bytes")
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Email sent successfully via Brevo")
            print(f"📬 Payment instructions delivered to {order_details['customer_email']}")
            return True
        else:
            print(f"❌ Email send failed: HTTP {response.status_code}")
            print(f"❌ Error details: {response.text}")
            
            # Try to parse error response
            try:
                error_data = response.json()
                print(f"❌ Parsed error: {error_data}")
            except:
                print("❌ Could not parse error response as JSON")
            
            return False
            
    except Exception as e:
        print(f"❌ Exception sending email: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    send_payment_email_brevo()