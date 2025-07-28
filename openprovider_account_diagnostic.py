#!/usr/bin/env python3
"""
Comprehensive OpenProvider account diagnostic
Check account status, permissions, and TLD availability
"""

import os
import logging
import requests
from apis.production_openprovider import OpenProviderAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_openprovider_account():
    """Comprehensive account diagnostic"""
    print("🔍 OPENPROVIDER ACCOUNT DIAGNOSTIC")
    print("=" * 35)

    try:
        # Initialize API
        op_api = OpenProviderAPI()
        print("✅ Authentication successful")

        # Check account info
        print("\n1. Checking account information...")
        url = f"{op_api.base_url}/v1beta/customers/info"
        response = requests.get(url, headers=op_api._get_headers(), timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Account info retrieved")
            print(f"   Status: {result.get('data', {}).get('status', 'Unknown')}")
            print(f"   Balance: {result.get('data', {}).get('balance', 'Unknown')}")
        else:
            print(f"⚠️ Account info error: {response.status_code}")

        # Check TLD info for .sbs
        print("\n2. Checking .sbs TLD availability...")
        url = f"{op_api.base_url}/v1beta/tlds/sbs"
        response = requests.get(url, headers=op_api._get_headers(), timeout=30)

        if response.status_code == 200:
            result = response.json()
            tld_data = result.get("data", {})
            print(f"✅ .sbs TLD information:")
            print(f"   Available: {tld_data.get('is_available', 'Unknown')}")
            print(f"   Price: {tld_data.get('price', 'Unknown')}")
            print(f"   Status: {tld_data.get('status', 'Unknown')}")
        else:
            print(f"⚠️ .sbs TLD info error: {response.status_code}")
            print(f"   Response: {response.text}")

        # Check domain availability for a test domain
        print("\n3. Checking domain availability...")
        test_domain = "opdiagnostic2025"
        url = f"{op_api.base_url}/v1beta/domains/check"
        data = {"domains": [{"name": test_domain, "extension": "sbs"}]}

        response = requests.post(
            url, json=data, headers=op_api._get_headers(), timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            domains = result.get("data", {}).get("results", [])
            if domains:
                domain_info = domains[0]
                print(f"✅ Domain check: {test_domain}.sbs")
                print(f"   Available: {domain_info.get('status') == 'free'}")
                print(f"   Status: {domain_info.get('status')}")
                print(f"   Price: {domain_info.get('price')}")
        else:
            print(f"⚠️ Domain check error: {response.status_code}")

        # Check recent orders/domains
        print("\n4. Checking recent domains...")
        url = f"{op_api.base_url}/v1beta/domains"
        response = requests.get(url, headers=op_api._get_headers(), timeout=30)

        if response.status_code == 200:
            result = response.json()
            domains = result.get("data", {}).get("results", [])
            print(f"✅ Found {len(domains)} domains in account:")

            for domain in domains[:5]:  # Show first 5
                print(
                    f"   • {domain.get('domain_name')} (Status: {domain.get('status')})"
                )

            # Look for our successful domain
            hbumbsslll_found = any(
                d.get("domain_name") == "hbumbsslll.sbs" for d in domains
            )
            if hbumbsslll_found:
                print(f"   ✅ Found successful domain: hbumbsslll.sbs")
            else:
                print(f"   ⚠️ Previous successful domain not found in current list")
        else:
            print(f"⚠️ Domains list error: {response.status_code}")

        return True

    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        return False


def test_minimal_registration():
    """Test with absolute minimal registration data"""
    print("\n🧪 TESTING MINIMAL REGISTRATION")
    print("=" * 30)

    try:
        op_api = OpenProviderAPI()

        # Try with absolute minimal data
        url = f"{op_api.base_url}/v1beta/domains"

        # Create fresh contact
        contact_handle = op_api._create_customer_handle()
        print(f"Created contact: {contact_handle}")

        # Minimal registration data
        data = {
            "domain": {"name": "minimal2025", "extension": "sbs"},
            "period": 1,
            "owner_handle": contact_handle,
            "admin_handle": contact_handle,
            "tech_handle": contact_handle,
            "billing_handle": contact_handle,
        }

        print(f"Testing minimal registration with data: {data}")

        response = requests.post(
            url, json=data, headers=op_api._get_headers(), timeout=30
        )

        print(f"Response: {response.status_code}")
        print(f"Body: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("✅ SUCCESS with minimal data!")
                return True

        return False

    except Exception as e:
        print(f"❌ Minimal test error: {e}")
        return False


async def main():
    """Run comprehensive diagnostic"""
    print("🚀 COMPREHENSIVE OPENPROVIDER DIAGNOSTIC")
    print("=" * 42)

    # Run account diagnostic
    account_ok = check_openprovider_account()

    # Test minimal registration
    minimal_success = test_minimal_registration()

    if not account_ok or not minimal_success:
        print("\n📋 DIAGNOSTIC SUMMARY")
        print("=" * 18)
        print("The consistent HTTP 400 error code 80 suggests:")
        print("1. Account may need verification/reactivation")
        print("2. .sbs TLD permissions may be restricted")
        print("3. Account balance may be insufficient")
        print("4. OpenProvider may have changed requirements")

        print("\n🎯 NEXT STEPS:")
        print("1. Contact OpenProvider support directly")
        print("2. Reference previous successful domain: hbumbsslll.sbs")
        print("3. Mention error code 80 and .sbs TLD issues")
        print("4. Request account status verification")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
