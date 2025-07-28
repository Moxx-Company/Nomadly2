#!/usr/bin/env python3
"""
Test email sending to verify Brevo configuration
"""
import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

async def send_test_email():
    """Send a simple test email to verify Brevo is working"""
    
    brevo_api_key = os.getenv('BREVO_API_KEY')
    if not brevo_api_key:
        print("❌ BREVO_API_KEY not found")
        return False
    
    # Simple test email
    email_data = {
        "sender": {
            "name": "Nomadly Test",
            "email": "noreply@cloakhost.ru"
        },
        "to": [
            {
                "email": "cloakhost@tutamail.com",
                "name": "Test User"
            }
        ],
        "subject": "🧪 Nomadly Email Test - Please Check",
        "htmlContent": """
        <html>
        <body>
            <h2>🧪 Email Delivery Test</h2>
            <p>This is a test email from Nomadly to verify email delivery is working.</p>
            <p><strong>Time:</strong> 2025-07-25 08:30 UTC</p>
            <p><strong>Purpose:</strong> Debugging email delivery issue</p>
            <p>If you receive this email, the Brevo configuration is working correctly.</p>
        </body>
        </html>
        """
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                json=email_data,
                headers={
                    "api-key": brevo_api_key,
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 201:
                print("✅ Test email sent successfully!")
                return True
            else:
                print("❌ Test email failed")
                return False
                
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(send_test_email())