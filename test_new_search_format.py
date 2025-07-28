#!/usr/bin/env python3
"""
Test the new search format that shows both main domain and alternatives
"""

def test_search_result_format():
    """Test what the new search results should look like"""
    
    print("🔍 NEW SEARCH RESULT FORMAT")
    print("="*50)
    
    # Example 1: Available domain
    print("\n📌 EXAMPLE 1: Available Domain (hubside.sbs)")
    print("-" * 40)
    print("🔍 Search Results: hubside.sbs")
    print()
    print("🟢 Available:")
    print("• hubside.sbs - $32.61 USD")
    print()
    print("💡 Alternative Extensions:")
    print("• hubside.net - $18.00 USD ✅ Available")
    print("• hubside.org - $16.00 USD ✅ Available") 
    print("• hubside.io - $49.00 USD ✅ Available")
    print()
    print("Buttons: [⚡ Register hubside.sbs] [⚡ Register hubside.net] [⚡ Register hubside.org] [⚡ Register hubside.io]")
    
    # Example 2: Taken domain
    print("\n📌 EXAMPLE 2: Taken Domain (wewillwin.sbs)")
    print("-" * 40)
    print("🔍 Search Results: wewillwin.sbs")
    print()
    print("🔴 Taken:")
    print("• wewillwin.sbs - Not available")
    print()
    print("💡 Alternative Extensions:")
    print("• wewillwin.net - $18.00 USD ✅ Available")
    print("• wewillwin.org - $16.00 USD ✅ Available")
    print("• wewillwin.io - $49.00 USD ✅ Available")
    print()
    print("Buttons: [⚡ Register wewillwin.net] [⚡ Register wewillwin.org] [⚡ Register wewillwin.io]")
    
    print("\n✅ KEY IMPROVEMENTS:")
    print("• Shows BOTH requested domain AND alternatives")
    print("• Works for available AND taken domains")
    print("• Shows real pricing for all extensions")
    print("• Provides registration buttons for available options")
    print("• Gives users more choice regardless of main domain status")

if __name__ == "__main__":
    test_search_result_format()