#!/usr/bin/env python3
"""
Generate .env template with current secrets
This helps you create a complete .env file with your actual API keys
"""

import os

def generate_env_template():
    """Generate .env file template with current secret values"""
    
    print("📝 Generating .env template with your current API keys...")
    
    # Read current secrets
    secrets = {
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'ADMIN_CHAT_ID': '5590563715',
        'OPENPROVIDER_USERNAME': os.getenv('OPENPROVIDER_USERNAME'),
        'OPENPROVIDER_PASSWORD': os.getenv('OPENPROVIDER_PASSWORD'),
        'CLOUDFLARE_API_TOKEN': os.getenv('CLOUDFLARE_API_TOKEN'),
        'CLOUDFLARE_EMAIL': os.getenv('CLOUDFLARE_EMAIL'),
        'BLOCKBEE_API_KEY': os.getenv('BLOCKBEE_API_KEY') or 'get_from_blockbee_io',
        'FASTFOREX_API_KEY': os.getenv('FASTFOREX_API_KEY'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
    }
    
    env_content = """# Nomadly2 Environment Configuration
# Generated from your current secrets

# ================================
# TELEGRAM CONFIGURATION  
# ================================
TELEGRAM_BOT_TOKEN={TELEGRAM_BOT_TOKEN}
ADMIN_CHAT_ID={ADMIN_CHAT_ID}

# ================================
# OPENPROVIDER DOMAIN REGISTRATION
# ================================
OPENPROVIDER_USERNAME={OPENPROVIDER_USERNAME}
OPENPROVIDER_PASSWORD={OPENPROVIDER_PASSWORD}

# ================================
# CLOUDFLARE DNS MANAGEMENT
# ================================
CLOUDFLARE_API_TOKEN={CLOUDFLARE_API_TOKEN}
CLOUDFLARE_EMAIL={CLOUDFLARE_EMAIL}

# ================================
# CRYPTOCURRENCY PAYMENTS
# ================================
BLOCKBEE_API_KEY={BLOCKBEE_API_KEY}

# ================================
# CURRENCY CONVERSION
# ================================
FASTFOREX_API_KEY={FASTFOREX_API_KEY}

# ================================
# DATABASE
# ================================
DATABASE_URL={DATABASE_URL}

# ================================
# EMAIL CONFIGURATION
# ================================
FALLBACK_CONTACT_EMAIL=privacy@nomadly.com
SENDER_EMAIL=noreply@nomadly.com
SUPPORT_EMAIL=support@nomadly.com

# ================================
# COMPANY BRANDING
# ================================
COMPANY_NAME=Nomadly
COMPANY_DOMAIN=nomadly.com
WEBSITE_URL=https://nomadly.com

# ================================
# DEFAULT NAMESERVERS
# ================================
DEFAULT_NS1=ns1.privatehoster.cc
DEFAULT_NS2=ns2.privatehoster.cc

# ================================
# PRICING CONFIGURATION
# ================================
DEFAULT_DOMAIN_PRICE=9.87
PRICE_MULTIPLIER=3.3
CURRENCY=USD

# ================================
# DEVELOPMENT/TESTING
# ================================
DEBUG_MODE=false
TEST_USER_ID=5590563715

# ================================
# WEBHOOK CONFIGURATION
# ================================
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000
""".format(**{k: v or f'ADD_YOUR_{k}_HERE' for k, v in secrets.items()})

    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Generated .env file with your current API keys!")
    
    # Show status
    valid_keys = [k for k, v in secrets.items() if v and v != 'get_from_blockbee_io']
    missing_keys = [k for k, v in secrets.items() if not v or v == 'get_from_blockbee_io']
    
    print(f"\n📊 Status:")
    print(f"✅ Keys with values: {len(valid_keys)}")
    print(f"⚠️  Keys needing values: {len(missing_keys)}")
    
    if missing_keys:
        print(f"\n⚠️  You need to add these keys to .env:")
        for key in missing_keys:
            if key == 'BLOCKBEE_API_KEY':
                print(f"   - {key}: Get from blockbee.io")
            else:
                print(f"   - {key}: Add your API key")

if __name__ == "__main__":
    generate_env_template()