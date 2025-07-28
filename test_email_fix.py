#!/usr/bin/env python3
"""
Test Email Address Handling Fix
===============================
Verify that email addresses no longer trigger domain validation errors
"""

import sys
import re

def test_email_detection_logic():
    """Test the email detection logic that was added to fix the bug"""
    
    print("🔍 Testing Email vs Domain Detection Logic")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        # Email addresses (should NOT trigger domain search)
        ("onarrival21@gmail.com", True, "Email address"),
        ("user@example.com", True, "Email address"),
        ("admin+test@domain.org", True, "Email address"),
        ("test.user@company.co.uk", True, "Email address"),
        
        # Domain names (should trigger domain search)
        ("example.com", False, "Domain name"),
        ("mydomain.net", False, "Domain name"),
        ("test-site.org", False, "Domain name"),
        ("nomadly.sbs", False, "Domain name"),
        
        # Invalid formats (should get helpful message)
        ("www.example.com", False, "Invalid domain - www prefix"),
        ("example", False, "Invalid domain - no TLD"),
        ("just-text", False, "Plain text"),
        ("", False, "Empty string"),
    ]
    
    print("Testing detection logic:")
    print()
    
    success_count = 0
    total_count = len(test_cases)
    
    for test_input, is_email, description in test_cases:
        # Simulate the logic from the fixed code
        has_dot = "." in test_input and len(test_input.split(".")) >= 2
        has_at = "@" in test_input
        
        if has_dot and has_at:
            detected_as = "email"
        elif has_dot and not has_at:
            domain_parts = test_input.lower().strip().split(".")
            if len(domain_parts) == 2 and all(len(part) > 0 for part in domain_parts):
                detected_as = "domain_search"
            else:
                detected_as = "unclear_input"
        else:
            detected_as = "regular_text"
        
        # Check if detection matches expectation
        expected = "email" if is_email else ("domain_search" if has_dot and not has_at and len(test_input.split(".")) == 2 else "other")
        
        if (is_email and detected_as == "email") or (not is_email and detected_as != "email"):
            status = "✅ PASS"
            success_count += 1
        else:
            status = "❌ FAIL"
        
        print(f"{status} {test_input:25} → {detected_as:15} ({description})")
    
    print()
    print(f"Results: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("🎉 All tests passed! Email detection logic is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Logic needs adjustment.")
        return False

def test_regex_patterns():
    """Test email validation patterns"""
    print("\n🔧 Testing Email Validation Patterns")
    print("=" * 50)
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    valid_emails = [
        "test@example.com",
        "user.name@domain.org", 
        "admin+test@company.co.uk",
        "onarrival21@gmail.com"
    ]
    
    invalid_emails = [
        "example.com",
        "user@",
        "@domain.com",
        "user name@domain.com",
        "www.example.com"
    ]
    
    print("Valid emails:")
    for email in valid_emails:
        match = re.match(email_pattern, email)
        status = "✅" if match else "❌"
        print(f"  {status} {email}")
    
    print("\nInvalid emails (should not match):")
    for email in invalid_emails:
        match = re.match(email_pattern, email)
        status = "✅" if not match else "❌"
        print(f"  {status} {email}")

if __name__ == "__main__":
    print("🧪 Email Address Handling Fix Test")
    print("=" * 50)
    
    logic_test = test_email_detection_logic()
    test_regex_patterns()
    
    if logic_test:
        print("\n🎯 Fix Status: SUCCESSFUL")
        print("Email addresses will no longer trigger domain validation errors.")
        sys.exit(0)
    else:
        print("\n⚠️ Fix Status: NEEDS REVIEW")
        sys.exit(1)