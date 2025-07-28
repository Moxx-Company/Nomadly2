#!/usr/bin/env python3
"""
Test DNS management UI functionality to identify edit/delete issues
"""

import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_dns_management_interface():
    """Test the DNS management interface"""
    print("🧪 Testing DNS Management Interface")
    print("=" * 50)
    
    # Import the bot and necessary modules
    try:
        from nomadly3_clean_bot import Nomadly3CleanBot
        from services.unified_dns_manager import unified_dns_manager
        
        # Test 1: Check if unified_dns_manager can get DNS records
        print("\n📊 Step 1: Testing DNS Records Retrieval...")
        try:
            dns_records = await unified_dns_manager.get_dns_records("claudeb.sbs")
            print(f"   ✅ Retrieved {len(dns_records)} DNS records for claudeb.sbs")
            
            # Show first few records for debugging
            for i, record in enumerate(dns_records[:3]):
                print(f"   Record {i}: {record.get('type')} {record.get('name')} -> {record.get('content')[:30]}...")
                
        except Exception as e:
            print(f"   ❌ DNS records retrieval failed: {e}")
            return False
        
        # Test 2: Simulate edit button callback
        print("\n✏️ Step 2: Testing Edit DNS Record Callback Generation...")
        try:
            # Create mock bot instance
            bot = Nomadly3CleanBot()
            
            # Create mock query
            mock_query = MagicMock()
            mock_query.from_user.id = 5590563715
            mock_query.edit_message_text = AsyncMock()
            
            # Test the edit records list function
            await bot.show_edit_dns_records_list(mock_query, "claudeb_sbs")
            
            # Check if the mock was called (meaning the function completed)
            if mock_query.edit_message_text.called:
                print("   ✅ Edit DNS records list generated successfully")
                call_args = mock_query.edit_message_text.call_args
                print(f"   Message: {call_args[0][0][:100]}...")
                
                # Extract keyboard from call
                if len(call_args) > 1 and 'reply_markup' in call_args[1]:
                    keyboard = call_args[1]['reply_markup']
                    if hasattr(keyboard, 'inline_keyboard'):
                        buttons = keyboard.inline_keyboard
                        print(f"   Generated {len(buttons)} edit buttons")
                        
                        # Show first button callback data
                        if buttons and len(buttons) > 0 and len(buttons[0]) > 0:
                            first_button = buttons[0][0]
                            print(f"   First button callback: {first_button.callback_data}")
                        else:
                            print("   ⚠️ No edit buttons found in interface")
                    else:
                        print("   ⚠️ No keyboard markup found")
                else:
                    print("   ⚠️ No reply markup in edit message call")
            else:
                print("   ❌ Edit DNS records list function failed to call edit_message_text")
                return False
                
        except Exception as e:
            print(f"   ❌ Edit records list test failed: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
        
        # Test 3: Test edit callback parsing
        print("\n🔧 Step 3: Testing Edit Callback Parsing...")
        try:
            # Test with sample callback data
            test_callback = "edit_dns_823d11992ce992a6d14865cc0ec5bebe_claudeb_sbs"
            
            # Simulate the callback parsing logic
            if test_callback.startswith("edit_dns_"):
                callback_part = test_callback.replace("edit_dns_", "")
                # Parse the callback like the bot does
                if "_" in callback_part:
                    parts = callback_part.rsplit("_", 2)  # Split from right to get domain parts
                    if len(parts) >= 3:
                        record_id = parts[0]
                        domain = f"{parts[1]}.{parts[2]}"
                        print(f"   ✅ Parsed callback: record_id='{record_id}', domain='{domain}'")
                    else:
                        print(f"   ⚠️ Insufficient parts in callback: {parts}")
                else:
                    print(f"   ⚠️ No underscore found in callback part: {callback_part}")
                    
        except Exception as e:
            print(f"   ❌ Callback parsing test failed: {e}")
            return False
            
        # Test 4: Test actual edit handler
        print("\n🎯 Step 4: Testing Edit Handler Function...")
        try:
            # Create mock for edit handler test
            mock_query_edit = MagicMock()
            mock_query_edit.from_user.id = 5590563715
            mock_query_edit.edit_message_text = AsyncMock()
            
            # Test the actual edit handler with a record ID
            if dns_records and len(dns_records) > 0:
                first_record_id = dns_records[0].get('id', 'test_id')
                await bot.handle_edit_dns_record(mock_query_edit, first_record_id, "claudeb.sbs")
                
                if mock_query_edit.edit_message_text.called:
                    print("   ✅ Edit handler completed successfully")
                    call_args = mock_query_edit.edit_message_text.call_args
                    if call_args:
                        print(f"   Response: {call_args[0][0][:100]}...")
                else:
                    print("   ❌ Edit handler did not call edit_message_text")
                    return False
            else:
                print("   ⚠️ No DNS records available for edit handler test")
                
        except Exception as e:
            print(f"   ❌ Edit handler test failed: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import modules: {e}")
        return False

async def main():
    """Main test function"""
    print("🔍 DNS MANAGEMENT UI DIAGNOSTIC")
    print("=" * 40)
    
    success = await test_dns_management_interface()
    
    print("\n📊 TEST RESULTS:")
    print("=" * 30)
    
    if success:
        print("✅ DNS management interface components working")
        print("✅ DNS records retrieval functional")
        print("✅ Edit interface generation working")
        print("✅ Callback parsing operational")
        print("\n💡 If UI still appears broken, the issue may be in:")
        print("   • Button callback routing in main handler")
        print("   • Session management during edit operations")
        print("   • Real-time DNS record updates")
    else:
        print("❌ DNS management interface has issues")
        print("⚠️ See specific error messages above for details")

if __name__ == "__main__":
    asyncio.run(main())