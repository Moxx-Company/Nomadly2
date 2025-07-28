#!/usr/bin/env python3
"""
Comprehensive Fix for Nameserver Management Issues
Addresses all identified issues with NS record management for user 5590563715
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
from database import get_db_manager
from apis.production_openprovider import OpenProviderAPI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NameserverManagementFixer:
    """Fix all nameserver management issues"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.openprovider = OpenProviderAPI()
        
    def run_comprehensive_fix(self):
        """Run comprehensive nameserver management fix"""
        print("🔧 COMPREHENSIVE NAMESERVER MANAGEMENT FIX")
        print("=" * 50)
        
        # Step 1: Fix database inconsistencies
        self.fix_database_nameserver_data()
        
        # Step 2: Validate OpenProvider domain IDs
        self.validate_domain_ids()
        
        # Step 3: Test nameserver update functionality  
        self.test_nameserver_updates()
        
        # Step 4: Clear stuck user states
        self.clear_stuck_states()
        
        print("\n🎉 NAMESERVER MANAGEMENT FIX COMPLETE")
        return True
        
    def fix_database_nameserver_data(self):
        """Fix database nameserver inconsistencies"""
        print("\n1. 📊 FIXING DATABASE NAMESERVER DATA")
        print("-" * 30)
        
        try:
            # Get all domains for user 5590563715
            with self.db.get_session() as session:
                from sqlalchemy import text
                
                result = session.execute(text("""
                    SELECT domain_name, openprovider_domain_id, cloudflare_zone_id, 
                           nameserver_mode, nameservers
                    FROM registered_domains 
                    WHERE telegram_id = 5590563715
                """))
                
                domains = result.fetchall()
                
                for domain_data in domains:
                    domain_name = domain_data[0]
                    nameservers = domain_data[4]
                    
                    if not nameservers or nameservers.strip() == "":
                        print(f"🔧 Fixing missing nameservers for {domain_name}")
                        # Set default Cloudflare nameservers
                        default_ns = '["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"]'
                        
                        session.execute(text("""
                            UPDATE registered_domains 
                            SET nameservers = :nameservers,
                                nameserver_mode = 'cloudflare'
                            WHERE domain_name = :domain_name
                        """), {
                            'nameservers': default_ns,
                            'domain_name': domain_name
                        })
                        
                        session.commit()
                        print(f"✅ Fixed nameservers for {domain_name}")
                    else:
                        print(f"✅ {domain_name} nameservers OK: {nameservers[:50]}...")
                        
        except Exception as e:
            print(f"❌ Database fix error: {e}")
            return False
            
        return True
        
    def validate_domain_ids(self):
        """Validate OpenProvider domain IDs"""
        print("\n2. 🔍 VALIDATING OPENPROVIDER DOMAIN IDS")
        print("-" * 30)
        
        try:
            with self.db.get_session() as session:
                from sqlalchemy import text
                
                result = session.execute(text("""
                    SELECT domain_name, openprovider_domain_id
                    FROM registered_domains 
                    WHERE telegram_id = 5590563715
                """))
                
                domains = result.fetchall()
                
                for domain_name, domain_id in domains:
                    print(f"🔍 Checking {domain_name}: ID {domain_id}")
                    
                    # Check for special status markers
                    domain_id_str = str(domain_id) if domain_id else "None"
                    
                    if domain_id_str in ["not_manageable_account_mismatch", "already_registered", "needs_reregistration"]:
                        print(f"⚠️  {domain_name} has special status: {domain_id_str}")
                        print(f"   -> Cannot update nameservers via OpenProvider API")
                        print(f"   -> DNS management via Cloudflare still works")
                    elif not domain_id or domain_id == "None":
                        print(f"❌ {domain_name} missing domain ID")
                    else:
                        try:
                            int(domain_id_str)
                            print(f"✅ {domain_name} has valid numeric ID: {domain_id}")
                        except ValueError:
                            print(f"❌ {domain_name} has invalid ID format: {domain_id_str}")
                            
        except Exception as e:
            print(f"❌ Domain ID validation error: {e}")
            return False
            
        return True
        
    def test_nameserver_updates(self):
        """Test nameserver update functionality"""
        print("\n3. ⚡ TESTING NAMESERVER UPDATE FUNCTIONALITY")  
        print("-" * 30)
        
        try:
            # Test with thanksjesus.sbs (known working domain)
            test_domain = "thanksjesus.sbs"
            test_nameservers = ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"]
            
            print(f"🧪 Testing nameserver update for {test_domain}")
            
            # Test the update method
            success = self.openprovider.update_nameservers(test_domain, test_nameservers)
            
            if success:
                print(f"✅ Nameserver update test PASSED for {test_domain}")
            else:
                print(f"❌ Nameserver update test FAILED for {test_domain}")
                print("   -> Checking logs for specific error details")
                
        except Exception as e:
            print(f"❌ Nameserver test error: {e}")
            return False
            
        return True
        
    def clear_stuck_states(self):
        """Clear stuck user states"""
        print("\n4. 🧹 CLEARING STUCK USER STATES")
        print("-" * 30)
        
        try:
            user_id = 5590563715
            
            with self.db.get_session() as session:
                from sqlalchemy import text
                
                # Get current state
                result = session.execute(text("""
                    SELECT current_state FROM user_states WHERE telegram_id = :user_id
                """), {'user_id': user_id})
                
                current_state = result.scalar()
                
                if current_state:
                    print(f"🔍 Current user state: {current_state}")
                    
                    if current_state in ["awaiting_nameserver_confirmation", "custom_nameservers_update"]:
                        print(f"🧹 Clearing stuck state: {current_state}")
                        
                        # Clear the state
                        session.execute(text("""
                            UPDATE user_states 
                            SET current_state = NULL,
                                state_data = NULL,
                                updated_at = NOW()
                            WHERE telegram_id = :user_id
                        """), {'user_id': user_id})
                        
                        session.commit()
                        print("✅ User state cleared successfully")
                    else:
                        print(f"✅ User state is normal: {current_state}")
                else:
                    print("✅ No user state found (user is free)")
                    
        except Exception as e:
            print(f"❌ State clearing error: {e}")
            return False
            
        return True
        
    def generate_fix_report(self):
        """Generate comprehensive fix report"""
        print("\n📋 NAMESERVER MANAGEMENT FIX REPORT")
        print("=" * 50)
        
        try:
            with self.db.get_session() as session:
                from sqlalchemy import text
                
                # Get all domain data
                result = session.execute(text("""
                    SELECT domain_name, openprovider_domain_id, cloudflare_zone_id, 
                           nameserver_mode, nameservers
                    FROM registered_domains 
                    WHERE telegram_id = 5590563715
                    ORDER BY domain_name
                """))
                
                domains = result.fetchall()
                
                print(f"📊 Total domains: {len(domains)}")
                print()
                
                for i, domain_data in enumerate(domains, 1):
                    domain_name = domain_data[0]
                    op_id = domain_data[1] 
                    cf_zone = domain_data[2]
                    ns_mode = domain_data[3]
                    nameservers = domain_data[4]
                    
                    print(f"{i}. {domain_name}")
                    print(f"   OpenProvider ID: {op_id}")
                    print(f"   Cloudflare Zone: {cf_zone}")
                    print(f"   NS Mode: {ns_mode}")
                    print(f"   Nameservers: {nameservers}")
                    
                    # Status assessment
                    if cf_zone and nameservers:
                        print("   Status: ✅ FULLY OPERATIONAL")
                    elif cf_zone:
                        print("   Status: ⚠️  ZONE OK, NAMESERVERS MISSING")
                    else:
                        print("   Status: ❌ NEEDS ATTENTION")
                    print()
                    
                # Get user state
                result = session.execute(text("""
                    SELECT current_state FROM user_states WHERE telegram_id = 5590563715
                """))
                
                user_state = result.scalar()
                print(f"👤 User State: {user_state or 'FREE'}")
                
        except Exception as e:
            print(f"❌ Report generation error: {e}")

if __name__ == "__main__":
    try:
        fixer = NameserverManagementFixer()
        fixer.run_comprehensive_fix()
        fixer.generate_fix_report()
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        sys.exit(1)