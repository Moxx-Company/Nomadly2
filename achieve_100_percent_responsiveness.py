#!/usr/bin/env python3
"""
Comprehensive Button Responsiveness Analyzer & Auto-Fixer
Goal: Achieve 100% button responsiveness by detecting and fixing all missing acknowledgments
"""

import re
import os


def analyze_callback_handlers():
    """Analyze nomadly2_bot.py for all callback handlers and missing acknowledgments"""
    print("🚀 COMPREHENSIVE 100% RESPONSIVENESS ANALYZER")
    print("=" * 60)

    with open("nomadly2_bot.py", "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

    # Find all elif callback handlers
    callback_patterns = []
    missing_acknowledgments = []

    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # Look for elif statements that handle callbacks
        if line_stripped.startswith("elif data"):
            # Extract the callback pattern
            if ".startswith(" in line_stripped:
                pattern_match = re.search(
                    r'data\.startswith\(["\']([^"\']+)["\']', line_stripped
                )
                if pattern_match:
                    pattern = pattern_match.group(1)
                    callback_patterns.append((i, pattern, line_stripped))

                    # Check if next few lines have query.answer()
                    has_acknowledgment = False
                    for j in range(i, min(i + 5, len(lines))):
                        if "query.answer(" in lines[j]:
                            has_acknowledgment = True
                            break

                    if not has_acknowledgment:
                        missing_acknowledgments.append((i, pattern, line_stripped))

            elif "data ==" in line_stripped:
                # Handle exact matches like data == "support"
                pattern_match = re.search(r'data == ["\']([^"\']+)["\']', line_stripped)
                if pattern_match:
                    pattern = pattern_match.group(1)
                    callback_patterns.append((i, pattern, line_stripped))

                    # Check if next few lines have query.answer()
                    has_acknowledgment = False
                    for j in range(i, min(i + 5, len(lines))):
                        if "query.answer(" in lines[j]:
                            has_acknowledgment = True
                            break

                    if not has_acknowledgment:
                        missing_acknowledgments.append((i, pattern, line_stripped))

    print(f"📊 ANALYSIS RESULTS:")
    print(f"   • Total callback handlers: {len(callback_patterns)}")
    print(f"   • Missing acknowledgments: {len(missing_acknowledgments)}")
    print(
        f"   • Current responsiveness: {((len(callback_patterns) - len(missing_acknowledgments)) / len(callback_patterns) * 100):.1f}%"
    )

    if missing_acknowledgments:
        print(f"\n⚠️ HANDLERS WITHOUT ACKNOWLEDGMENT:")
        for line_num, pattern, line_content in missing_acknowledgments[:20]:
            print(f"   Line {line_num}: {pattern}")

    return missing_acknowledgments, callback_patterns


def generate_fixes(missing_acknowledgments):
    """Generate specific fixes for missing acknowledgments"""
    print(f"\n🔧 GENERATING AUTOMATIC FIXES")
    print("=" * 40)

    fixes = []

    # Map patterns to appropriate acknowledgment messages
    acknowledgment_map = {
        "refresh_status_": 'await query.answer("Checking status...")',
        "switch_crypto_": 'await query.answer("Loading options...")',
        "copy_addr_": 'await query.answer("Address copied!")',
        "copy_address_": 'await query.answer("Address copied!")',
        "create_crypto_": 'await query.answer("Creating payment...")',
        "crypto_": 'await query.answer("Loading crypto...")',
        "crypto_domain_": 'await query.answer("Creating payment...")',
        "crypto_custom_": 'await query.answer("Creating payment...")',
        "register_crypto_": 'await query.answer("Loading options...")',
        "pay_crypto_": 'await query.answer("Loading crypto...")',
        "pay_balance_": 'await query.answer("Processing payment...")',
        "dns_manage_": 'await query.answer("Loading DNS...")',
        "dns_view_": 'await query.answer("Loading records...")',
        "dns_status_": 'await query.answer("Checking status...")',
        "dns_add_a_": 'await query.answer("Adding record...")',
        "dns_custom_a_": 'await query.answer("Adding record...")',
        "dns_manual_a_": 'await query.answer("Adding record...")',
        "dns_quick_a_root_": 'await query.answer("Adding record...")',
        "check_payment_": 'await query.answer("Checking payment...")',
        "new_crypto_": 'await query.answer("Creating payment...")',
    }

    for line_num, pattern, line_content in missing_acknowledgments:
        # Find the best acknowledgment message
        acknowledgment = "await query.answer()"

        for map_pattern, map_ack in acknowledgment_map.items():
            if pattern.startswith(map_pattern) or map_pattern.startswith(pattern):
                acknowledgment = map_ack
                break

        fixes.append(
            {
                "line_num": line_num,
                "pattern": pattern,
                "acknowledgment": acknowledgment,
                "original_line": line_content,
            }
        )

        print(f"   • Line {line_num}: {pattern} → {acknowledgment}")

    return fixes


def apply_fixes(fixes):
    """Apply the fixes to nomadly2_bot.py"""
    print(f"\n⚡ APPLYING {len(fixes)} FIXES")
    print("=" * 30)

    with open("nomadly2_bot.py", "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Apply fixes in reverse order to maintain line numbers
    fixes_applied = 0
    fixes.sort(key=lambda x: x["line_num"], reverse=True)

    for fix in fixes:
        line_idx = fix["line_num"] - 1  # Convert to 0-based index

        if line_idx < len(lines):
            original_line = lines[line_idx]

            # Find the indentation of the elif line
            indent = len(original_line) - len(original_line.lstrip())
            acknowledgment_line = " " * (indent + 4) + fix["acknowledgment"] + "\n"

            # Insert the acknowledgment right after the elif line
            lines.insert(line_idx + 1, acknowledgment_line)
            fixes_applied += 1
            print(f"   ✅ Fixed line {fix['line_num']}: {fix['pattern']}")

    # Write the fixed content back
    with open("nomadly2_bot.py", "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n🎉 Applied {fixes_applied} fixes successfully!")
    return fixes_applied


def verify_responsiveness():
    """Verify the final responsiveness rate"""
    print(f"\n📊 FINAL VERIFICATION")
    print("=" * 25)

    missing_after, total_after = analyze_callback_handlers()

    final_rate = (
        ((len(total_after) - len(missing_after)) / len(total_after) * 100)
        if total_after
        else 100
    )

    print(f"\n🎯 FINAL RESULTS:")
    print(f"   • Total handlers: {len(total_after)}")
    print(f"   • Missing acknowledgments: {len(missing_after)}")
    print(f"   • Final responsiveness: {final_rate:.1f}%")

    if final_rate >= 95:
        print(f"   🎉 EXCELLENT! Near-perfect responsiveness achieved!")
    elif final_rate >= 90:
        print(f"   ✅ GREAT! High responsiveness achieved!")
    elif final_rate >= 80:
        print(f"   👍 GOOD! Solid responsiveness achieved!")
    else:
        print(f"   ⚠️ More work needed for optimal responsiveness")

    return final_rate


def main():
    """Main execution function"""
    print("🎯 GOAL: ACHIEVE 100% BUTTON RESPONSIVENESS")
    print("=" * 50)

    # Step 1: Analyze current state
    missing_acks, total_handlers = analyze_callback_handlers()

    if not missing_acks:
        print("🎉 Already at 100% responsiveness!")
        return

    # Step 2: Generate fixes
    fixes = generate_fixes(missing_acks)

    # Step 3: Apply fixes
    fixes_applied = apply_fixes(fixes)

    # Step 4: Verify results
    final_rate = verify_responsiveness()

    print(f"\n🚀 TRANSFORMATION COMPLETE!")
    print(f"   • Fixes applied: {fixes_applied}")
    print(f"   • Final responsiveness: {final_rate:.1f}%")

    if final_rate >= 95:
        print(f"   🎉 SUCCESS: Near-perfect button responsiveness achieved!")

    return final_rate


if __name__ == "__main__":
    main()
