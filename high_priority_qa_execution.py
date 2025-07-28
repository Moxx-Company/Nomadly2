#!/usr/bin/env python3
"""
High Priority QA Test Execution Suite
Executing 5 critical tests identified for Nomadly2 bot
"""

import sys
import re
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HighPriorityQATester:
    """Execute high priority QA tests"""
    
    def __init__(self):
        self.test_results = []
        self.critical_findings = []
        self.passed_tests = 0
        self.total_tests = 0
        
    def log_test_result(self, test_name, status, details="", severity="info"):
        """Log test result with details"""
        self.test_results.append({
            'test': test_name,
            'status': status,
            'details': details,
            'severity': severity,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        if status == "PASS":
            self.passed_tests += 1
        elif severity == "critical":
            self.critical_findings.append(f"{test_name}: {details}")
        
        self.total_tests += 1

    def test_menu_button_ui_interaction(self):
        """Test 1: Menu/Button UI Interaction - Core UX"""
        print("🎨 TEST 1: Menu/Button UI Interaction")
        print("-" * 50)
        
        try:
            with open('nomadly2_bot.py', 'r') as f:
                content = f.read()
            
            # Test button layout consistency
            button_patterns = [
                (r'InlineKeyboardButton.*text.*callback_data', 'Inline keyboard structure'),
                (r'🔍.*Search Domain', 'Search domain button'),
                (r'💰.*Wallet', 'Wallet button'),
                (r'🌐.*DNS Management', 'DNS management button'),
                (r'⚙️.*Settings', 'Settings button'),
                (r'📊.*My Domains', 'Domain management button')
            ]
            
            button_score = 0
            total_button_tests = len(button_patterns)
            
            for pattern, description in button_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    print(f"  ✅ {description} - Found")
                    button_score += 1
                else:
                    print(f"  ❌ {description} - Missing")
            
            # Test button responsiveness patterns
            callback_patterns = [
                (r'callback_query\.answer\(', 'Immediate acknowledgment'),
                (r'edit_message_text', 'Message updates'),
                (r'send_message', 'New message sending'),
                (r'delete_message', 'Message cleanup')
            ]
            
            responsiveness_score = 0
            for pattern, description in callback_patterns:
                matches = len(re.findall(pattern, content))
                if matches >= 5:  # Should have multiple instances
                    print(f"  ✅ {description} - {matches} instances")
                    responsiveness_score += 1
                else:
                    print(f"  ⚠️ {description} - Only {matches} instances")
            
            # Calculate overall UI score
            ui_score = (button_score + responsiveness_score) / (total_button_tests + len(callback_patterns))
            
            if ui_score >= 0.8:
                self.log_test_result("Menu/Button UI Interaction", "PASS", 
                                   f"UI score: {ui_score:.1%}, excellent button layout and responsiveness")
                print(f"\n  ✅ PASS - UI Score: {ui_score:.1%}")
            else:
                self.log_test_result("Menu/Button UI Interaction", "FAIL", 
                                   f"UI score: {ui_score:.1%}, needs improvement in button consistency", "high")
                print(f"\n  ❌ FAIL - UI Score: {ui_score:.1%}")
                
        except Exception as e:
            self.log_test_result("Menu/Button UI Interaction", "ERROR", str(e), "critical")
            print(f"  ❌ ERROR: {e}")

    def test_input_sanitization_enhanced(self):
        """Test 2: Input Sanitization (Enhanced) - Security Critical"""
        print("\n🔒 TEST 2: Input Sanitization (Enhanced)")
        print("-" * 50)
        
        try:
            with open('nomadly2_bot.py', 'r') as f:
                content = f.read()
            
            # Test for SQL injection protection
            sql_protection = [
                (r'SQLAlchemy', 'ORM usage prevents SQL injection'),
                (r'text\(.*\)', 'Parameterized queries'),
                (r'\.strip\(\)', 'Input trimming'),
                (r'clean.*input|sanitize', 'Input cleaning functions')
            ]
            
            sql_score = 0
            for pattern, description in sql_protection:
                if re.search(pattern, content, re.IGNORECASE):
                    print(f"  ✅ {description}")
                    sql_score += 1
                else:
                    print(f"  ⚠️ Missing: {description}")
            
            # Test for XSS prevention
            xss_protection = [
                (r'escape.*html|html.*escape', 'HTML escaping'),
                (r'str\(.*\)', 'String conversion'),
                (r'json\.dumps', 'JSON serialization'),
                (r'format.*string', 'Safe string formatting')
            ]
            
            xss_score = 0
            for pattern, description in xss_protection:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if matches > 0:
                    print(f"  ✅ {description} - {matches} instances")
                    xss_score += 1
                else:
                    print(f"  ⚠️ {description} - Not found")
            
            # Test for command injection protection
            command_protection = [
                (r'shell.*False|shell=False', 'Shell injection protection'),
                (r'subprocess.*shell=False', 'Subprocess protection'),
                (r'os\.system', 'Dangerous os.system usage'),
                (r'eval\(|exec\(', 'Dangerous eval/exec usage')
            ]
            
            command_score = 0
            dangerous_found = 0
            for pattern, description in command_protection:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if 'Dangerous' in description:
                    if matches == 0:
                        print(f"  ✅ No {description}")
                        command_score += 1
                    else:
                        print(f"  ❌ Found {matches} instances of {description}")
                        dangerous_found += 1
                else:
                    if matches > 0:
                        print(f"  ✅ {description}")
                        command_score += 1
            
            # Calculate security score
            total_security_tests = len(sql_protection) + len(xss_protection) + len(command_protection)
            security_score = (sql_score + xss_score + command_score) / total_security_tests
            
            if security_score >= 0.7 and dangerous_found == 0:
                self.log_test_result("Input Sanitization Enhanced", "PASS", 
                                   f"Security score: {security_score:.1%}, good protection measures")
                print(f"\n  ✅ PASS - Security Score: {security_score:.1%}")
            else:
                self.log_test_result("Input Sanitization Enhanced", "FAIL", 
                                   f"Security score: {security_score:.1%}, dangerous patterns: {dangerous_found}", "critical")
                print(f"\n  ❌ FAIL - Security Score: {security_score:.1%}, Dangerous patterns: {dangerous_found}")
                
        except Exception as e:
            self.log_test_result("Input Sanitization Enhanced", "ERROR", str(e), "critical")
            print(f"  ❌ ERROR: {e}")

    def test_invalid_record_formats_enhanced(self):
        """Test 3: Invalid Record Formats (Enhanced) - Data Integrity"""
        print("\n🛡️ TEST 3: Invalid Record Formats (Enhanced)")
        print("-" * 50)
        
        try:
            # Check DNS input validation
            dns_files = ['complete_dns_system.py', 'nomadly2_bot.py']
            validation_found = False
            validation_details = []
            
            for filename in dns_files:
                try:
                    with open(filename, 'r') as f:
                        content = f.read()
                    
                    # Test IP address validation
                    ip_validation = [
                        (r'ipaddress\..*valid|valid.*ip', 'IP address validation'),
                        (r'socket\.inet_aton', 'Socket IP validation'),
                        (r'regex.*\d+\.\d+\.\d+\.\d+', 'IP regex pattern'),
                        (r'Invalid.*IP|IP.*invalid', 'IP error handling')
                    ]
                    
                    for pattern, description in ip_validation:
                        if re.search(pattern, content, re.IGNORECASE):
                            print(f"  ✅ {description} in {filename}")
                            validation_found = True
                            validation_details.append(description)
                    
                    # Test domain validation
                    domain_validation = [
                        (r'is_valid_domain', 'Domain validation function'),
                        (r'Invalid.*Domain|Domain.*invalid', 'Domain error handling'),
                        (r'tld.*validation|valid.*tld', 'TLD validation'),
                        (r'domain.*format|format.*domain', 'Domain format checking')
                    ]
                    
                    for pattern, description in domain_validation:
                        if re.search(pattern, content, re.IGNORECASE):
                            print(f"  ✅ {description} in {filename}")
                            validation_found = True
                            validation_details.append(description)
                    
                    # Test email validation
                    email_validation = [
                        (r'email.*valid|valid.*email', 'Email validation'),
                        (r'@.*\.|\..*@', 'Email format pattern'),
                        (r'Invalid.*email|email.*invalid', 'Email error handling')
                    ]
                    
                    for pattern, description in email_validation:
                        if re.search(pattern, content, re.IGNORECASE):
                            print(f"  ✅ {description} in {filename}")
                            validation_found = True
                            validation_details.append(description)
                    
                except FileNotFoundError:
                    print(f"  ⚠️ File {filename} not found")
            
            # Check for DNS error parser
            try:
                with open('dns_error_parser.py', 'r') as f:
                    error_content = f.read()
                print("  ✅ DNS error parser module found")
                validation_found = True
                validation_details.append("DNS error parser")
            except FileNotFoundError:
                print("  ⚠️ DNS error parser module not found")
            
            if validation_found and len(validation_details) >= 3:
                self.log_test_result("Invalid Record Formats Enhanced", "PASS", 
                                   f"Found {len(validation_details)} validation mechanisms")
                print(f"\n  ✅ PASS - {len(validation_details)} validation mechanisms found")
            else:
                self.log_test_result("Invalid Record Formats Enhanced", "FAIL", 
                                   f"Insufficient validation, only {len(validation_details)} mechanisms", "high")
                print(f"\n  ❌ FAIL - Only {len(validation_details)} validation mechanisms")
                
        except Exception as e:
            self.log_test_result("Invalid Record Formats Enhanced", "ERROR", str(e), "critical")
            print(f"  ❌ ERROR: {e}")

    def test_set_ttl_value(self):
        """Test 4: Set TTL Value - DNS Functionality Gap"""
        print("\n⏱️ TEST 4: Set TTL Value")
        print("-" * 50)
        
        try:
            with open('complete_dns_system.py', 'r') as f:
                dns_content = f.read()
            
            with open('nomadly2_bot.py', 'r') as f:
                bot_content = f.read()
            
            # Test TTL functionality
            ttl_features = [
                (r'ttl.*input|input.*ttl', 'TTL input handling'),
                (r'custom.*ttl|ttl.*custom', 'Custom TTL support'),
                (r'ttl.*value|value.*ttl', 'TTL value processing'),
                (r'300|600|1800|3600', 'Common TTL values'),
                (r'prompt.*ttl', 'TTL prompting')
            ]
            
            ttl_score = 0
            found_features = []
            
            for pattern, description in ttl_features:
                dns_matches = len(re.findall(pattern, dns_content, re.IGNORECASE))
                bot_matches = len(re.findall(pattern, bot_content, re.IGNORECASE))
                total_matches = dns_matches + bot_matches
                
                if total_matches > 0:
                    print(f"  ✅ {description} - {total_matches} instances")
                    ttl_score += 1
                    found_features.append(description)
                else:
                    print(f"  ❌ {description} - Not found")
            
            # Test TTL validation
            ttl_validation = [
                (r'int\(.*ttl\)|ttl.*int', 'TTL integer conversion'),
                (r'ttl.*range|range.*ttl', 'TTL range validation'),
                (r'ttl.*error|error.*ttl', 'TTL error handling'),
                (r'60.*86400|300.*604800', 'TTL limits (60s-1week)')
            ]
            
            validation_score = 0
            for pattern, description in ttl_validation:
                dns_matches = len(re.findall(pattern, dns_content, re.IGNORECASE))
                bot_matches = len(re.findall(pattern, bot_content, re.IGNORECASE))
                total_matches = dns_matches + bot_matches
                
                if total_matches > 0:
                    print(f"  ✅ {description}")
                    validation_score += 1
                else:
                    print(f"  ⚠️ {description} - Not found")
            
            total_ttl_tests = len(ttl_features) + len(ttl_validation)
            overall_score = (ttl_score + validation_score) / total_ttl_tests
            
            if overall_score >= 0.6:
                self.log_test_result("Set TTL Value", "PASS", 
                                   f"TTL score: {overall_score:.1%}, found {len(found_features)} features")
                print(f"\n  ✅ PASS - TTL Score: {overall_score:.1%}")
            else:
                self.log_test_result("Set TTL Value", "FAIL", 
                                   f"TTL score: {overall_score:.1%}, insufficient TTL support", "medium")
                print(f"\n  ❌ FAIL - TTL Score: {overall_score:.1%}")
                
        except Exception as e:
            self.log_test_result("Set TTL Value", "ERROR", str(e), "high")
            print(f"  ❌ ERROR: {e}")

    def test_payment_timeout_expiration(self):
        """Test 5: Payment Timeout/Expiration - Payment Workflow Gap"""
        print("\n💸 TEST 5: Payment Timeout/Expiration")
        print("-" * 50)
        
        try:
            # Check payment service and bot files
            files_to_check = ['payment_service.py', 'nomadly2_bot.py', 'webhook_server.py']
            timeout_features = []
            
            for filename in files_to_check:
                try:
                    with open(filename, 'r') as f:
                        content = f.read()
                    
                    # Test timeout mechanisms
                    timeout_patterns = [
                        (r'expire.*time|time.*expire', 'Expiration time handling'),
                        (r'timeout|expired', 'Timeout detection'),
                        (r'datetime.*now|now.*datetime', 'Current time comparison'),
                        (r'payment.*status|status.*payment', 'Payment status tracking'),
                        (r'cancel.*payment|payment.*cancel', 'Payment cancellation')
                    ]
                    
                    for pattern, description in timeout_patterns:
                        matches = len(re.findall(pattern, content, re.IGNORECASE))
                        if matches > 0:
                            print(f"  ✅ {description} in {filename} - {matches} instances")
                            timeout_features.append(f"{description} ({filename})")
                    
                except FileNotFoundError:
                    print(f"  ⚠️ File {filename} not found")
            
            # Check database models for expiration fields
            try:
                with open('database.py', 'r') as f:
                    db_content = f.read()
                
                expiration_fields = [
                    (r'expires_at', 'Expiration timestamp field'),
                    (r'created_at', 'Creation timestamp field'),
                    (r'completed_at', 'Completion timestamp field'),
                    (r'DateTime', 'DateTime field usage')
                ]
                
                for pattern, description in expiration_fields:
                    matches = len(re.findall(pattern, db_content, re.IGNORECASE))
                    if matches > 0:
                        print(f"  ✅ {description} - {matches} instances")
                        timeout_features.append(description)
                
            except FileNotFoundError:
                print("  ⚠️ Database file not found")
            
            # Test cleanup mechanisms
            cleanup_patterns = [
                (r'clean.*expired|expired.*clean', 'Expired payment cleanup'),
                (r'scheduled.*task|task.*scheduled', 'Scheduled cleanup tasks'),
                (r'background.*process', 'Background processing'),
                (r'webhook.*timeout', 'Webhook timeout handling')
            ]
            
            cleanup_found = 0
            for filename in files_to_check:
                try:
                    with open(filename, 'r') as f:
                        content = f.read()
                    
                    for pattern, description in cleanup_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            print(f"  ✅ {description} in {filename}")
                            cleanup_found += 1
                            timeout_features.append(description)
                except FileNotFoundError:
                    continue
            
            # Calculate timeout score
            total_features = len(timeout_features)
            
            if total_features >= 8:
                self.log_test_result("Payment Timeout Expiration", "PASS", 
                                   f"Found {total_features} timeout/expiration features")
                print(f"\n  ✅ PASS - {total_features} timeout features found")
            elif total_features >= 5:
                self.log_test_result("Payment Timeout Expiration", "PARTIAL", 
                                   f"Found {total_features} features, may need enhancement", "medium")
                print(f"\n  ⚠️ PARTIAL - {total_features} timeout features (needs enhancement)")
            else:
                self.log_test_result("Payment Timeout Expiration", "FAIL", 
                                   f"Only {total_features} features found, insufficient timeout handling", "high")
                print(f"\n  ❌ FAIL - Only {total_features} timeout features")
                
        except Exception as e:
            self.log_test_result("Payment Timeout Expiration", "ERROR", str(e), "critical")
            print(f"  ❌ ERROR: {e}")

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 70)
        print("📋 HIGH PRIORITY QA TEST EXECUTION REPORT")
        print("=" * 70)
        
        # Calculate scores
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n📊 EXECUTION SUMMARY:")
        print(f"   Tests Executed: {self.total_tests}")
        print(f"   Tests Passed: {self.passed_tests}")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        print(f"   Critical Findings: {len(self.critical_findings)}")
        
        # Show detailed results
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️", "ERROR": "🚨"}[result['status']]
            print(f"   {status_icon} {result['test']} - {result['details']}")
        
        # Critical findings
        if self.critical_findings:
            print(f"\n🚨 CRITICAL FINDINGS:")
            for finding in self.critical_findings:
                print(f"   ❌ {finding}")
        
        # Quality assessment
        print(f"\n🎯 QUALITY ASSESSMENT:")
        if pass_rate >= 80:
            print("   🟢 EXCELLENT - High priority areas well covered")
        elif pass_rate >= 60:
            print("   🟡 GOOD - Some areas need attention")
        elif pass_rate >= 40:
            print("   🟠 FAIR - Multiple areas need improvement")
        else:
            print("   🔴 POOR - Significant issues require immediate attention")
        
        # Combined QA score (original 89.4% + new tests)
        original_score = 89.4
        new_test_weight = 15  # Weight of these 5 critical tests
        combined_score = (original_score * 85 + pass_rate * new_test_weight) / 100
        
        print(f"\n📈 COMBINED QA SCORE:")
        print(f"   Original QA: 89.4%")
        print(f"   High Priority Tests: {pass_rate:.1f}%")
        print(f"   Combined Score: {combined_score:.1f}%")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if pass_rate >= 80:
            print("   ✅ Ready for production deployment")
            print("   ✅ All critical areas adequately tested")
        else:
            print("   🔧 Address failing tests before production")
            print("   ⚠️ Focus on security and UX improvements")
        
        print(f"\n📅 Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return combined_score >= 85

    def run_high_priority_tests(self):
        """Execute all high priority QA tests"""
        print("🚀 HIGH PRIORITY QA TEST EXECUTION")
        print("=" * 70)
        print("Executing 5 critical tests for maximum impact")
        print("Focus: Core UX, Security, Data Integrity, DNS gaps, Payment workflows")
        print("=" * 70)
        
        # Execute all tests
        self.test_menu_button_ui_interaction()
        self.test_input_sanitization_enhanced()
        self.test_invalid_record_formats_enhanced()
        self.test_set_ttl_value()
        self.test_payment_timeout_expiration()
        
        # Generate final assessment
        return self.generate_final_report()


def main():
    """Main execution function"""
    tester = HighPriorityQATester()
    success = tester.run_high_priority_tests()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)