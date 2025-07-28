#!/usr/bin/env python3
"""
Domain Registration Track Record - Investigate What Actually Happened
"""

from database import get_db_manager
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def investigate_domain_registration():
    """Investigate what actually happened with domain registration"""
    print("🔍 DOMAIN REGISTRATION TRACK RECORD INVESTIGATION")
    print("=" * 60)

    try:
        db_manager = get_db_manager()

        # Check the specific order
        order_id = "e1acf701-93f1-41e3-b334-74f482734d38"
        order = db_manager.get_order(order_id)

        print(f"📋 ORDER DETAILS:")
        print(f"   Order ID: {order.order_id}")
        print(f"   Service Type: {order.service_type}")
        print(f"   Payment Status: {order.payment_status}")
        print(f"   Amount: ${order.amount}")
        print(f"   Created: {order.created_at}")

        # Check what's in the database for registered domains
        domains = db_manager.get_user_domains(5590563715)
        print(f"\n🌐 DATABASE REGISTERED DOMAINS:")
        print("=" * 35)

        if domains:
            for domain in domains:
                print(f"Domain: {domain.domain_name}")
                print(f"Status: {domain.status}")
                print(f"Registration Date: {domain.registration_date}")
                print(f"OpenProvider Domain ID: {domain.openprovider_domain_id}")
                print(f"Cloudflare Zone ID: {domain.cloudflare_zone_id}")
                print(f"Nameserver Mode: {domain.nameserver_mode}")
                print(f"Contact Handle: {domain.openprovider_contact_handle}")
                print()
        else:
            print("No domains found in database")

        # Check what the current registration method actually does
        print(f"🔍 ANALYZING CURRENT REGISTRATION LOGIC:")
        print("=" * 45)

        # Look at the _complete_domain_registration_sync method
        with open("payment_service.py", "r") as f:
            content = f.read()

        # Find what it actually does for registration
        if (
            'logger.info(f"Domain nomadly5.sbs registered successfully in database")'
            in content
        ):
            print("❌ ISSUE FOUND: Registration method only stores in database")
            print("   - Does NOT call OpenProvider API to actually register domain")
            print("   - Does NOT create Cloudflare DNS zone")
            print("   - Only creates local database record")

        # Check if there are any API calls
        has_openprovider_call = "openprovider.register_domain" in content
        has_cloudflare_call = "cloudflare.create_zone" in content

        print(f"\n🔍 API INTEGRATION ANALYSIS:")
        print("=" * 30)
        print(
            f"OpenProvider API Call Present: {'✅ Yes' if has_openprovider_call else '❌ No'}"
        )
        print(
            f"Cloudflare API Call Present: {'✅ Yes' if has_cloudflare_call else '❌ No'}"
        )

        # Check if this is just mock/placeholder registration
        if not has_openprovider_call and not has_cloudflare_call:
            print(f"\n❌ CRITICAL ISSUE IDENTIFIED:")
            print("=" * 30)
            print("The current registration method is PLACEHOLDER/MOCK only")
            print("- Payment is processed correctly ✅")
            print("- Domain name is extracted correctly ✅")
            print("- BUT domain is NOT actually registered with registrar ❌")
            print("- Database entry is created but no real domain exists ❌")

            print(f"\n📋 WHAT NEEDS TO BE FIXED:")
            print("=" * 25)
            print("1. Add actual OpenProvider API call to register domain")
            print("2. Add actual Cloudflare API call to create DNS zone")
            print("3. Store real domain_id and cloudflare_zone_id from API responses")
            print("4. Implement proper error handling for failed registrations")

            return False
        else:
            print("API integration appears to be present")
            return True

    except Exception as e:
        print(f"❌ Investigation error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    investigate_domain_registration()
