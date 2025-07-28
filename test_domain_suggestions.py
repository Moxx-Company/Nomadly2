#!/usr/bin/env python3
"""
Test domain suggestions functionality to verify alt_price fix
"""

import asyncio
import sys
from domain_service import get_domain_service

async def test_domain_suggestions():
    """Test that domain suggestions work without alt_price errors"""
    
    print("🔍 Testing Domain Suggestions Functionality...")
    
    try:
        domain_service = get_domain_service()
        
        # Test domain search that should show alternatives
        test_domain = "testdomain123.com"
        
        print(f"Testing domain search for: {test_domain}")
        result = await domain_service.search_domain_availability(test_domain)
        
        if result.get("success"):
            results = result.get("results", [])
            print(f"✅ Domain search completed successfully")
            print(f"📊 Found {len(results)} results")
            
            # Check if we have the main domain and alternatives
            main_domain = None
            alternatives = []
            
            for domain_result in results:
                if domain_result.get("requested"):
                    main_domain = domain_result
                else:
                    alternatives.append(domain_result)
            
            print(f"\n📋 Search Results:")
            if main_domain:
                print(f"  Main: {main_domain['domain']} - ${main_domain['price']:.2f} ({'Available' if main_domain['available'] else 'Unavailable'})")
            
            if alternatives:
                print(f"  Alternatives found: {len(alternatives)}")
                for alt in alternatives:
                    print(f"    {alt['domain']} - ${alt['price']:.2f} ({'Available' if alt['available'] else 'Unavailable'})")
            else:
                print("  ⚠️  No alternatives found")
            
            return len(alternatives) > 0
        else:
            print(f"❌ Domain search failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing domain suggestions: {e}")
        return False

async def main():
    print("🚀 Domain Suggestions Fix Verification")
    print("=" * 45)
    
    success = await test_domain_suggestions()
    
    if success:
        print("\n✅ Domain suggestions are working correctly!")
        print("Users will see alternative domain options when searching.")
        sys.exit(0)
    else:
        print("\n❌ Domain suggestions still have issues")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())