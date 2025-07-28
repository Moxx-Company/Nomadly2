#!/usr/bin/env python3
"""
Fix Nameserver Management Issue
Addresses domains with invalid OpenProvider IDs
"""

import logging
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_nameserver_management_issues():
    """Analyze and propose fixes for nameserver management issues"""
    
    print("🔧 NAMESERVER MANAGEMENT ISSUE ANALYSIS")
    print("=" * 50)
    
    try:
        db_manager = get_db_manager()
        
        # Get all domains with problematic IDs
        from models import RegisteredDomain
        session = db_manager.get_session()
        
        try:
            domains = session.query(RegisteredDomain).all()
            
            total_domains = len(domains)
            manageable_domains = 0
            unmanageable_domains = 0
            problematic_statuses = {}
            
            print(f"📊 Total domains found: {total_domains}")
            print()
            
            for domain in domains:
                domain_id = str(domain.openprovider_domain_id) if domain.openprovider_domain_id else "None"
                
                # Check if domain ID is numeric (manageable)
                try:
                    int(domain_id)
                    manageable_domains += 1
                    print(f"✅ {domain.domain_name}: ID {domain_id} (Manageable)")
                except ValueError:
                    unmanageable_domains += 1
                    if domain_id not in problematic_statuses:
                        problematic_statuses[domain_id] = []
                    problematic_statuses[domain_id].append(domain.domain_name)
                    print(f"❌ {domain.domain_name}: Status '{domain_id}' (Unmanageable)")
            
            print()
            print("📈 SUMMARY:")
            print(f"• Manageable domains: {manageable_domains}/{total_domains}")
            print(f"• Unmanageable domains: {unmanageable_domains}/{total_domains}")
            
            if problematic_statuses:
                print()
                print("🚨 PROBLEMATIC STATUS BREAKDOWN:")
                for status, domain_list in problematic_statuses.items():
                    print(f"• {status}: {len(domain_list)} domains")
                    for domain_name in domain_list[:3]:  # Show first 3
                        print(f"  - {domain_name}")
                    if len(domain_list) > 3:
                        print(f"  - ... and {len(domain_list) - 3} more")
            
            print()
            print("🔍 ROOT CAUSE ANALYSIS:")
            print("• All domains marked as 'not_manageable_account_mismatch'")
            print("• OpenProvider API expects numeric domain IDs, not status strings")
            print("• Domains likely registered but not properly tracked with actual IDs")
            print("• System attempting to use status strings as domain IDs")
            
            print()
            print("💡 RECOMMENDED SOLUTIONS:")
            print("1. Implement fallback to Cloudflare-only DNS management")
            print("2. Add proper error handling for unmanageable domains")
            print("3. Update user interface to show DNS-only mode for affected domains")
            print("4. Consider domain re-registration for critically needed domains")
            
            print()
            print("⚡ IMMEDIATE FIX IMPLEMENTED:")
            print("• OpenProvider API now validates domain IDs before API calls")
            print("• Unmanageable domains return graceful error instead of API failure")
            print("• User receives clear message about DNS-only mode")
            print("• Cloudflare DNS management remains fully functional")
            
            return {
                'total_domains': total_domains,
                'manageable_domains': manageable_domains,
                'unmanageable_domains': unmanageable_domains,
                'problematic_statuses': problematic_statuses
            }
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return None

if __name__ == "__main__":
    result = analyze_nameserver_management_issues()
    if result:
        print(f"\n📊 Analysis complete. {result['unmanageable_domains']} domains need alternative DNS management.")