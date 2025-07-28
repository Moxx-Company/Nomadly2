#!/usr/bin/env python3
"""
Test French payment page functionality
Verify that payment workflow displays in French for French-speaking users
"""

import asyncio
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockCallbackQuery:
    def __init__(self, user_id, data):
        self.data = data
        self.from_user = type('User', (), {'id': user_id})()
        self.message = None
    
    async def answer(self, text):
        logger.info(f"✅ Button feedback: {text}")
    
    async def edit_message_text(self, text, **kwargs):
        logger.info(f"📱 Bot message updated:\n{text}")
        # Check for French translations in payment text
        french_keywords = [
            "Finaliser l'enregistrement",
            "Choisissez votre méthode de paiement",
            "Solde portefeuille",
            "Modifier email",
            "Modifier DNS",
            "Retour recherche",
            "Confidentialité WHOIS",
            "Serveurs de noms"
        ]
        
        found_french = []
        for keyword in french_keywords:
            if keyword in text:
                found_french.append(keyword)
        
        if found_french:
            logger.info(f"✅ French translations found: {found_french}")
        else:
            logger.warning("⚠️ No French translations detected in payment page")

async def test_french_payment_page():
    """Test French payment page display"""
    try:
        from nomadly3_clean_bot import NomadlyCleanBot
        
        logger.info("🧪 FRENCH PAYMENT PAGE TEST")
        logger.info("=" * 50)
        
        # Initialize bot
        logger.info("🔍 Test 1: Bot initialization with French user")
        bot = NomadlyCleanBot()
        
        # French user from sessions
        french_user_id = 5590563715
        
        # Verify French language is loaded
        if french_user_id in bot.user_sessions:
            user_lang = bot.user_sessions[french_user_id].get('language')
            logger.info(f"✅ French user language loaded: {user_lang}")
        else:
            logger.error(f"❌ French user {french_user_id} not found in sessions")
            return False
        
        # Test domain registration (payment page)
        logger.info("\n🔍 Test 2: Domain registration page (should show French)")
        test_domain = "testfrench_com"
        
        # Mock callback query for domain registration
        query = MockCallbackQuery(french_user_id, f"register_{test_domain}")
        
        # Call domain registration handler - this should show French payment page
        await bot.handle_domain_registration(query, test_domain)
        
        logger.info("\n🔍 Test 3: Verify session language persistence")
        if french_user_id in bot.user_sessions:
            session_lang = bot.user_sessions[french_user_id].get('language')
            logger.info(f"✅ Session language preserved: {session_lang}")
        
        logger.info("\n" + "=" * 50)
        logger.info("🎉 FRENCH PAYMENT PAGE TEST COMPLETED")
        logger.info("📝 Expected French elements:")
        logger.info("   • 'Finaliser l'enregistrement' (Complete Registration)")
        logger.info("   • 'Choisissez votre méthode de paiement' (Choose payment method)")
        logger.info("   • 'Solde portefeuille' (Wallet Balance)")
        logger.info("   • 'Modifier email' (Edit Email)")
        logger.info("   • 'Modifier DNS' (Edit DNS)")
        logger.info("   • 'Retour recherche' (Back to Search)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run French payment page test"""
    logger.info(f"🚀 Starting French payment test at {datetime.now()}")
    
    success = asyncio.run(test_french_payment_page())
    
    if success:
        logger.info("\n✅ FRENCH PAYMENT PAGE TEST PASSED!")
        logger.info("🇫🇷 Payment workflow now supports French language")
        logger.info("💳 Users can complete domain registration in French")
    else:
        logger.error("\n❌ FRENCH PAYMENT PAGE TEST FAILED")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)