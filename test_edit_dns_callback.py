#!/usr/bin/env python3
"""
Test the actual edit DNS callback that users are experiencing
"""

import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_edit_dns_callback():
    """Test the exact callback that was generated"""
    print("🧪 TESTING EXACT DNS EDIT CALLBACK")
    print("=" * 50)
    
    # The exact callback from the debug output
    test_callback = "edit_dns_e40f36f424fbb4e1a1cdaaa39bc78d94_claudeb_sbs"
    
    print(f"Testing callback: {test_callback}")
    
    # Test the parsing logic manually
    if test_callback.startswith("edit_dns_"):
        callback_part = test_callback.replace("edit_dns_", "")
        print(f"Callback part: {callback_part}")
        
        # This is the logic from the bot
        parts = callback_part.rsplit("_", 2)  # Split into max 3 parts from right
        print(f"Parts: {parts}")
        
        if len(parts) >= 3:
            record_id = parts[0]
            domain = f"{parts[1]}.{parts[2]}"
            print(f"✅ Parsed successfully:")
            print(f"   Record ID: {record_id}")
            print(f"   Domain: {domain}")
            
            # Now test the actual bot function
            try:
                from nomadly3_clean_bot import NomadlyCleanBot
                
                bot = NomadlyCleanBot()
                
                # Create mock query
                mock_query = MagicMock()
                mock_query.from_user.id = 5590563715
                mock_query.edit_message_text = AsyncMock()
                mock_query.answer = AsyncMock()
                
                print("\n🔧 Testing handle_edit_dns_record function...")
                await bot.handle_edit_dns_record(mock_query, record_id, domain)
                
                if mock_query.edit_message_text.called:
                    print("✅ Edit DNS record handler completed successfully!")
                    call_args = mock_query.edit_message_text.call_args
                    if call_args and len(call_args[0]) > 0:
                        message = call_args[0][0]
                        print(f"Response message: {message[:200]}...")
                    else:
                        print("No message content found")
                else:
                    print("❌ Edit DNS record handler did not respond")
                    
            except Exception as e:
                print(f"❌ Error testing bot function: {e}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
        
        elif len(parts) == 2:
            record_id = parts[0]
            domain = parts[1].replace('_', '.')
            print(f"✅ Parsed with fallback:")
            print(f"   Record ID: {record_id}")
            print(f"   Domain: {domain}")
        else:
            print(f"❌ Parsing failed: Expected at least 2 parts, got {len(parts)}")

async def test_delete_dns_functionality():
    """Test delete DNS functionality as well"""
    print("\n🗑️ TESTING DELETE DNS FUNCTIONALITY")
    print("=" * 40)
    
    try:
        from nomadly3_clean_bot import NomadlyCleanBot
        
        bot = NomadlyCleanBot()
        
        # Create mock query
        mock_query = MagicMock()
        mock_query.from_user.id = 5590563715
        mock_query.edit_message_text = AsyncMock()
        mock_query.answer = AsyncMock()
        
        print("Testing delete DNS records list generation...")
        await bot.show_delete_dns_records_list(mock_query, "claudeb_sbs")
        
        if mock_query.edit_message_text.called:
            print("✅ Delete DNS records list generated")
            call_args = mock_query.edit_message_text.call_args
            
            # Check for buttons
            if len(call_args) > 1 and 'reply_markup' in call_args[1]:
                keyboard = call_args[1]['reply_markup']
                if hasattr(keyboard, 'inline_keyboard'):
                    buttons = keyboard.inline_keyboard
                    print(f"   Found {len(buttons)} delete buttons")
                    
                    if buttons and len(buttons) > 0:
                        first_button = buttons[0][0] if len(buttons[0]) > 0 else None
                        if first_button:
                            print(f"   First delete button callback: {first_button.callback_data}")
                        else:
                            print("   No first delete button found")
                else:
                    print("   No inline keyboard in delete interface")
            else:
                print("   No reply markup in delete interface")
        else:
            print("❌ Delete DNS records list failed to generate")
            
    except Exception as e:
        print(f"❌ Error testing delete functionality: {e}")

async def main():
    """Main test function"""
    await test_edit_dns_callback()
    await test_delete_dns_functionality()
    
    print("\n📊 DIAGNOSIS SUMMARY")
    print("=" * 30)
    print("If parsing works but handlers don't respond:")
    print("• Check session state management")
    print("• Verify DNS record retrieval in handlers") 
    print("• Check error handling in edit/delete functions")

if __name__ == "__main__":
    asyncio.run(main())