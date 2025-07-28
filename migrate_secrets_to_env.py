#!/usr/bin/env python3
"""
Migration Script: Move API Keys from Secrets to .env
This script helps you copy API keys from Replit secrets to your .env file
"""

import os
import sys
from dotenv import load_dotenv, set_key

def migrate_secrets_to_env():
    """Migrate API keys from environment/secrets to .env file"""
    
    print("🔄 Migrating API keys from secrets to .env file...")
    
    # Load existing .env file
    load_dotenv()
    
    # Define the API keys we need to migrate
    api_keys_to_migrate = {
        'TELEGRAM_BOT_TOKEN': 'Your Telegram bot token from @BotFather',
        'OPENPROVIDER_USERNAME': 'Your OpenProvider username',
        'OPENPROVIDER_PASSWORD': 'Your OpenProvider password',
        'CLOUDFLARE_API_TOKEN': 'Your Cloudflare API token',
        'FASTFOREX_API_KEY': 'Your FastForex API key',
        'BLOCKBEE_API_KEY': 'Your BlockBee API key',
        'DATABASE_URL': 'Your PostgreSQL database URL',
    }
    
    env_file_path = '.env'
    updated_keys = []
    missing_keys = []
    
    for key, description in api_keys_to_migrate.items():
        # Try to get the value from current environment (secrets)
        value = os.getenv(key)
        
        if value and value != f'your_{key.lower()}_here':
            # Update .env file with the real value
            set_key(env_file_path, key, value)
            updated_keys.append(key)
            print(f"✅ Migrated {key}")
        else:
            missing_keys.append((key, description))
            print(f"⚠️  Missing {key}")
    
    print(f"\n📊 Migration Summary:")
    print(f"✅ Successfully migrated: {len(updated_keys)} keys")
    print(f"⚠️  Missing keys: {len(missing_keys)} keys")
    
    if updated_keys:
        print(f"\n✅ Migrated keys:")
        for key in updated_keys:
            print(f"   - {key}")
    
    if missing_keys:
        print(f"\n⚠️  You still need to add these keys to your .env file:")
        for key, description in missing_keys:
            print(f"   - {key}: {description}")
    
    print(f"\n📝 Next steps:")
    print(f"1. Check your .env file - the existing keys have been updated")
    print(f"2. Add any missing API keys manually to .env")
    print(f"3. Remove the keys from Replit secrets once everything works")
    print(f"4. Restart your bot to use the .env configuration")
    
    return len(missing_keys) == 0

def check_env_file():
    """Check if .env file has all required keys"""
    print("\n🔍 Checking .env file configuration...")
    
    load_dotenv()
    
    required_keys = [
        'TELEGRAM_BOT_TOKEN',
        'DATABASE_URL',
        'OPENPROVIDER_USERNAME', 
        'OPENPROVIDER_PASSWORD',
        'CLOUDFLARE_API_TOKEN'
    ]
    
    missing = []
    placeholder = []
    valid = []
    
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            missing.append(key)
        elif 'your_' in value and '_here' in value:
            placeholder.append(key)
        else:
            valid.append(key)
    
    print(f"✅ Valid keys: {len(valid)}")
    print(f"📝 Placeholder keys: {len(placeholder)}")
    print(f"❌ Missing keys: {len(missing)}")
    
    if valid:
        print(f"\n✅ Keys with real values:")
        for key in valid:
            print(f"   - {key}")
    
    if placeholder:
        print(f"\n📝 Keys with placeholder values (need real values):")
        for key in placeholder:
            print(f"   - {key}")
    
    if missing:
        print(f"\n❌ Missing keys:")
        for key in missing:
            print(f"   - {key}")
    
    return len(missing) == 0 and len(placeholder) == 0

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 NOMADLY2 API KEYS MIGRATION")
    print("=" * 60)
    
    # First, try to migrate from secrets
    migrate_success = migrate_secrets_to_env()
    
    # Then check the final state
    config_complete = check_env_file()
    
    if config_complete:
        print(f"\n🎉 All API keys are properly configured in .env!")
        print(f"✅ Your app is ready to use .env instead of secrets")
    else:
        print(f"\n⚠️  Configuration incomplete")
        print(f"📝 Please add the missing API keys to .env manually")