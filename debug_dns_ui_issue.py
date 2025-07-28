#!/usr/bin/env python3
"""
Debug DNS UI issue - simulate user interaction to identify problems
"""

import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simulate_dns_edit_click():
    """Simulate user clicking edit DNS record button"""
    print("🔍 SIMULATING DNS EDIT BUTTON CLICK")
    print("=" * 40)
    
    try:
        # Import the bot class
        from nomadly3_clean_bot import NomadlyCleanBot
        
        # Create bot instance
        bot = NomadlyCleanBot()
        
        # Mock query object like Telegram would send
        mock_query = MagicMock()
        mock_query.from_user.id = 5590563715
        mock_query.edit_message_text = AsyncMock()
        mock_query.answer = AsyncMock()
        
        print("1. Testing DNS Records List Generation...")
        # First test: show edit DNS records list
        await bot.show_edit_dns_records_list(mock_query, "claudeb_sbs")
        
        if mock_query.edit_message_text.called:
            print("   ✅ Edit DNS records list generated")
            call_args = mock_query.edit_message_text.call_args
            message_text = call_args[0][0] if call_args and len(call_args[0]) > 0 else "No message"
            print(f"   Message preview: {message_text[:100]}...")
            
            # Extract buttons from reply markup
            if len(call_args) > 1 and 'reply_markup' in call_args[1]:
                keyboard = call_args[1]['reply_markup']
                if hasattr(keyboard, 'inline_keyboard'):
                    buttons = keyboard.inline_keyboard
                    print(f"   Found {len(buttons)} buttons")
                    
                    if buttons and len(buttons) > 0:
                        # Test clicking the first edit button
                        first_button = buttons[0][0] if len(buttons[0]) > 0 else None
                        if first_button:
                            callback_data = first_button.callback_data
                            print(f"   First button callback: {callback_data}")
                            
                            print("\n2. Testing Edit Button Callback...")
                            # Reset mock
                            mock_query.edit_message_text.reset_mock()
                            
                            # Simulate callback processing
                            await bot.handle_callback_query_logic(mock_query, callback_data)
                            
                            if mock_query.edit_message_text.called:
                                print("   ✅ Edit button callback processed successfully")
                                edit_call_args = mock_query.edit_message_text.call_args
                                edit_message = edit_call_args[0][0] if edit_call_args and len(edit_call_args[0]) > 0 else "No edit message"
                                print(f"   Edit response: {edit_message[:150]}...")
                            else:
                                print("   ❌ Edit button callback failed - no response generated")
                        else:
                            print("   ❌ No first button found")
                    else:
                        print("   ❌ No buttons found in keyboard")
                else:
                    print("   ❌ No inline keyboard found")
            else:
                print("   ❌ No reply markup found")
        else:
            print("   ❌ Edit DNS records list failed to generate")
            
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

async def main():
    """Main test function"""
    await simulate_dns_edit_click()
    
    print("\n📊 DIAGNOSIS COMPLETE")
    print("=" * 30)
    print("If all tests pass, the issue might be:")
    print("• Session state management during edits")
    print("• Real-time DNS record synchronization")
    print("• User permission or authentication issues")
    print("• Network connectivity to Cloudflare API")

if __name__ == "__main__":
    asyncio.run(main())