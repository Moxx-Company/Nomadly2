#!/usr/bin/env python3
"""
Test the start command directly to see what's happening
"""

import asyncio
import logging
from datetime import datetime

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_start_command():
    """Test start command behavior directly"""
    try:
        from nomadly3_clean_bot import NomadlyCleanBot
        from telegram import Update, User, Message
        
        # Create bot instance
        logger.info("Creating bot instance...")
        bot = NomadlyCleanBot()
        
        # Check current sessions
        logger.info(f"Sessions loaded: {len(bot.user_sessions)}")
        for user_id, session in bot.user_sessions.items():
            logger.info(f"User {user_id}: {session.get('language', 'NO LANGUAGE')}")
        
        # Create mock update object for testing
        test_user_id = 5590563715
        
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
                self.username = "testuser"
                self.first_name = "Test"
        
        class MockMessage:
            def __init__(self, user):
                self.from_user = user
                
            async def reply_text(self, text, **kwargs):
                logger.info(f"BOT WOULD SEND: {text}")
        
        class MockUpdate:
            def __init__(self, user_id):
                self.effective_user = MockUser(user_id)
                self.message = MockMessage(self.effective_user)
        
        # Test start command
        logger.info(f"Testing start command for user {test_user_id}...")
        update = MockUpdate(test_user_id)
        
        # Call the actual start command
        await bot.start_command(update, None)
        
        logger.info("Start command test completed")
        
    except Exception as e:
        logger.error(f"Error testing start command: {e}")
        import traceback
        traceback.print_exc()

def main():
    logger.info("🧪 Testing Start Command Directly")
    logger.info("=" * 50)
    
    # Run the async test
    asyncio.run(test_start_command())

if __name__ == "__main__":
    main()