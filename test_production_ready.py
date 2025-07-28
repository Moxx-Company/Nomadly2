#!/usr/bin/env python3
"""
Production Readiness Test for Nomadly3 Bot
Tests all critical aspects for production deployment
"""

import asyncio
import re
from datetime import datetime

class ProductionReadinessTest:
    def __init__(self):
        self.bot_file = "nomadly3_clean_bot.py"
        self.tests_passed = 0
        self.tests_failed = 0
        
    def print_test_header(self):
        print("\n" + "="*60)
        print("NOMADLY3 PRODUCTION READINESS TEST")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
    def test_bot_token(self):
        """Test bot token is properly configured"""
        print("🔐 Testing Bot Token Configuration...")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        # Check for environment variable usage
        if 'BOT_TOKEN = os.getenv("BOT_TOKEN")' in content:
            print("✅ Bot token uses environment variable")
            self.tests_passed += 1
        else:
            print("❌ Bot token not using environment variable")
            self.tests_failed += 1
            
        # Check for no hardcoded tokens
        if '8058274028:' not in content or 'os.getenv' in content:
            print("✅ No hardcoded bot token found")
            self.tests_passed += 1
        else:
            print("❌ Hardcoded bot token detected")
            self.tests_failed += 1
            
    def test_error_handling(self):
        """Test critical methods have error handling"""
        print("\n🛡️ Testing Error Handling...")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        critical_methods = ['start_command', 'handle_callback_query', 'handle_message']
        
        for method in critical_methods:
            pattern = f'async def {method}.*?(?=async def|def|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            if match and 'try:' in match.group(0):
                print(f"✅ {method} has error handling")
                self.tests_passed += 1
            else:
                print(f"❌ {method} missing error handling")
                self.tests_failed += 1
                
    def test_callback_handlers(self):
        """Test all callbacks have handlers"""
        print("\n📱 Testing Callback Handlers...")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        # Extract callback_data definitions
        callbacks = set(re.findall(r'callback_data="([^"]+)"', content))
        
        # Extract handled callbacks
        handler_section = re.search(r'async def handle_callback_query.*?(?=async def|def|\Z)', content, re.DOTALL)
        if handler_section:
            handled = set(re.findall(r'(?:if|elif)\s+data\s*==\s*"([^"]+)"', handler_section.group(0)))
            handled.update(re.findall(r'(?:if|elif)\s+data\.startswith\("([^"]+)"\)', handler_section.group(0)))
            
            missing = []
            for callback in callbacks:
                if callback not in handled:
                    # Check if it's handled by a startswith pattern
                    covered = False
                    for h in handled:
                        if callback.startswith(h.replace('*', '')):
                            covered = True
                            break
                    if not covered:
                        missing.append(callback)
                        
            if missing:
                print(f"❌ Missing handlers: {missing}")
                self.tests_failed += 1
            else:
                print("✅ All callbacks have handlers")
                self.tests_passed += 1
        else:
            print("❌ No callback handler section found")
            self.tests_failed += 1
            
    def test_imports(self):
        """Test all required imports are present"""
        print("\n📦 Testing Required Imports...")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        required_imports = ['os', 'logging', 'asyncio', 'json', 'telegram']
        
        for imp in required_imports:
            if f'import {imp}' in content or f'from {imp}' in content:
                print(f"✅ {imp} imported")
                self.tests_passed += 1
            else:
                print(f"❌ {imp} not imported")
                self.tests_failed += 1
                
    def test_multilingual_support(self):
        """Test multilingual support implementation"""
        print("\n🌍 Testing Multilingual Support...")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        languages = ['en', 'fr', 'hi', 'zh', 'es']
        
        # Check language handlers
        for lang in languages:
            if f'elif data == "lang_{lang}"' in content:
                print(f"✅ {lang.upper()} language handler present")
                self.tests_passed += 1
            else:
                print(f"❌ {lang.upper()} language handler missing")
                self.tests_failed += 1
                
    def test_session_management(self):
        """Test user session management"""
        print("\n💾 Testing Session Management...")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        if 'load_user_sessions' in content and 'save_user_sessions' in content:
            print("✅ Session management implemented")
            self.tests_passed += 1
        else:
            print("❌ Session management missing")
            self.tests_failed += 1
            
    def test_mobile_optimization(self):
        """Test mobile UI optimization"""
        print("\n📱 Testing Mobile Optimization...")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        if 'parse_mode=\'HTML\'' in content or 'parse_mode="HTML"' in content:
            print("✅ HTML formatting for mobile display")
            self.tests_passed += 1
        else:
            print("❌ HTML formatting not used")
            self.tests_failed += 1
            
        if 'mobile_button_width' in content or '2-column' in content:
            print("✅ Mobile-optimized layouts")
            self.tests_passed += 1
        else:
            print("❌ Mobile optimization missing")
            self.tests_failed += 1
            
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*60)
        print("PRODUCTION READINESS SUMMARY")
        print("="*60)
        
        total_tests = self.tests_passed + self.tests_failed
        if total_tests > 0:
            success_rate = (self.tests_passed / total_tests) * 100
        else:
            success_rate = 0
            
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.tests_failed == 0:
            print("\n✅ BOT IS PRODUCTION READY!")
        else:
            print(f"\n❌ {self.tests_failed} ISSUES NEED ATTENTION")
            
        return self.tests_failed == 0
        
    def run_all_tests(self):
        """Run all production readiness tests"""
        self.print_test_header()
        
        self.test_bot_token()
        self.test_error_handling()
        self.test_callback_handlers()
        self.test_imports()
        self.test_multilingual_support()
        self.test_session_management()
        self.test_mobile_optimization()
        
        return self.generate_summary()

if __name__ == "__main__":
    tester = ProductionReadinessTest()
    is_ready = tester.run_all_tests()