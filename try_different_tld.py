#!/usr/bin/env python3
"""
Test domain registration with different TLDs to isolate .sbs issue
"""

import logging
from apis.production_openprovider import OpenProviderAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_different_tlds():
    """Test registration with different TLDs"""
    print("🌐 TESTING DIFFERENT TLD REGISTRATION")
    print("=" * 37)

    try:
        op_api = OpenProviderAPI()

        # Test different TLDs
        test_tlds = [
            "com",  # Most common
            "org",  # Non-profit
            "net",  # Network
            "info",  # Information
            "biz",  # Business
            "sbs",  # Our target
        ]

        results = {}

        for tld in test_tlds:
            print(f"\n🎯 Testing .{tld} registration...")
            test_domain = f"testdomreg2025"

            try:
                success, domain_id, message = op_api.register_domain(
                    test_domain, tld, {}, None
                )

                if success and domain_id:
                    print(f"✅ .{tld} registration SUCCESS: {domain_id}")
                    results[tld] = "SUCCESS"

                    # If successful, we found a working TLD
                    print(f"\n🎉 BREAKTHROUGH: .{tld} registration works!")
                    print("This confirms the API integration is correct")
                    print("The issue is specifically with .sbs TLD permissions")
                    break
                else:
                    print(f"❌ .{tld} failed: {message}")
                    results[tld] = f"FAILED: {message}"

            except Exception as e:
                print(f"❌ .{tld} error: {e}")
                results[tld] = f"ERROR: {e}"

        print(f"\n📊 RESULTS SUMMARY:")
        print("=" * 17)
        for tld, result in results.items():
            status_icon = "✅" if "SUCCESS" in result else "❌"
            print(f"{status_icon} .{tld}: {result}")

        # Check if any TLD worked
        successful_tlds = [
            tld for tld, result in results.items() if "SUCCESS" in result
        ]

        if successful_tlds:
            print(f"\n🎉 WORKING TLDs FOUND: {', '.join(successful_tlds)}")
            print("✅ API integration is correct")
            print("✅ Account has domain registration capabilities")
            print("⚠️ Issue is specific to .sbs TLD permissions")

            print(f"\n🔧 SOLUTION:")
            print("Contact OpenProvider to enable .sbs TLD for your account")
            print("Reference successful registration of other TLDs")
            return True
        else:
            print(f"\n❌ NO TLDs WORKING")
            print("This indicates a broader account or API issue")
            return False

    except Exception as e:
        print(f"❌ TLD test error: {e}")
        return False


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_different_tlds())
