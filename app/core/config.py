"""
Core configuration management for Nomadly3 Domain Registration Bot
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    PGHOST: str = os.getenv("PGHOST", "localhost")
    PGPORT: str = os.getenv("PGPORT", "5432")
    PGDATABASE: str = os.getenv("PGDATABASE", "nomadly")
    PGUSER: str = os.getenv("PGUSER", "postgres")
    PGPASSWORD: str = os.getenv("PGPASSWORD", "")
    
    # OpenProvider API Configuration
    OPENPROVIDER_USERNAME: str = os.getenv("OPENPROVIDER_USERNAME", "")
    OPENPROVIDER_PASSWORD: str = os.getenv("OPENPROVIDER_PASSWORD", "")
    OPENPROVIDER_API_URL: str = os.getenv("OPENPROVIDER_API_URL", "https://api.openprovider.eu")
    
    # Cloudflare API Configuration
    CLOUDFLARE_API_TOKEN: str = os.getenv("CLOUDFLARE_API_TOKEN", "")
    CLOUDFLARE_API_URL: str = os.getenv("CLOUDFLARE_API_URL", "https://api.cloudflare.com/client/v4")
    
    # BlockBee Payment Configuration
    BLOCKBEE_API_KEY: str = os.getenv("BLOCKBEE_API_KEY", "")
    BLOCKBEE_API_URL: str = os.getenv("BLOCKBEE_API_URL", "https://api.blockbee.io")
    
    # FastForex Currency API
    FASTFOREX_API_KEY: str = os.getenv("FASTFOREX_API_KEY", "")
    FASTFOREX_API_URL: str = os.getenv("FASTFOREX_API_URL", "https://api.fastforex.io")
    
    # Brevo Email Service
    BREVO_API_KEY: str = os.getenv("BREVO_API_KEY", "")
    BREVO_SMTP_KEY: str = os.getenv("BREVO_SMTP_KEY", "")
    BREVO_API_URL: str = os.getenv("BREVO_API_URL", "https://api.brevo.com/v3")
    
    # Application Settings
    APP_NAME: str = "Nomadly3 Domain Bot"
    APP_VERSION: str = "1.4.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Offshore Pricing
    OFFSHORE_MULTIPLIER: float = float(os.getenv("OFFSHORE_MULTIPLIER", "3.3"))
    
    # Webhook Configuration
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
    
    # Default Language
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "DATABASE_URL",
            "OPENPROVIDER_USERNAME",
            "OPENPROVIDER_PASSWORD",
            "CLOUDFLARE_API_TOKEN",
            "BLOCKBEE_API_KEY",
            "FASTFOREX_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Global config instance
config = Config()