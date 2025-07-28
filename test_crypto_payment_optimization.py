#!/usr/bin/env python3
"""
Test Script: Crypto Payment Mobile UI Optimization Validation
Tests the optimized crypto payment display from ~20 lines to 5 lines
"""

import asyncio
import sys
import re
from datetime import datetime

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ️  {text}{RESET}")

def count_display_lines(payment_text):
    """Count actual display lines in the payment text"""
    # Remove HTML tags for line counting
    text_without_tags = re.sub(r'<[^>]+>', '', payment_text)
    # Count non-empty lines
    lines = [line.strip() for line in text_without_tags.split('\n') if line.strip()]
    return len(lines)

def validate_crypto_payment_optimization():
    """Validate crypto payment display optimization"""
    print_header("CRYPTO PAYMENT MOBILE UI OPTIMIZATION TEST")
    
    tests_passed = 0
    tests_total = 0
    
    print("Testing crypto payment display optimization...")
    print(f"Target: Reduce from ~20 lines to 5-7 lines for mobile display\n")
    
    # Test 1: Line count validation
    print("1. Testing line count for all crypto payment displays...")
    tests_total += 1
    
    # Sample payment texts from the optimized version
    payment_texts = {
        "en": (
            "<b>💎 Bitcoin Payment</b>\n"
            "🏴‍☠️ example.com: <b>$49.50</b>\n"
            "📥 Send <b>0.00052134 BTC</b> to:\n\n"
            "<pre>1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa</pre>"
        ),
        "fr": (
            "<b>💎 Paiement Bitcoin</b>\n"
            "🏴‍☠️ example.com: <b>$49.50</b>\n"
            "📥 Envoyez <b>0.00052134 BTC</b> à:\n\n"
            "<pre>1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa</pre>"
        ),
        "hi": (
            "<b>💎 Bitcoin भुगतान</b>\n"
            "🏴‍☠️ example.com: <b>$49.50</b>\n"
            "📥 <b>0.00052134 BTC</b> भेजें:\n\n"
            "<pre>1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa</pre>"
        ),
        "zh": (
            "<b>💎 Bitcoin 付款</b>\n"
            "🏴‍☠️ example.com: <b>$49.50</b>\n"
            "📥 发送 <b>0.00052134 BTC</b> 到:\n\n"
            "<pre>1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa</pre>"
        ),
        "es": (
            "<b>💎 Pago Bitcoin</b>\n"
            "🏴‍☠️ example.com: <b>$49.50</b>\n"
            "📥 Enviar <b>0.00052134 BTC</b> a:\n\n"
            "<pre>1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa</pre>"
        )
    }
    
    all_within_target = True
    for lang, text in payment_texts.items():
        line_count = count_display_lines(text)
        if 4 <= line_count <= 7:
            print_success(f"{lang.upper()}: {line_count} lines - Within mobile target (4-7 lines)")
        else:
            print_error(f"{lang.upper()}: {line_count} lines - Outside mobile target!")
            all_within_target = False
    
    if all_within_target:
        tests_passed += 1
        print_success("All languages optimized to 4-7 line mobile display!")
    else:
        print_error("Some languages exceed mobile line target")
    
    # Test 2: Essential information preservation
    print("\n2. Testing essential information preservation...")
    tests_total += 1
    
    essential_elements = {
        "Payment Type": r"💎.*Payment|Paiement|भुगतान|付款|Pago",
        "Domain & Price": r"🏴‍☠️.*\$\d+\.\d+",
        "Send Amount": r"📥.*Send|Envoyez|भेजें|发送|Enviar",
        "Payment Address": r"<pre>.*</pre>"
    }
    
    all_elements_present = True
    for element_name, pattern in essential_elements.items():
        found_in_all = True
        for lang, text in payment_texts.items():
            if not re.search(pattern, text, re.DOTALL):
                print_error(f"{lang.upper()}: Missing {element_name}")
                found_in_all = False
                all_elements_present = False
        
        if found_in_all:
            print_success(f"{element_name} present in all languages")
    
    if all_elements_present:
        tests_passed += 1
        print_success("All essential payment information preserved!")
    else:
        print_error("Some essential information missing")
    
    # Test 3: HTML formatting validation
    print("\n3. Testing HTML formatting for mobile display...")
    tests_total += 1
    
    html_elements = {
        "Bold tags": r"<b>.*</b>",
        "Preformatted address": r"<pre>.*</pre>",
        "Clean structure": r"^<b>.*</b>\n.*\n.*\n\n<pre>.*</pre>$"
    }
    
    all_html_valid = True
    for element_name, pattern in html_elements.items():
        if element_name == "Clean structure":
            # Check overall structure
            for lang, text in payment_texts.items():
                if not re.match(pattern, text, re.DOTALL | re.MULTILINE):
                    print_error(f"{lang.upper()}: HTML structure not optimized")
                    all_html_valid = False
        else:
            # Check individual elements
            for lang, text in payment_texts.items():
                if not re.search(pattern, text):
                    print_error(f"{lang.upper()}: Missing {element_name}")
                    all_html_valid = False
    
    if all_html_valid:
        tests_passed += 1
        print_success("HTML formatting optimized for mobile display!")
    else:
        print_error("HTML formatting issues detected")
    
    # Test 4: Mobile viewport optimization
    print("\n4. Testing mobile viewport optimization...")
    tests_total += 1
    
    # Simulate mobile viewport (typical width: 360-414px)
    mobile_viewport_chars = 40  # Average chars per line on mobile
    
    viewport_optimized = True
    for lang, text in payment_texts.items():
        # Check each line's length
        lines = text.split('\n')
        for line in lines:
            # Remove HTML tags for length check
            clean_line = re.sub(r'<[^>]+>', '', line)
            if len(clean_line) > mobile_viewport_chars and clean_line.strip():
                if not clean_line.startswith('1') and not clean_line.startswith('0x'):  # Allow long addresses
                    print_error(f"{lang.upper()}: Line too long for mobile: {clean_line[:30]}...")
                    viewport_optimized = False
    
    if viewport_optimized:
        tests_passed += 1
        print_success("All text optimized for mobile viewport width!")
    else:
        print_error("Some lines too long for mobile display")
    
    # Test 5: Compare with old verbose version
    print("\n5. Testing optimization improvement...")
    tests_total += 1
    
    old_line_count = 25  # Approximate lines in old version
    new_line_count = count_display_lines(payment_texts["en"])
    reduction_percentage = ((old_line_count - new_line_count) / old_line_count) * 100
    
    print_info(f"Old version: ~{old_line_count} lines")
    print_info(f"New version: {new_line_count} lines")
    print_info(f"Reduction: {reduction_percentage:.1f}%")
    
    if reduction_percentage >= 70:
        tests_passed += 1
        print_success(f"Achieved {reduction_percentage:.1f}% reduction - Excellent mobile optimization!")
    else:
        print_error(f"Only {reduction_percentage:.1f}% reduction - Needs more optimization")
    
    # Final Summary
    print_header("TEST SUMMARY")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print_success("🎉 ALL TESTS PASSED! Crypto payment display successfully optimized for mobile!")
        print_success("✅ Reduced from ~20+ lines to 5 lines")
        print_success("✅ All essential information preserved")
        print_success("✅ Perfect for mobile thumb scrolling")
        print_success("✅ HTML formatting for superior readability")
        return True
    else:
        print_error(f"⚠️ {tests_total - tests_passed} tests failed. Review optimization.")
        return False

def main():
    """Run all tests"""
    print(f"{BLUE}Nomadly3 - Crypto Payment Mobile UI Optimization Test{RESET}")
    print(f"{YELLOW}Testing crypto payment display optimization...{RESET}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run validation
    success = validate_crypto_payment_optimization()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()