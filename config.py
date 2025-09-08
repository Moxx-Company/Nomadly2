"""
Configuration management for Nomadly2 Bot
Centralizes environment variables and configuration settings
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file (override system environment)
load_dotenv(override=True)


class Config:
    """Centralized configuration for the bot"""

    # API Credentials
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
    OPENPROVIDER_USERNAME = os.getenv("OPENPROVIDER_USERNAME")
    OPENPROVIDER_PASSWORD = os.getenv("OPENPROVIDER_PASSWORD")
    CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    CLOUDFLARE_EMAIL = os.getenv("CLOUDFLARE_EMAIL")
    CLOUDFLARE_GLOBAL_API_KEY = os.getenv("CLOUDFLARE_GLOBAL_API_KEY")
    BLOCKBEE_API_KEY = os.getenv("BLOCKBEE_API_KEY")
    FASTFOREX_API_KEY = os.getenv("FASTFOREX_API_KEY")
    
    # Payment Gateway Configuration
    PAYMENT_GATEWAY = os.getenv("PAYMENT_GATEWAY", "blockbee").lower()
    DYNOPAY_API_KEY = os.getenv("DYNOPAY_API_KEY")
    DYNOPAY_TOKEN = os.getenv("DYNOPAY_TOKEN")
    
    # Email Service (Brevo)
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    BREVO_SMTP_KEY = os.getenv("BREVO_SMTP_KEY")
    BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "noreply@cloakhost.ru")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Email Configuration
    FALLBACK_CONTACT_EMAIL = os.getenv("FALLBACK_CONTACT_EMAIL", "cloakhost@tutamail.com")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@nomadly.com")
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@nomadly.com")

    # Branding & URLs
    COMPANY_NAME = os.getenv("COMPANY_NAME", "Nomadly")
    COMPANY_DOMAIN = os.getenv("COMPANY_DOMAIN", "nomadly.com")
    WEBSITE_URL = os.getenv("WEBSITE_URL", "https://nomadly.com")

    # Default Nameservers
    DEFAULT_CUSTOM_NAMESERVERS = [
        os.getenv("DEFAULT_NS1", "ns1.privatehoster.cc"),
        os.getenv("DEFAULT_NS2", "ns2.privatehoster.cc"),
    ]

    DEFAULT_REGISTRAR_NAMESERVERS = [
        "ns1.openprovider.nl",
        "ns2.openprovider.be",
        "ns3.openprovider.eu",
    ]

    # Pricing Configuration
    DEFAULT_DOMAIN_PRICE = float(os.getenv("DEFAULT_DOMAIN_PRICE", "9.87"))  # Updated to reflect 3.3x multiplier ($2.99 * 3.3 = $9.87)
    PRICE_MULTIPLIER = float(os.getenv("PRICE_MULTIPLIER", "3.3"))  # 3.3x markup on API prices
    CURRENCY = os.getenv("CURRENCY", "USD")

    # Server Configuration
    SERVER_PUBLIC_IP = os.getenv("SERVER_PUBLIC_IP")
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8000"))

    # Development/Testing
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    TEST_USER_ID = int(os.getenv("TEST_USER_ID", "5590563715"))
    
    # Additional Services (Optional)
    WHCMS_API_URL = os.getenv("WHCMS_API_URL")
    WHCMS_API_KEY = os.getenv("WHCMS_API_KEY")
    WHCMS_API_SECRET = os.getenv("WHCMS_API_SECRET")
    
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

    @classmethod
    def get_email_config(cls) -> Dict[str, str]:
        """Get email configuration"""
        return {
            "fallback": cls.FALLBACK_CONTACT_EMAIL,
            "sender": cls.SENDER_EMAIL,
            "support": cls.SUPPORT_EMAIL,
        }

    @classmethod
    def get_nameserver_config(cls) -> Dict[str, List[str]]:
        """Get nameserver configuration"""
        return {
            "custom_default": cls.DEFAULT_CUSTOM_NAMESERVERS,
            "registrar_default": cls.DEFAULT_REGISTRAR_NAMESERVERS,
        }

    @classmethod
    def validate_required_config(cls) -> List[str]:
        """Validate required configuration and return missing items"""
        missing = []
        required_vars = [
            ("TELEGRAM_BOT_TOKEN", cls.TELEGRAM_BOT_TOKEN),
            ("DATABASE_URL", cls.DATABASE_URL),
            ("OPENPROVIDER_USERNAME", cls.OPENPROVIDER_USERNAME),
            ("OPENPROVIDER_PASSWORD", cls.OPENPROVIDER_PASSWORD),
        ]

        for var_name, var_value in required_vars:
            if not var_value:
                missing.append(var_name)

        return missing

    @classmethod
    def validate_payment_gateway_config(cls) -> Dict[str, Any]:
        """Validate payment gateway configuration and return status"""
        # Get fresh values from environment
        payment_gateway = os.getenv("PAYMENT_GATEWAY", "blockbee").lower()
        dynopay_api_key = os.getenv("DYNOPAY_API_KEY")
        dynopay_token = os.getenv("DYNOPAY_TOKEN")
        blockbee_api_key = os.getenv("BLOCKBEE_API_KEY")
        
        validation_result = {
            "is_valid": True,
            "gateway": payment_gateway,
            "missing_vars": [],
            "warnings": [],
            "message": ""
        }
        
        # Check if PAYMENT_GATEWAY is explicitly set
        payment_gateway_env = os.getenv("PAYMENT_GATEWAY")
        if not payment_gateway_env:
            validation_result["is_valid"] = False
            validation_result["missing_vars"].append("PAYMENT_GATEWAY")
            validation_result["message"] = "❌ PAYMENT_GATEWAY environment variable is required but not set!"
            return validation_result
        
        # Validate DynoPay configuration if selected
        if payment_gateway == "dynopay":
            if not dynopay_api_key:
                validation_result["is_valid"] = False
                validation_result["missing_vars"].append("DYNOPAY_API_KEY")
                validation_result["message"] = "❌ DynoPay selected but DYNOPAY_API_KEY is not set!"
            elif not dynopay_token:
                validation_result["is_valid"] = False
                validation_result["missing_vars"].append("DYNOPAY_TOKEN")
                validation_result["message"] = "❌ DynoPay selected but DYNOPAY_TOKEN is not set!"
            else:
                validation_result["message"] = "✅ DynoPay configuration is valid"
        
        # Validate BlockBee configuration if selected
        elif payment_gateway == "blockbee":
            if not blockbee_api_key:
                validation_result["is_valid"] = False
                validation_result["missing_vars"].append("BLOCKBEE_API_KEY")
                validation_result["message"] = "❌ BlockBee selected but BLOCKBEE_API_KEY is not set!"
            else:
                validation_result["message"] = "✅ BlockBee configuration is valid"
        
        # Handle unknown payment gateway
        else:
            validation_result["is_valid"] = False
            validation_result["warnings"].append(f"Unknown payment gateway: {payment_gateway}")
            validation_result["message"] = f"❌ Unknown payment gateway: {payment_gateway}. Supported: dynopay, blockbee"
        
        return validation_result


def get_server_ip() -> str:
    """Get server IP address for A records"""
    return Config.SERVER_PUBLIC_IP or "93.184.216.34"  # Example IP fallback


def send_payment_gateway_error_message(bot, chat_id: int) -> None:
    """Send payment gateway configuration error message to user"""
    try:
        validation = Config.validate_payment_gateway_config()
        
        if not validation["is_valid"]:
            error_message = f"""
🚨 **Payment Gateway Configuration Error**

{validation['message']}

**Missing Environment Variables:**
{chr(10).join(f"• {var}" for var in validation['missing_vars'])}

**Required Setup:**
1. Set `PAYMENT_GATEWAY` in your `.env` file
2. Choose either:
   - `PAYMENT_GATEWAY=dynopay` (requires `DYNOPAY_API_KEY` and `DYNOPAY_TOKEN`)
   - `PAYMENT_GATEWAY=blockbee` (requires `BLOCKBEE_API_KEY`)

**Example .env configuration:**
```
PAYMENT_GATEWAY=dynopay
DYNOPAY_API_KEY=your_api_key_here
DYNOPAY_TOKEN=your_token_here
```

Please contact the administrator to fix this configuration issue.
            """
            
            bot.send_message(
                chat_id=chat_id,
                text=error_message,
                parse_mode='Markdown'
            )
            
    except Exception as e:
        # Fallback error message if bot is not available
        print(f"❌ Payment Gateway Configuration Error: {e}")
        print(f"❌ {validation.get('message', 'Unknown configuration error')}")


# Configuration instance
config = Config()
