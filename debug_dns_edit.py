#!/usr/bin/env python3
"""
Debug DNS Edit - Test the exact edit workflow that's failing
"""

import asyncio
from unified_dns_manager import UnifiedDNSManager

async def test_dns_edit_workflow():
    """Test the DNS edit workflow to find the issue"""
    domain = "claudeb.sbs"
    
    print(f"🔍 Testing DNS edit workflow for {domain}")
    
    # Step 1: Get DNS records (same as edit list does)
    print("\n📋 Step 1: Retrieving DNS Records for Edit List")
    try:
        dns_manager = UnifiedDNSManager()
        records = await dns_manager.get_dns_records(domain)
        
        if records:
            print(f"✅ Found {len(records)} DNS records:")
            for i, record in enumerate(records[:3], 1):  # Show first 3
                record_id = record.get('id', '')
                rec_type = record.get('type', 'N/A')
                name = record.get('name', '@')
                if name == domain:
                    name = "@"
                content = record.get('content', 'N/A')
                if len(content) > 30:
                    content = content[:27] + "..."
                
                print(f"  {i}. ID: {record_id}")
                print(f"     Type: {rec_type}, Name: {name}, Content: {content}")
                
                # Simulate callback data creation (like in show_edit_dns_records_list)
                callback_data = f"edit_dns_{record_id}_{domain.replace('.', '_')}"
                print(f"     Callback: {callback_data}")
                
                # Simulate callback parsing (like in handle_callback_query)
                parts = callback_data.replace("edit_dns_", "").split("_", 1)
                if len(parts) == 2:
                    parsed_record_id, parsed_domain = parts
                    parsed_domain_clean = parsed_domain.replace('_', '.')
                    print(f"     Parsed ID: {parsed_record_id}")
                    print(f"     Parsed Domain: {parsed_domain_clean}")
                    
                    # Test the matching logic (like in handle_edit_dns_record)
                    match_found = False
                    for test_record in records:
                        if str(test_record.get('id')) == str(parsed_record_id):
                            match_found = True
                            print(f"     ✅ Record match found!")
                            break
                    
                    if not match_found:
                        print(f"     ❌ Record match NOT found!")
                        print(f"     🔍 Comparing '{parsed_record_id}' with available IDs:")
                        for test_record in records:
                            test_id = str(test_record.get('id'))
                            print(f"         - '{test_id}' == '{parsed_record_id}' ? {test_id == parsed_record_id}")
                else:
                    print(f"     ❌ Callback parsing failed: {len(parts)} parts")
                
                print()  # Blank line between records
        else:
            print("❌ No DNS records found")
            
    except Exception as e:
        print(f"❌ Error in DNS edit workflow test: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")

    # Step 2: Test specific record ID that might be causing issues
    print("\n🎯 Step 2: Testing Specific Record ID Matching")
    try:
        # Let's manually test with the first record we found in the previous debug
        test_record_id = "823d11992ce992a6d14865cc0ec5bebe"  # First A record ID from previous debug
        
        print(f"Testing with record ID: {test_record_id}")
        
        # Get records again
        records = await dns_manager.get_dns_records(domain)
        found_record = None
        
        for record in records:
            record_id_str = str(record.get('id'))
            print(f"Comparing: '{record_id_str}' == '{test_record_id}' ? {record_id_str == test_record_id}")
            if record_id_str == test_record_id:
                found_record = record
                print("✅ Found matching record!")
                break
        
        if not found_record:
            print("❌ No matching record found")
        else:
            print(f"✅ Match details: {found_record.get('type')} {found_record.get('name')} → {found_record.get('content')}")
            
    except Exception as e:
        print(f"❌ Error in specific ID test: {e}")

if __name__ == "__main__":
    asyncio.run(test_dns_edit_workflow())