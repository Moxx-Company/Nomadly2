#!/usr/bin/env python3
"""
Production Deep Test - Comprehensive Bot Analysis
Identifies duplicate handlers, callbacks, bugs, and issues
"""

import re
import ast
from collections import defaultdict
from datetime import datetime

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

class ProductionDeepTest:
    def __init__(self):
        self.bot_file = "nomadly3_clean_bot.py"
        self.issues_found = []
        self.duplicate_methods = []
        self.missing_handlers = []
        self.duplicate_callbacks = []
        self.undefined_references = []
        self.security_issues = []
        
    def print_header(self, text):
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{text:^70}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
    def print_section(self, text):
        print(f"\n{CYAN}{'─'*50}{RESET}")
        print(f"{CYAN}{text}{RESET}")
        print(f"{CYAN}{'─'*50}{RESET}")
        
    def print_success(self, text):
        print(f"{GREEN}✅ {text}{RESET}")
        
    def print_error(self, text):
        print(f"{RED}❌ {text}{RESET}")
        self.issues_found.append(text)
        
    def print_warning(self, text):
        print(f"{YELLOW}⚠️  {text}{RESET}")
        
    def print_info(self, text):
        print(f"ℹ️  {text}")
        
    def test_duplicate_methods(self):
        """Find duplicate method definitions"""
        self.print_section("DUPLICATE METHOD ANALYSIS")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        # Find all method definitions
        method_pattern = r'^\s*(async\s+)?def\s+(\w+)\s*\('
        methods = defaultdict(list)
        
        for match in re.finditer(method_pattern, content, re.MULTILINE):
            method_name = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            methods[method_name].append(line_num)
            
        # Find duplicates
        duplicates_found = False
        for method_name, lines in methods.items():
            if len(lines) > 1:
                duplicates_found = True
                self.duplicate_methods.append(method_name)
                self.print_error(f"Duplicate method '{method_name}' at lines: {lines}")
                
        if not duplicates_found:
            self.print_success("No duplicate methods found")
            
    def test_callback_handlers(self):
        """Test callback handler coverage"""
        self.print_section("CALLBACK HANDLER ANALYSIS")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        # Extract all callback_data definitions
        callback_pattern = r'callback_data=["\']([^"\']+)["\']'
        callbacks_defined = set()
        
        for match in re.finditer(callback_pattern, content):
            callback = match.group(1)
            # Handle f-strings
            if '{' in callback:
                base = callback.split('{')[0]
                callbacks_defined.add(f"{base}*")
            else:
                callbacks_defined.add(callback)
                
        # Extract handled callbacks
        handler_patterns = [
            r'if\s+data\s*==\s*["\']([^"\']+)["\']',
            r'elif\s+data\s*==\s*["\']([^"\']+)["\']',
            r'if\s+data\.startswith\(["\']([^"\']+)["\']',
            r'elif\s+data\.startswith\(["\']([^"\']+)["\']',
        ]
        
        callbacks_handled = set()
        for pattern in handler_patterns:
            for match in re.finditer(pattern, content):
                callback = match.group(1)
                callbacks_handled.add(callback)
                # Add wildcard version for startswith
                if 'startswith' in pattern:
                    callbacks_handled.add(f"{callback}*")
                    
        # Find missing handlers
        missing = callbacks_defined - callbacks_handled
        
        # Filter out false positives
        filtered_missing = []
        for callback in missing:
            # Check if it's handled by a startswith pattern
            handled = False
            for handled_callback in callbacks_handled:
                if handled_callback.endswith('*'):
                    prefix = handled_callback[:-1]
                    if callback.startswith(prefix) or callback[:-1] == prefix:
                        handled = True
                        break
            if not handled:
                filtered_missing.append(callback)
                
        self.print_info(f"Total callbacks defined: {len(callbacks_defined)}")
        self.print_info(f"Total handlers found: {len(callbacks_handled)}")
        
        if filtered_missing:
            for callback in sorted(filtered_missing):
                self.print_error(f"Missing handler for callback: {callback}")
                self.missing_handlers.append(callback)
        else:
            self.print_success("All callbacks have handlers")
            
    def test_duplicate_callbacks(self):
        """Find duplicate callback_data values"""
        self.print_section("DUPLICATE CALLBACK ANALYSIS")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Track callback definitions with line numbers
        callback_locations = defaultdict(list)
        
        for i, line in enumerate(lines, 1):
            matches = re.findall(r'callback_data=["\']([^"\']+)["\']', line)
            for callback in matches:
                if '{' not in callback:  # Skip f-strings
                    callback_locations[callback].append(i)
                    
        # Find duplicates
        duplicates_found = False
        for callback, locations in callback_locations.items():
            if len(locations) > 1:
                duplicates_found = True
                self.duplicate_callbacks.append(callback)
                self.print_error(f"Duplicate callback '{callback}' at lines: {locations}")
                
        if not duplicates_found:
            self.print_success("No duplicate callback_data values found")
            
    def test_undefined_references(self):
        """Find undefined variable/method references"""
        self.print_section("UNDEFINED REFERENCE ANALYSIS")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        # Common undefined reference patterns
        undefined_patterns = [
            (r'self\.(\w+)\s*\(', "method calls"),
            (r'self\.(\w+)\s*=', "attribute assignments"),
            (r'await\s+self\.(\w+)\s*\(', "async method calls"),
        ]
        
        # Extract all defined methods
        defined_methods = set()
        for match in re.finditer(r'def\s+(\w+)\s*\(', content):
            defined_methods.add(match.group(1))
            
        # Extract all defined attributes
        defined_attrs = set(['user_sessions', 'registry_api', 'forex_api', 
                           'trustee_manager', 'payment_service', 'ui_cleanup'])
        
        # Check for undefined references
        undefined_found = False
        for pattern, desc in undefined_patterns:
            for match in re.finditer(pattern, content):
                ref = match.group(1)
                if ref not in defined_methods and ref not in defined_attrs:
                    # Skip known false positives
                    if ref not in ['get', 'startswith', 'endswith', 'replace', 
                                 'format', 'split', 'strip', 'lower', 'upper']:
                        line_num = content[:match.start()].count('\n') + 1
                        self.print_warning(f"Possible undefined {desc}: self.{ref} at line {line_num}")
                        undefined_found = True
                        
        if not undefined_found:
            self.print_success("No undefined references found")
            
    def test_security_issues(self):
        """Check for security issues"""
        self.print_section("SECURITY ANALYSIS")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        security_checks = [
            (r'8058274028:', "Hardcoded bot token"),
            (r'(password|secret|key)\s*=\s*["\'][^"\']+["\']', "Hardcoded secrets"),
            (r'eval\s*\(', "Unsafe eval usage"),
            (r'exec\s*\(', "Unsafe exec usage"),
            (r'pickle\.loads', "Unsafe pickle usage"),
        ]
        
        issues_found = False
        for pattern, issue in security_checks:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    if issue == "Hardcoded bot token":
                        # Check if it's in environment variable usage
                        line_start = content.rfind('\n', 0, match.start()) + 1
                        line_end = content.find('\n', match.end())
                        line_content = content[line_start:line_end]
                        if 'os.getenv' not in line_content and 'BOT_TOKEN' not in line_content:
                            self.print_error(f"{issue} at line {line_num}")
                            self.security_issues.append(issue)
                            issues_found = True
                    else:
                        self.print_warning(f"Potential {issue} at line {line_num}")
                        
        if not issues_found:
            self.print_success("No critical security issues found")
            
    def test_error_handling(self):
        """Check error handling coverage"""
        self.print_section("ERROR HANDLING ANALYSIS")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        # Find all async methods
        async_methods = []
        for match in re.finditer(r'async\s+def\s+(\w+)\s*\([^)]*\):', content):
            method_name = match.group(1)
            method_start = match.end()
            # Find method end
            next_method = re.search(r'\n\s*(?:async\s+)?def\s+\w+\s*\(', content[method_start:])
            if next_method:
                method_end = method_start + next_method.start()
            else:
                method_end = len(content)
            
            method_body = content[method_start:method_end]
            async_methods.append((method_name, method_body))
            
        # Check for try/except blocks
        methods_without_error_handling = []
        for method_name, method_body in async_methods:
            if 'try:' not in method_body and method_name not in ['__init__']:
                # Check if it's a critical method
                critical_keywords = ['handle', 'show', 'process', 'payment', 'domain']
                if any(keyword in method_name.lower() for keyword in critical_keywords):
                    methods_without_error_handling.append(method_name)
                    
        if methods_without_error_handling:
            self.print_warning(f"Methods without error handling: {len(methods_without_error_handling)}")
            for method in methods_without_error_handling[:5]:  # Show first 5
                self.print_info(f"  - {method}")
            if len(methods_without_error_handling) > 5:
                self.print_info(f"  ... and {len(methods_without_error_handling) - 5} more")
        else:
            self.print_success("All critical methods have error handling")
            
    def test_import_issues(self):
        """Check for import issues"""
        self.print_section("IMPORT ANALYSIS")
        
        with open(self.bot_file, 'r') as f:
            content = f.read()
            
        # Extract imports
        imports = []
        for line in content.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line.strip())
                
        # Check for missing common imports
        required_imports = [
            'logging',
            'asyncio',
            'telegram',
            'os',
            'json',
        ]
        
        missing_imports = []
        for req in required_imports:
            if not any(req in imp for imp in imports):
                missing_imports.append(req)
                
        if missing_imports:
            for imp in missing_imports:
                self.print_warning(f"Possibly missing import: {imp}")
        else:
            self.print_success("All common imports present")
            
        # Check for duplicate imports
        seen_imports = set()
        for imp in imports:
            if imp in seen_imports:
                self.print_error(f"Duplicate import: {imp}")
            seen_imports.add(imp)
            
    def generate_summary(self):
        """Generate test summary"""
        self.print_header("PRODUCTION TEST SUMMARY")
        
        total_issues = (len(self.duplicate_methods) + len(self.missing_handlers) + 
                       len(self.duplicate_callbacks) + len(self.security_issues))
        
        print(f"Total Critical Issues Found: {total_issues}")
        print(f"\nBreakdown:")
        print(f"  - Duplicate Methods: {len(self.duplicate_methods)}")
        print(f"  - Missing Handlers: {len(self.missing_handlers)}")
        print(f"  - Duplicate Callbacks: {len(self.duplicate_callbacks)}")
        print(f"  - Security Issues: {len(self.security_issues)}")
        
        if total_issues == 0:
            self.print_success("\n✅ BOT IS PRODUCTION READY!")
        else:
            self.print_error(f"\n❌ {total_issues} CRITICAL ISSUES NEED FIXING")
            
        return total_issues
        
    def run_all_tests(self):
        """Run all production tests"""
        print(f"{BLUE}NOMADLY3 PRODUCTION DEEP TEST{RESET}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Bot File: {self.bot_file}")
        
        # Run all tests
        self.test_duplicate_methods()
        self.test_callback_handlers()
        self.test_duplicate_callbacks()
        self.test_undefined_references()
        self.test_security_issues()
        self.test_error_handling()
        self.test_import_issues()
        
        # Generate summary
        return self.generate_summary()

if __name__ == "__main__":
    tester = ProductionDeepTest()
    issues = tester.run_all_tests()
    exit(0 if issues == 0 else 1)