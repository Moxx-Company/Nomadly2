#!/usr/bin/env python3
"""
Comprehensive Bug Scanner
=========================

This script scans the entire codebase for various types of bugs:
- Syntax errors
- Import issues
- Missing method calls
- Database query problems
- API integration issues
- Logic errors

Author: Nomadly2 Development Team
Date: July 22, 2025
"""

import os
import re
import ast
import logging
from typing import List, Dict, Set
from database import get_db_manager

logger = logging.getLogger(__name__)

class ComprehensiveBugScanner:
    """Scan for various types of bugs in the codebase"""
    
    def __init__(self):
        self.bugs_found = []
        self.files_scanned = 0
        self.bug_categories = {
            'syntax_errors': [],
            'import_errors': [],
            'missing_methods': [],
            'sql_issues': [], 
            'api_issues': [],
            'logic_errors': [],
            'runtime_risks': []
        }
    
    def scan_file_for_bugs(self, file_path: str) -> Dict[str, List]:
        """Scan a single file for various bug types"""
        file_bugs = {category: [] for category in self.bug_categories.keys()}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check syntax errors
            try:
                ast.parse(content)
            except SyntaxError as e:
                file_bugs['syntax_errors'].append(f"Line {e.lineno}: {e.msg}")
            
            # Check for common problematic patterns
            self.check_import_issues(content, file_bugs, file_path)
            self.check_missing_methods(content, file_bugs, file_path)
            self.check_sql_issues(content, file_bugs, file_path)
            self.check_api_issues(content, file_bugs, file_path)
            self.check_logic_errors(content, file_bugs, file_path)
            self.check_runtime_risks(content, file_bugs, file_path)
            
            return file_bugs
            
        except Exception as e:
            file_bugs['runtime_risks'].append(f"File read error: {e}")
            return file_bugs
    
    def check_import_issues(self, content: str, file_bugs: Dict, file_path: str):
        """Check for import-related issues"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for circular imports
            if 'from . import' in line and file_path in line:
                file_bugs['import_errors'].append(f"Line {i}: Potential circular import")
            
            # Check for undefined imports
            if re.search(r'from\s+(\w+)\s+import\s+(\w+)', line):
                match = re.search(r'from\s+(\w+)\s+import\s+(\w+)', line)
                if match and match.group(1) not in ['os', 'sys', 're', 'json', 'logging']:
                    # This would need more sophisticated checking
                    pass
    
    def check_missing_methods(self, content: str, file_bugs: Dict, file_path: str):
        """Check for calls to undefined methods"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for self.method calls where method might not exist
            if 'self.get_db_manager()' in line:
                file_bugs['missing_methods'].append(f"Line {i}: self.get_db_manager() should be get_db_manager()")
            
            # Check for await outside async functions
            if re.search(r'^\s*await\s+', line) and 'async def' not in content[:content.find(line)]:
                file_bugs['missing_methods'].append(f"Line {i}: await used outside async function")
            
            # Check for undefined API_TIMEOUT
            if 'API_TIMEOUT' in line and 'API_TIMEOUT =' not in content:
                file_bugs['missing_methods'].append(f"Line {i}: API_TIMEOUT not defined")
    
    def check_sql_issues(self, content: str, file_bugs: Dict, file_path: str):
        """Check for SQL-related issues"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for old column names that were fixed
            if 'amount_usd' in line and 'wallet_transactions' in content:
                file_bugs['sql_issues'].append(f"Line {i}: Should use 'amount' not 'amount_usd'")
            
            if 'expires_at' in line and 'registered_domains' in content:
                file_bugs['sql_issues'].append(f"Line {i}: Should use 'expiry_date' not 'expires_at'")
            
            # Check for JSONB without casting
            if re.search(r'service_details\s+LIKE', line, re.IGNORECASE):
                file_bugs['sql_issues'].append(f"Line {i}: JSONB LIKE needs ::text casting")
            
            # Check for SQL injection risks
            if re.search(r'["\'].*%s.*["\'].*%.*\(', line):
                file_bugs['sql_issues'].append(f"Line {i}: Potential SQL injection risk")
    
    def check_api_issues(self, content: str, file_bugs: Dict, file_path: str):
        """Check for API integration issues"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for hardcoded API endpoints
            if 'https://' in line and 'api.' in line:
                file_bugs['api_issues'].append(f"Line {i}: Hardcoded API endpoint")
            
            # Check for missing error handling
            if 'requests.get' in line or 'requests.post' in line:
                # Look for try/except nearby
                context = '\n'.join(lines[max(0, i-5):i+5])
                if 'try:' not in context and 'except' not in context:
                    file_bugs['api_issues'].append(f"Line {i}: API call without error handling")
            
            # Check for missing timeouts
            if 'requests.' in line and 'timeout=' not in line:
                file_bugs['api_issues'].append(f"Line {i}: API call without timeout")
    
    def check_logic_errors(self, content: str, file_bugs: Dict, file_path: str):
        """Check for logical errors"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for assignment in conditionals
            if re.search(r'if.*=(?!=)', line):
                file_bugs['logic_errors'].append(f"Line {i}: Assignment in conditional (use ==)")
            
            # Check for empty exception handlers
            if 'except:' in line:
                next_lines = lines[i:i+3] if i < len(lines) else []
                if all('pass' in nl or nl.strip() == '' for nl in next_lines):
                    file_bugs['logic_errors'].append(f"Line {i}: Empty exception handler")
            
            # Check for infinite loops
            if 'while True:' in line:
                context = '\n'.join(lines[i:i+10])
                if 'break' not in context and 'return' not in context:
                    file_bugs['logic_errors'].append(f"Line {i}: Potential infinite loop")
    
    def check_runtime_risks(self, content: str, file_bugs: Dict, file_path: str):
        """Check for runtime risks"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for dictionary key access without checks
            if re.search(r'\w+\[[\'"]\w+[\'\"]\]', line) and 'get(' not in line:
                file_bugs['runtime_risks'].append(f"Line {i}: Dictionary access without key check")
            
            # Check for division without zero check
            if '/' in line and 'if' not in line and '//' not in line:
                file_bugs['runtime_risks'].append(f"Line {i}: Division without zero check")
            
            # Check for file operations without context managers
            if 'open(' in line and 'with' not in line:
                file_bugs['runtime_risks'].append(f"Line {i}: File open without context manager")
    
    def scan_all_files(self) -> Dict:
        """Scan all Python files in the project"""
        try:
            logger.info("🔍 STARTING COMPREHENSIVE BUG SCAN")
            logger.info("=" * 50)
            
            python_files = []
            for root, dirs, files in os.walk('.'):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__']]
                
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            logger.info(f"📁 Scanning {len(python_files)} Python files...")
            
            total_bugs = {category: [] for category in self.bug_categories.keys()}
            files_with_bugs = 0
            
            for file_path in python_files:
                self.files_scanned += 1
                file_bugs = self.scan_file_for_bugs(file_path)
                
                has_bugs = False
                for category, bugs in file_bugs.items():
                    if bugs:
                        has_bugs = True
                        for bug in bugs:
                            total_bugs[category].append(f"{file_path}: {bug}")
                
                if has_bugs:
                    files_with_bugs += 1
            
            # Generate summary
            summary = {
                'files_scanned': self.files_scanned,
                'files_with_bugs': files_with_bugs,
                'total_bugs': sum(len(bugs) for bugs in total_bugs.values()),
                'bug_breakdown': {cat: len(bugs) for cat, bugs in total_bugs.items()},
                'detailed_bugs': total_bugs
            }
            
            logger.info("✅ BUG SCAN COMPLETE")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Bug scan failed: {e}")
            return {}

def main():
    """Run comprehensive bug scan"""
    print("🔍 COMPREHENSIVE BUG SCANNER")
    print("=" * 35)
    
    try:
        scanner = ComprehensiveBugScanner()
        results = scanner.scan_all_files()
        
        if results:
            print(f"\n📊 SCAN RESULTS:")
            print(f"   Files scanned: {results['files_scanned']}")
            print(f"   Files with bugs: {results['files_with_bugs']}")
            print(f"   Total bugs found: {results['total_bugs']}")
            
            print(f"\n🔍 BUG BREAKDOWN:")
            for category, count in results['bug_breakdown'].items():
                if count > 0:
                    emoji = "🔥" if count > 10 else "⚠️" if count > 5 else "ℹ️"
                    print(f"   {emoji} {category.replace('_', ' ').title()}: {count}")
            
            # Show top issues
            print(f"\n🔍 TOP ISSUES FOUND:")
            for category, bugs in results['detailed_bugs'].items():
                if bugs:
                    print(f"\n📋 {category.replace('_', ' ').title()}:")
                    for bug in bugs[:3]:  # Show first 3 of each type
                        print(f"   - {bug}")
                    if len(bugs) > 3:
                        print(f"   ... and {len(bugs) - 3} more")
            
            if results['total_bugs'] == 0:
                print(f"\n✅ NO SIGNIFICANT BUGS FOUND")
                print(f"   Codebase appears to be in good condition")
            else:
                print(f"\n💡 RECOMMENDATIONS:")
                if results['bug_breakdown']['syntax_errors'] > 0:
                    print(f"   🔥 Fix syntax errors immediately")
                if results['bug_breakdown']['sql_issues'] > 0:
                    print(f"   💾 Review database queries")
                if results['bug_breakdown']['api_issues'] > 0:
                    print(f"   🌐 Add error handling to API calls")
        
        else:
            print("\n❌ BUG SCAN FAILED - Check logs for details")
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()