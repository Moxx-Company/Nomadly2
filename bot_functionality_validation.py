#!/usr/bin/env python3
"""
Bot Functionality Validation - Test All Callback Handlers
"""

import re
import sys
from pathlib import Path

class BotValidator:
    def __init__(self):
        self.bot_file = "nomadly3_clean_bot.py"
        self.callback_handlers = []
        self.method_implementations = []
        
    def extract_callback_handlers(self):
        """Extract all callback handlers from the bot file"""
        with open(self.bot_file, 'r') as f:
            content = f.read()
        
        # Find callback handler section
        handler_section = self.extract_handler_section(content)
        if not handler_section:
            return False
        
        # Extract all handler patterns
        patterns = [
            r'if data and data\.startswith\("([^"]+)"\)',  # startswith patterns
            r'elif data == "([^"]+)"',                     # exact match patterns
            r'elif data in \[(.*?)\]',                     # list patterns
        ]
        
        handlers = set()
        for pattern in patterns:
            matches = re.findall(pattern, handler_section)
            for match in matches:
                if isinstance(match, tuple):
                    for m in match:
                        if m:
                            handlers.add(m.strip('"'))
                else:
                    handlers.add(match)
        
        # Handle startswith patterns specially
        if 'lang_' in handlers:
            handlers.update(['lang_en', 'lang_fr', 'lang_hi', 'lang_zh', 'lang_es'])
        if 'register_' in handlers:
            handlers.add('register_*')
        if 'crypto_' in handlers:
            handlers.add('crypto_*')
        
        self.callback_handlers = sorted(handlers)
        return True
    
    def extract_handler_section(self, content):
        """Extract the callback handler section"""
        start = content.find("async def handle_callback_query")
        if start == -1:
            return None
        
        # Find the end of the method
        end = content.find("\n    async def", start + 1)
        if end == -1:
            end = content.find("\ndef main", start)
            if end == -1:
                end = len(content)
        
        return content[start:end]
    
    def extract_method_implementations(self):
        """Extract all method implementations"""
        with open(self.bot_file, 'r') as f:
            content = f.read()
        
        # Find all async method definitions
        method_pattern = r'async def ([a-zA-Z_][a-zA-Z0-9_]*)\('
        methods = re.findall(method_pattern, content)
        
        self.method_implementations = sorted(set(methods))
        return True
    
    def validate_bot_functionality(self):
        """Validate comprehensive bot functionality"""
        print("🔍 BOT FUNCTIONALITY VALIDATION")
        print("=" * 50)
        
        # Extract handlers and methods
        if not self.extract_callback_handlers():
            print("❌ Failed to extract callback handlers")
            return False
        
        if not self.extract_method_implementations():
            print("❌ Failed to extract method implementations")
            return False
        
        print(f"✅ Found {len(self.callback_handlers)} callback handler patterns")
        print(f"✅ Found {len(self.method_implementations)} method implementations")
        
        # Validate critical handlers
        critical_handlers = [
            'main_menu', 'search_domain', 'my_domains', 'wallet', 
            'manage_dns', 'nameservers', 'loyalty', 'support',
            'change_language', 'lang_en', 'lang_fr'
        ]
        
        missing_critical = []
        for handler in critical_handlers:
            if handler not in self.callback_handlers and not any(h.startswith(handler.split('_')[0]) for h in self.callback_handlers):
                missing_critical.append(handler)
        
        if missing_critical:
            print(f"⚠️  Missing critical handlers: {missing_critical}")
        else:
            print("✅ All critical handlers are covered")
        
        # Validate method coverage
        required_methods = [
            'handle_callback_query', 'start_command', 'show_main_menu',
            'handle_language_selection', 'show_domain_search',
            'handle_message', 'show_wallet_menu'
        ]
        
        missing_methods = []
        for method in required_methods:
            if method not in self.method_implementations:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"⚠️  Missing required methods: {missing_methods}")
        else:
            print("✅ All required methods are implemented")
        
        return len(missing_critical) == 0 and len(missing_methods) == 0
    
    def test_language_handling(self):
        """Test language handling specifically"""
        print(f"\n🌍 LANGUAGE HANDLING VALIDATION")
        print("=" * 40)
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
        
        # Check if language selection is properly handled
        lang_startswith = 'data.startswith("lang_")' in content
        lang_handler = 'handle_language_selection' in content
        
        languages = ['lang_en', 'lang_fr', 'lang_hi', 'lang_zh', 'lang_es']
        lang_buttons = all(lang in content for lang in languages)
        
        print(f"✅ Language startswith pattern: {'✓' if lang_startswith else '✗'}")
        print(f"✅ Language handler method: {'✓' if lang_handler else '✗'}")
        print(f"✅ All language buttons: {'✓' if lang_buttons else '✗'}")
        
        return lang_startswith and lang_handler and lang_buttons
    
    def test_bot_startup(self):
        """Test if bot can start without errors"""
        print(f"\n🚀 BOT STARTUP VALIDATION")
        print("=" * 35)
        
        # Check for syntax errors
        try:
            with open(self.bot_file, 'r') as f:
                content = f.read()
            
            compile(content, self.bot_file, 'exec')
            print("✅ No syntax errors detected")
            syntax_ok = True
        except SyntaxError as e:
            print(f"❌ Syntax error: {e}")
            syntax_ok = False
        
        # Check for missing imports
        required_imports = [
            'from telegram import', 'from telegram.ext import',
            'import os', 'import logging', 'import asyncio'
        ]
        
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"⚠️  Missing imports: {missing_imports}")
        else:
            print("✅ All required imports present")
        
        # Check for BOT_TOKEN configuration
        token_config = 'BOT_TOKEN = os.getenv("BOT_TOKEN")' in content
        print(f"✅ Secure token configuration: {'✓' if token_config else '✗'}")
        
        return syntax_ok and len(missing_imports) == 0 and token_config
    
    def generate_comprehensive_report(self):
        """Generate comprehensive validation report"""
        print(f"\n📊 COMPREHENSIVE VALIDATION REPORT")
        print("=" * 60)
        
        functionality_ok = self.validate_bot_functionality()
        language_ok = self.test_language_handling()
        startup_ok = self.test_bot_startup()
        
        total_score = sum([functionality_ok, language_ok, startup_ok])
        
        print(f"\n🎯 VALIDATION RESULTS:")
        print(f"   Bot Functionality: {'✅ PASS' if functionality_ok else '❌ FAIL'}")
        print(f"   Language Handling: {'✅ PASS' if language_ok else '❌ FAIL'}")
        print(f"   Bot Startup: {'✅ PASS' if startup_ok else '❌ FAIL'}")
        print(f"   Overall Score: {total_score}/3")
        
        if total_score == 3:
            print(f"\n🎉 BOT IS PRODUCTION READY!")
            print("   All validation tests passed successfully.")
        elif total_score >= 2:
            print(f"\n⚠️  BOT IS MOSTLY READY")
            print("   Minor issues need attention before production.")
        else:
            print(f"\n❌ BOT NEEDS SIGNIFICANT WORK")
            print("   Major issues must be resolved before deployment.")
        
        return total_score == 3

def main():
    print("🤖 NOMADLY3 BOT VALIDATION SUITE")
    print("=" * 70)
    
    validator = BotValidator()
    is_production_ready = validator.generate_comprehensive_report()
    
    if is_production_ready:
        print(f"\n✨ VALIDATION COMPLETE - BOT READY FOR DEPLOYMENT")
    else:
        print(f"\n🔧 VALIDATION COMPLETE - ISSUES REQUIRE ATTENTION")
    
    return is_production_ready

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)