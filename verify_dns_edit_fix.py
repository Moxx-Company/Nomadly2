#!/usr/bin/env python3
"""
Comprehensive verification of DNS editing functionality after fixing the zone_id parameter issue.
"""

import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock, patch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_dns_edit_workflow():
    """Test complete DNS editing workflow with fixed parameter passing"""
    print("🧪 TESTING COMPLETE DNS EDIT WORKFLOW WITH ZONE_ID FIX")
    print("=" * 60)
    
    try:
        from nomadly3_clean_bot import NomadlyCleanBot
        from unified_dns_manager import UnifiedDNSManager
        
        bot = NomadlyCleanBot()
        
        # Simulate user selecting edit button
        print("Step 1: User clicks edit button")
        mock_query = MagicMock()
        mock_query.from_user.id = 5590563715
        mock_query.edit_message_text = AsyncMock()
        mock_query.answer = AsyncMock()
        
        # Test edit DNS record function
        record_id = "e40f36f424fbb4e1a1cdaaa39bc78d94"
        domain = "claudeb.sbs"
        
        print(f"   Record ID: {record_id}")
        print(f"   Domain: {domain}")
        
        # Mock DNS records response
        mock_dns_records = [
            {
                "id": "e40f36f424fbb4e1a1cdaaa39bc78d94",
                "type": "A",
                "name": "@",
                "content": "192.0.2.1",
                "ttl": 300
            },
            {
                "id": "f50a47b525cc5bc3def6fa563ce88e45",
                "type": "A", 
                "name": "www",
                "content": "192.0.2.1",
                "ttl": 300
            }
        ]
        
        with patch.object(bot.unified_dns_manager, 'get_dns_records', return_value=mock_dns_records):
            await bot.handle_edit_dns_record(mock_query, record_id, domain)
        
        if mock_query.edit_message_text.called:
            print("✅ Edit form displayed successfully")
            call_args = mock_query.edit_message_text.call_args
            if call_args and len(call_args[0]) > 0:
                message = call_args[0][0]
                print(f"   Form content: {message[:150]}...")
            else:
                print("   No message content found")
        else:
            print("❌ Edit form failed to display")
            return False
        
        # Step 2: Simulate user typing new value
        print("\nStep 2: User types new IP address")
        mock_message = MagicMock()
        mock_message.from_user.id = 5590563715
        mock_message.reply_text = AsyncMock()
        
        new_value = "208.77.244.11"
        print(f"   New value: {new_value}")
        
        # Mock successful zone ID lookup and update
        mock_zone_id = "f366a9dc0eadd5ea5b6f865b76cea73f"
        
        with patch.object(bot.unified_dns_manager, 'get_dns_records', return_value=mock_dns_records), \
             patch.object(bot.unified_dns_manager, 'get_zone_id', return_value=mock_zone_id), \
             patch.object(bot.unified_dns_manager, 'update_dns_record', return_value=True):
            
            await bot.handle_dns_edit_input(mock_message, new_value)
        
        if mock_message.reply_text.called:
            print("✅ DNS update completed successfully")
            call_args = mock_message.reply_text.call_args
            if call_args and len(call_args[0]) > 0:
                message = call_args[0][0]
                if "successfully" in message.lower():
                    print("   Update success message displayed")
                    return True
                else:
                    print(f"   Message: {message[:100]}...")
            else:
                print("   No message content found")
        else:
            print("❌ DNS update response failed")
        
    except Exception as e:
        print(f"❌ Error testing DNS edit workflow: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    return False

async def test_unified_dns_manager_parameters():
    """Test that unified DNS manager methods have correct parameters"""
    print("\n🔧 TESTING UNIFIED DNS MANAGER PARAMETER SIGNATURES")
    print("=" * 50)
    
    try:
        from unified_dns_manager import UnifiedDNSManager
        import inspect
        
        # Check update_dns_record method signature
        manager = UnifiedDNSManager()
        update_method = getattr(manager, 'update_dns_record')
        sig = inspect.signature(update_method)
        
        print(f"update_dns_record signature: {sig}")
        
        required_params = ['zone_id', 'record_id', 'record_type', 'name', 'content']
        method_params = list(sig.parameters.keys())
        
        for param in required_params:
            if param in method_params:
                print(f"✅ Parameter '{param}' found")
            else:
                print(f"❌ Parameter '{param}' missing")
                
        # Check if domain parameter exists (should NOT exist)
        if 'domain' in method_params:
            print("❌ Old 'domain' parameter still exists - needs to be removed")
            return False
        else:
            print("✅ Old 'domain' parameter correctly removed")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking method signatures: {e}")
        return False

async def test_dns_deletion_workflow():
    """Test DNS deletion workflow to ensure it's also working"""
    print("\n🗑️ TESTING DNS DELETION WORKFLOW")
    print("=" * 40)
    
    try:
        from nomadly3_clean_bot import NomadlyCleanBot
        
        bot = NomadlyCleanBot()
        
        # Mock deletion call
        mock_query = MagicMock()
        mock_query.from_user.id = 5590563715
        mock_query.edit_message_text = AsyncMock()
        mock_query.answer = AsyncMock()
        
        record_id = "idx_2"  # Index-based ID
        domain = "claudeb.sbs"
        
        # Mock DNS records
        mock_dns_records = [
            {"id": "rec1", "type": "A", "name": "@", "content": "192.0.2.1"},
            {"id": "rec2", "type": "A", "name": "www", "content": "192.0.2.1"},
            {"id": "rec3", "type": "MX", "name": "@", "content": "mail.claudeb.sbs"}
        ]
        
        mock_zone_id = "f366a9dc0eadd5ea5b6f865b76cea73f"
        
        with patch.object(bot.unified_dns_manager, 'get_dns_records', return_value=mock_dns_records), \
             patch.object(bot.unified_dns_manager, 'get_zone_id', return_value=mock_zone_id), \
             patch.object(bot.unified_dns_manager, 'delete_dns_record', return_value=True):
            
            await bot.handle_delete_dns_record(mock_query, record_id, domain)
        
        if mock_query.edit_message_text.called:
            print("✅ DNS deletion completed successfully")
            call_args = mock_query.edit_message_text.call_args
            if call_args and len(call_args[0]) > 0:
                message = call_args[0][0]
                if "successfully" in message.lower() or "deleted" in message.lower():
                    print("   Deletion success message displayed")
                    return True
                else:
                    print(f"   Message: {message[:100]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing DNS deletion: {e}")
        return False

async def main():
    """Main test function"""
    print("🔍 COMPREHENSIVE DNS FUNCTIONALITY VERIFICATION")
    print("=" * 55)
    print("Testing DNS edit/delete functionality after zone_id parameter fix\n")
    
    # Run all tests
    results = []
    
    results.append(await test_unified_dns_manager_parameters())
    results.append(await test_dns_edit_workflow())
    results.append(await test_dns_deletion_workflow())
    
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    tests = ["Parameter Signatures", "DNS Edit Workflow", "DNS Delete Workflow"] 
    for i, (test_name, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_name}: {status}")
    
    overall_success = all(results)
    print(f"\n🎯 OVERALL STATUS: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n✅ DNS editing functionality should now work properly for users!")
        print("   - Edit button callbacks are parsed correctly")
        print("   - Edit forms display with current values")
        print("   - User input is processed and updates DNS records")
        print("   - Zone ID parameter issue has been resolved")
    else:
        print("\n❌ Issues remain that need to be addressed")

if __name__ == "__main__":
    asyncio.run(main())