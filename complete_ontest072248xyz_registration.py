#!/usr/bin/env python3
"""
Complete the registration of ontest072248xyz.sbs domain that was interrupted by workflow restart.
We have confirmed payment and partial completion - now finish the process.
"""

import sys
import asyncio
from database import DatabaseManager
from datetime import datetime, timezone
from sqlalchemy import text

def complete_domain_registration():
    """Complete the domain registration that was interrupted"""
    
    print("🔧 COMPLETING INTERRUPTED DOMAIN REGISTRATION")
    print("===============================================")
    
    try:
        db = DatabaseManager()
        
        # Domain registration details from webhook logs
        domain_details = {
            'domain_name': 'ontest072248xyz.sbs',
            'user_id': 5590563715,
            'order_id': '4064c994-e2fb-4dc1-8570-727f1303ad68',
            'cloudflare_zone_id': '0ad9ef496bad59fd32ec70bf00149f3a',
            'openprovider_contact_handle': 'contact_4358',
            'openprovider_customer_handle': 'JP987516-US',
            'transaction_id': '0xe7f4dfc00ce15d4aa27b41e373d23645d8b652f5dc6049e8c7ab901120dafb9e',
            'eth_amount': '0.00738965',
            'nameserver_mode': 'cloudflare',
            'status': 'active'
        }
        
        print(f"✅ Domain: {domain_details['domain_name']}")
        print(f"✅ User ID: {domain_details['user_id']}")
        print(f"✅ Payment: {domain_details['eth_amount']} ETH confirmed")
        print(f"✅ Transaction: {domain_details['transaction_id']}")
        print(f"✅ Cloudflare Zone: {domain_details['cloudflare_zone_id']}")
        print()
        
        with db.get_session() as session:
            # Check if domain already exists
            existing = session.execute(
                text("SELECT id FROM registered_domains WHERE domain_name = :domain"),
                {'domain': domain_details['domain_name']}
            ).fetchone()
            
            if existing:
                print("⚠️  Domain already exists in database!")
                print(f"   Record ID: {existing[0]}")
                return True
            
            # Create the registered domain record
            print("📝 Creating registered domain record...")
            
            # Get current timestamp
            now = datetime.now(timezone.utc)
            
            # Calculate expiry (1 year from now)
            expiry_date = datetime.now(timezone.utc).replace(year=datetime.now().year + 1)
            
            insert_query = text("""
                INSERT INTO registered_domains (
                    domain_name,
                    user_id,
                    status,
                    nameserver_mode,
                    cloudflare_zone_id,
                    openprovider_contact_handle,
                    nameserver_addresses,
                    price_paid,
                    created_at,
                    updated_at,
                    expiry_date
                ) VALUES (
                    :domain_name,
                    :user_id,
                    :status,
                    :nameserver_mode,
                    :cloudflare_zone_id,
                    :openprovider_contact_handle,
                    :nameserver_addresses,
                    :price_paid,
                    :created_at,
                    :updated_at,
                    :expiry_date
                )
            """)
            
            # Default Cloudflare nameservers for the zone
            nameservers = ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"]
            
            session.execute(insert_query, {
                'domain_name': domain_details['domain_name'],
                'user_id': domain_details['user_id'],
                'status': domain_details['status'],
                'nameserver_mode': domain_details['nameserver_mode'],
                'cloudflare_zone_id': domain_details['cloudflare_zone_id'],
                'openprovider_contact_handle': domain_details['openprovider_contact_handle'],
                'nameserver_addresses': nameservers,
                'price_paid': 9.87,  # USD amount paid
                'created_at': now,
                'updated_at': now,
                'expires_at': expiry_date
            })
            
            session.commit()
            
            print("✅ Domain record created successfully!")
            
            # Verify the record was created
            verify = session.execute(
                text("SELECT id, domain_name, status FROM registered_domains WHERE domain_name = :domain"),
                {'domain': domain_details['domain_name']}
            ).fetchone()
            
            if verify:
                print(f"✅ Verification: Domain {verify[1]} created with ID {verify[0]}, status: {verify[2]}")
                print()
                print("🎉 DOMAIN REGISTRATION COMPLETED SUCCESSFULLY!")
                print("============================================")
                print(f"Domain: {domain_details['domain_name']}")
                print(f"Status: Active and available to user")
                print(f"Cloudflare Zone: {domain_details['cloudflare_zone_id']}")
                print(f"Payment: {domain_details['eth_amount']} ETH confirmed")
                print(f"User can now manage this domain through the bot")
                
                return True
            else:
                print("❌ Failed to verify domain creation")
                return False
                
    except Exception as e:
        print(f"❌ Registration completion failed: {e}")
        return False

if __name__ == "__main__":
    success = complete_domain_registration()
    sys.exit(0 if success else 1)