#!/usr/bin/env python3
"""
Test script to verify complete mobile UI optimization with HTML formatting
Tests all optimized screens to ensure they display correctly with HTML parse_mode
"""

import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nomadly3_clean_bot import NomadlyCleanBot

class TestMobileUIHTMLComplete:
    def __init__(self):
        self.bot = NomadlyCleanBot()
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def create_mock_query(self, user_id=123456789, callback_data="test"):
        """Create a mock query object for testing"""
        query = Mock()
        query.from_user = Mock()
        query.from_user.id = user_id
        query.from_user.username = "testuser"
        query.data = callback_data
        query.edit_message_text = AsyncMock()
        query.answer = AsyncMock()
        query.message = Mock()
        query.message.reply_text = AsyncMock()
        return query
        
    async def test_optimized_screens(self):
        """Test all optimized screens for mobile UI and HTML formatting"""
        print("\n🎯 Testing Complete Mobile UI Optimization with HTML Formatting\n")
        
        # Test 1: Domain Management Screen
        await self.test_domain_management()
        
        # Test 2: Website Control Screen
        await self.test_website_control()
        
        # Test 3: Portfolio Stats Screen
        await self.test_portfolio_stats()
        
        # Test 4: Mass DNS Update Screen
        await self.test_mass_dns_update()
        
        # Test 5: Access Control Screen
        await self.test_access_control()
        
        # Test 6: HTML Parse Mode Verification
        await self.test_html_parse_mode()
        
    async def test_domain_management(self):
        """Test domain management screen optimization"""
        print("📱 Test 1: Domain Management Screen Optimization")
        
        try:
            query = self.create_mock_query()
            await self.bot.handle_domain_management(query, "example.com")
            
            # Check if message was edited
            assert query.edit_message_text.called, "edit_message_text not called"
            
            # Get the message text
            call_args = query.edit_message_text.call_args
            message_text = call_args[0][0]
            
            # Verify compact format
            lines = message_text.strip().split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            print(f"   ✓ Lines count: {len(non_empty_lines)} (should be ~5-7)")
            print(f"   ✓ HTML tags present: {'<b>' in message_text}")
            
            # Check for HTML formatting
            assert '<b>' in message_text, "HTML formatting missing"
            assert len(non_empty_lines) <= 7, f"Too many lines: {len(non_empty_lines)}"
            
            # Check parse_mode
            parse_mode = call_args[1].get('parse_mode', '')
            assert parse_mode == 'HTML', f"Wrong parse_mode: {parse_mode}"
            
            self.passed_tests += 1
            print("   ✅ Domain Management: Mobile-optimized with HTML")
            
        except Exception as e:
            print(f"   ❌ Domain Management Error: {e}")
            
        self.total_tests += 1
        
    async def test_website_control(self):
        """Test website control screen optimization"""
        print("\n📱 Test 2: Website Control Screen Optimization")
        
        try:
            query = self.create_mock_query()
            await self.bot.handle_website_control(query, "example.com")
            
            call_args = query.edit_message_text.call_args
            message_text = call_args[0][0]
            
            lines = message_text.strip().split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            print(f"   ✓ Lines count: {len(non_empty_lines)} (should be ~4)")
            print(f"   ✓ Compact format: {len(message_text) < 200}")
            
            assert '<b>' in message_text, "HTML formatting missing"
            assert len(non_empty_lines) <= 5, f"Too many lines: {len(non_empty_lines)}"
            
            parse_mode = call_args[1].get('parse_mode', '')
            assert parse_mode == 'HTML', f"Wrong parse_mode: {parse_mode}"
            
            self.passed_tests += 1
            print("   ✅ Website Control: Mobile-optimized with HTML")
            
        except Exception as e:
            print(f"   ❌ Website Control Error: {e}")
            
        self.total_tests += 1
        
    async def test_portfolio_stats(self):
        """Test portfolio stats screen optimization"""
        print("\n📱 Test 3: Portfolio Stats Screen Optimization")
        
        try:
            query = self.create_mock_query()
            await self.bot.handle_portfolio_stats(query)
            
            call_args = query.edit_message_text.call_args
            message_text = call_args[0][0]
            
            lines = message_text.strip().split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            print(f"   ✓ Lines count: {len(non_empty_lines)} (should be ~4)")
            print(f"   ✓ Statistics condensed: {len(message_text) < 150}")
            
            assert '<b>' in message_text, "HTML formatting missing"
            assert len(non_empty_lines) <= 5, f"Too many lines: {len(non_empty_lines)}"
            
            parse_mode = call_args[1].get('parse_mode', '')
            assert parse_mode == 'HTML', f"Wrong parse_mode: {parse_mode}"
            
            self.passed_tests += 1
            print("   ✅ Portfolio Stats: Mobile-optimized with HTML")
            
        except Exception as e:
            print(f"   ❌ Portfolio Stats Error: {e}")
            
        self.total_tests += 1
        
    async def test_mass_dns_update(self):
        """Test mass DNS update screen optimization"""
        print("\n📱 Test 4: Mass DNS Update Screen Optimization")
        
        try:
            query = self.create_mock_query()
            await self.bot.handle_mass_dns_update(query)
            
            call_args = query.edit_message_text.call_args
            message_text = call_args[0][0]
            
            lines = message_text.strip().split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            print(f"   ✓ Lines count: {len(non_empty_lines)} (should be ~4)")
            print(f"   ✓ Bulk operations simplified: {'Select bulk operation' in message_text}")
            
            assert '<b>' in message_text, "HTML formatting missing"
            assert len(non_empty_lines) <= 5, f"Too many lines: {len(non_empty_lines)}"
            
            parse_mode = call_args[1].get('parse_mode', '')
            assert parse_mode == 'HTML', f"Wrong parse_mode: {parse_mode}"
            
            self.passed_tests += 1
            print("   ✅ Mass DNS Update: Mobile-optimized with HTML")
            
        except Exception as e:
            print(f"   ❌ Mass DNS Update Error: {e}")
            
        self.total_tests += 1
        
    async def test_access_control(self):
        """Test access control screen optimization"""
        print("\n📱 Test 5: Access Control Screen Optimization")
        
        try:
            query = self.create_mock_query()
            await self.bot.handle_access_control(query, "example.com")
            
            call_args = query.edit_message_text.call_args
            message_text = call_args[0][0]
            
            lines = message_text.strip().split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            print(f"   ✓ Lines count: {len(non_empty_lines)} (should be ~4)")
            print(f"   ✓ Security info condensed: {len(message_text) < 150}")
            
            assert '<b>' in message_text, "HTML formatting missing"
            assert len(non_empty_lines) <= 5, f"Too many lines: {len(non_empty_lines)}"
            
            parse_mode = call_args[1].get('parse_mode', '')
            assert parse_mode == 'HTML', f"Wrong parse_mode: {parse_mode}"
            
            self.passed_tests += 1
            print("   ✅ Access Control: Mobile-optimized with HTML")
            
        except Exception as e:
            print(f"   ❌ Access Control Error: {e}")
            
        self.total_tests += 1
        
    async def test_html_parse_mode(self):
        """Test HTML parse mode across all screens"""
        print("\n📱 Test 6: HTML Parse Mode Verification")
        
        screens_to_test = [
            ("Domain Management", self.bot.handle_domain_management, ["query", "example.com"]),
            ("Website Control", self.bot.handle_website_control, ["query", "example.com"]),
            ("Portfolio Stats", self.bot.handle_portfolio_stats, ["query"]),
            ("Mass DNS Update", self.bot.handle_mass_dns_update, ["query"]),
            ("Access Control", self.bot.handle_access_control, ["query", "example.com"]),
        ]
        
        html_count = 0
        
        for screen_name, handler, args in screens_to_test:
            try:
                query = self.create_mock_query()
                
                # Replace "query" with actual query object
                actual_args = []
                for arg in args:
                    if arg == "query":
                        actual_args.append(query)
                    else:
                        actual_args.append(arg)
                
                await handler(*actual_args)
                
                if query.edit_message_text.called:
                    call_args = query.edit_message_text.call_args
                    parse_mode = call_args[1].get('parse_mode', '')
                    
                    if parse_mode == 'HTML':
                        html_count += 1
                        print(f"   ✓ {screen_name}: HTML parse_mode")
                    else:
                        print(f"   ✗ {screen_name}: {parse_mode} parse_mode")
                        
            except Exception as e:
                print(f"   ✗ {screen_name}: Error - {e}")
        
        print(f"\n   HTML Parse Mode: {html_count}/{len(screens_to_test)} screens")
        
        if html_count == len(screens_to_test):
            self.passed_tests += 1
            print("   ✅ All screens use HTML parse_mode")
        else:
            print("   ❌ Some screens missing HTML parse_mode")
            
        self.total_tests += 1
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 MOBILE UI OPTIMIZATION TEST SUMMARY")
        print("="*60)
        
        print(f"\nTotal Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n✅ ALL MOBILE UI OPTIMIZATIONS COMPLETE WITH HTML FORMATTING!")
            print("🎯 Bot is fully optimized for mobile-first experience")
            print("📱 All screens display compactly with proper HTML formatting")
        else:
            print("\n⚠️ Some optimizations need attention")
            
async def main():
    """Run all mobile UI optimization tests"""
    tester = TestMobileUIHTMLComplete()
    
    try:
        await tester.test_optimized_screens()
    except Exception as e:
        print(f"\n❌ Test execution error: {e}")
        
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())