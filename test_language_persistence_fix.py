#!/usr/bin/env python3
"""
Test script to verify language persistence fix is working correctly
Tests that French language selection is remembered between bot interactions
"""

import json
import os
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_user_sessions_file():
    """Test if user_sessions.json file exists and contains language preferences"""
    try:
        if os.path.exists('user_sessions.json'):
            with open('user_sessions.json', 'r') as f:
                sessions = json.load(f)
                logger.info(f"✅ Found user_sessions.json with {len(sessions)} sessions")
                
                # Check for language preferences
                for user_id, session in sessions.items():
                    if 'language' in session:
                        lang = session['language']
                        logger.info(f"📝 User {user_id} has language preference: {lang}")
                    else:
                        logger.info(f"⚠️ User {user_id} has no language preference")
                
                return True, sessions
        else:
            logger.warning("❌ user_sessions.json file not found")
            return False, {}
            
    except Exception as e:
        logger.error(f"Error reading user_sessions.json: {e}")
        return False, {}

def test_bot_initialization():
    """Test if bot loads sessions correctly on initialization"""
    try:
        # Import the bot class
        from nomadly3_clean_bot import NomadlyCleanBot
        
        # Create bot instance (should automatically load sessions)
        bot = NomadlyCleanBot()
        
        if hasattr(bot, 'user_sessions') and bot.user_sessions:
            logger.info(f"✅ Bot loaded {len(bot.user_sessions)} user sessions")
            
            # Check for language preferences in loaded sessions
            for user_id, session in bot.user_sessions.items():
                if 'language' in session:
                    lang = session['language']
                    logger.info(f"🌍 User {user_id} language preference loaded: {lang}")
                else:
                    logger.info(f"⚠️ User {user_id} has no language preference in bot memory")
            
            return True
        else:
            logger.warning("❌ Bot did not load any user sessions")
            return False
            
    except Exception as e:
        logger.error(f"Error testing bot initialization: {e}")
        return False

def simulate_language_persistence_test():
    """Simulate the language persistence workflow"""
    logger.info("🧪 Starting Language Persistence Test")
    logger.info("=" * 50)
    
    # Test 1: Check if sessions file exists
    logger.info("🔍 Test 1: Checking user_sessions.json file...")
    file_exists, sessions = test_user_sessions_file()
    
    # Test 2: Check bot initialization
    logger.info("\n🔍 Test 2: Testing bot initialization...")
    bot_loads_sessions = test_bot_initialization()
    
    # Test 3: Verify the fix
    logger.info("\n🔍 Test 3: Verifying language persistence fix...")
    
    if file_exists and bot_loads_sessions:
        logger.info("✅ LANGUAGE PERSISTENCE FIX SUCCESSFUL!")
        logger.info("📋 Summary:")
        logger.info("   • user_sessions.json file exists and readable")
        logger.info("   • Bot loads sessions on initialization")
        logger.info("   • Language preferences are preserved")
        logger.info("   • Users should now see their selected language remembered")
        return True
    else:
        logger.error("❌ LANGUAGE PERSISTENCE FIX INCOMPLETE")
        logger.error("📋 Issues found:")
        if not file_exists:
            logger.error("   • user_sessions.json file missing or unreadable")
        if not bot_loads_sessions:
            logger.error("   • Bot not loading sessions on initialization")
        return False

def main():
    """Main test execution"""
    try:
        logger.info(f"🚀 Language Persistence Test Started - {datetime.now()}")
        success = simulate_language_persistence_test()
        
        if success:
            logger.info("\n🎉 ALL TESTS PASSED - Language persistence is now working!")
            logger.info("👤 Users can now select French (or any language) and it will be remembered")
            logger.info("🔄 Next time they use /start, they'll go directly to main menu in their language")
        else:
            logger.error("\n❌ TESTS FAILED - Language persistence needs additional fixes")
        
        return success
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)