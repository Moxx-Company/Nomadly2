#!/usr/bin/env python3
"""
Verify BlockBee API integration is properly configured
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_blockbee_integration():
    """Check if BlockBee API is properly configured"""
    logger.info("🔍 Checking BlockBee API Integration...")
    
    # Check environment variable
    blockbee_key = os.getenv('BLOCKBEE_API_KEY')
    
    if blockbee_key:
        logger.info(f"✅ BlockBee API Key found: {blockbee_key[:10]}...{blockbee_key[-10:]}")
        logger.info(f"   Full key length: {len(blockbee_key)} characters")
        
        # Check if it matches the expected format
        if len(blockbee_key) >= 50:
            logger.info("✅ API key format appears valid (50+ characters)")
            return True
        else:
            logger.warning("⚠️ API key seems too short for BlockBee")
            return False
    else:
        logger.error("❌ BLOCKBEE_API_KEY not found in environment")
        return False

def check_env_file():
    """Check .env file content"""
    logger.info("📄 Checking .env file...")
    
    try:
        with open('.env', 'r') as f:
            content = f.read()
            
        if 'BLOCKBEE_API_KEY=' in content:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('BLOCKBEE_API_KEY='):
                    key_value = line.split('=', 1)[1]
                    logger.info(f"✅ Found in .env: BLOCKBEE_API_KEY={key_value[:10]}...{key_value[-10:]}")
                    return True
        else:
            logger.error("❌ BLOCKBEE_API_KEY not found in .env file")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error reading .env file: {e}")
        return False

def main():
    """Main verification"""
    logger.info("🚀 BlockBee Integration Verification")
    logger.info("=" * 50)
    
    env_file_ok = check_env_file()
    env_var_ok = check_blockbee_integration()
    
    logger.info("\n" + "=" * 50)
    logger.info("VERIFICATION RESULTS")
    logger.info("=" * 50)
    
    logger.info(f".env file: {'✅ FOUND' if env_file_ok else '❌ MISSING'}")
    logger.info(f"Environment variable: {'✅ LOADED' if env_var_ok else '❌ NOT LOADED'}")
    
    if env_file_ok and env_var_ok:
        logger.info("\n🎯 BlockBee API integration is properly configured!")
        return True
    elif env_file_ok and not env_var_ok:
        logger.info("\n⚠️ API key in .env but not loaded. Restart may be needed.")
        return False
    else:
        logger.info("\n❌ BlockBee API configuration needs attention")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)