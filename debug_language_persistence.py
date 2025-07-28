#!/usr/bin/env python3
"""
Debug script to test language persistence thoroughly
"""

import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_session_loading():
    """Test actual session loading behavior"""
    try:
        # Import and create bot instance to test actual behavior
        from nomadly3_clean_bot import NomadlyCleanBot
        
        logger.info("Creating bot instance...")
        bot = NomadlyCleanBot()
        
        # Test with real user ID from sessions file
        test_user_id = 5590563715
        
        logger.info(f"Testing with user ID: {test_user_id}")
        logger.info(f"User sessions loaded: {len(bot.user_sessions)}")
        logger.info(f"Session data for user {test_user_id}:")
        
        if test_user_id in bot.user_sessions:
            session = bot.user_sessions[test_user_id]
            logger.info(f"  - Language: {session.get('language', 'NOT SET')}")
            logger.info(f"  - Keys in session: {list(session.keys())}")
            
            # Test the exact condition from start_command
            has_language = "language" in session
            logger.info(f"  - Has language key: {has_language}")
            
            if has_language:
                logger.info(f"✅ Language persistence should work for user {test_user_id}")
                return True
            else:
                logger.error(f"❌ Language key missing in session for user {test_user_id}")
                return False
        else:
            logger.error(f"❌ User {test_user_id} not found in loaded sessions")
            return False
            
    except Exception as e:
        logger.error(f"Error testing session loading: {e}")
        return False

def simulate_start_command_logic():
    """Simulate the exact logic from start_command"""
    try:
        from nomadly3_clean_bot import NomadlyCleanBot
        
        bot = NomadlyCleanBot()
        test_user_id = 5590563715
        
        logger.info("Simulating start_command logic...")
        
        # Exact same check as in start_command
        if test_user_id in bot.user_sessions and "language" in bot.user_sessions[test_user_id]:
            saved_language = bot.user_sessions[test_user_id]["language"]
            logger.info(f"✅ Condition passed - saved language: {saved_language}")
            logger.info("Should show main menu in French")
            return True
        else:
            logger.error("❌ Condition failed - would show language selection")
            logger.info(f"  - User in sessions: {test_user_id in bot.user_sessions}")
            if test_user_id in bot.user_sessions:
                logger.info(f"  - Language in session: {'language' in bot.user_sessions[test_user_id]}")
                logger.info(f"  - Session keys: {list(bot.user_sessions[test_user_id].keys())}")
            return False
            
    except Exception as e:
        logger.error(f"Error simulating start command: {e}")
        return False

def main():
    logger.info("🔍 Debug Language Persistence")
    logger.info("=" * 40)
    
    # Test 1: Raw file check
    logger.info("Test 1: Raw session file check")
    if os.path.exists('user_sessions.json'):
        with open('user_sessions.json', 'r') as f:
            sessions = json.load(f)
            logger.info(f"Raw file content: {json.dumps(sessions, indent=2)}")
    
    # Test 2: Session loading
    logger.info("\nTest 2: Session loading test")
    loading_works = test_session_loading()
    
    # Test 3: Start command simulation
    logger.info("\nTest 3: Start command logic simulation")
    start_logic_works = simulate_start_command_logic()
    
    logger.info("\n" + "=" * 40)
    if loading_works and start_logic_works:
        logger.info("✅ All tests passed - language persistence should work")
    else:
        logger.error("❌ Issues found with language persistence")
        
    return loading_works and start_logic_works

if __name__ == "__main__":
    main()