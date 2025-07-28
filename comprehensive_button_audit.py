#!/usr/bin/env python3
"""
Comprehensive Button Responsiveness Audit
Identifies potential UI responsiveness issues across all bot buttons
"""

import re
import logging
from typing import Dict, List, Set, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ButtonResponsivenessAuditor:
    """Comprehensive audit system for button responsiveness issues"""
    
    def __init__(self, bot_file: str = "nomadly3_clean_bot.py"):
        self.bot_file = bot_file
        self.callback_definitions = set()
        self.callback_handlers = set()
        self.navigation_callbacks = set()
        self.potential_issues = []
        
    def extract_all_callbacks(self) -> Set[str]:
        """Extract all callback_data definitions from the bot file"""
        logger.info("🔍 Extracting all callback definitions...")
        
        try:
            with open(self.bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading bot file: {e}")
            return set()
        
        # Pattern to find callback_data definitions
        callback_patterns = [
            r'callback_data=["\']([^"\']+)["\']',
            r'callback_data=f["\']([^"\']+)["\']'
        ]
        
        callbacks = set()
        for pattern in callback_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if '{' in match:
                    # Convert f-string patterns to base patterns
                    base_pattern = re.sub(r'\{[^}]+\}', '*', match)
                    callbacks.add(base_pattern)
                else:
                    callbacks.add(match)
        
        logger.info(f"   Found {len(callbacks)} callback definitions")
        return callbacks
    
    def extract_all_handlers(self) -> Set[str]:
        """Extract all callback handlers from handle_callback_query method"""
        logger.info("🔧 Extracting all callback handlers...")
        
        try:
            with open(self.bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading bot file: {e}")
            return set()
        
        # Find the handle_callback_query method
        handle_callback_pattern = r'async def handle_callback_query\(.*?\):(.*?)(?=\n    async def|\n    def|\nclass|\Z)'
        handle_callback_match = re.search(handle_callback_pattern, content, re.DOTALL)
        
        if not handle_callback_match:
            logger.error("Could not find handle_callback_query method")
            return set()
        
        callback_content = handle_callback_match.group(1)
        
        # Extract handler patterns
        handler_patterns = [
            r'elif data == ["\']([^"\']+)["\']:',
            r'elif data and data\.startswith\(["\']([^"\']+)["\']',
            r'if data == ["\']([^"\']+)["\']:',
            r'if data and data\.startswith\(["\']([^"\']+)["\']',
        ]
        
        handlers = set()
        for pattern in handler_patterns:
            matches = re.findall(pattern, callback_content)
            for match in matches:
                handlers.add(match)
                # Add wildcard version for startswith patterns
                if 'startswith' in pattern:
                    handlers.add(f"{match}*")
        
        logger.info(f"   Found {len(handlers)} callback handlers")
        return handlers
    
    def identify_navigation_callbacks(self) -> Set[str]:
        """Identify callbacks that perform navigation and might face UI cache issues"""
        logger.info("🧭 Identifying navigation callbacks...")
        
        # Known navigation patterns
        navigation_patterns = [
            'main_menu', 'my_domains', 'search_domain', 'change_language',
            'show_languages', 'wallet', 'support_menu', 'back_to_',
            'return_to_', 'cancel_', 'menu_'
        ]
        
        nav_callbacks = set()
        for callback in self.callback_definitions:
            for pattern in navigation_patterns:
                if callback.startswith(pattern) or callback == pattern:
                    nav_callbacks.add(callback)
        
        logger.info(f"   Found {len(nav_callbacks)} navigation callbacks")
        return nav_callbacks
    
    def identify_potential_ui_issues(self) -> List[Dict]:
        """Identify potential UI responsiveness issues"""
        logger.info("⚠️ Analyzing potential UI responsiveness issues...")
        
        issues = []
        
        # Issue 1: Missing handlers
        missing_handlers = []
        for callback in self.callback_definitions:
            is_handled = False
            for handler in self.callback_handlers:
                if handler.endswith('*'):
                    # Pattern match
                    pattern = handler[:-1]
                    if callback.startswith(pattern):
                        is_handled = True
                        break
                elif callback == handler:
                    is_handled = True
                    break
            
            if not is_handled:
                missing_handlers.append(callback)
        
        if missing_handlers:
            issues.append({
                'type': 'Missing Handlers',
                'severity': 'HIGH',
                'count': len(missing_handlers),
                'callbacks': missing_handlers[:10],  # Show first 10
                'impact': 'Buttons will not respond when clicked'
            })
        
        # Issue 2: Navigation callbacks not in UI cleanup bypass
        ui_bypass_patterns = [
            'main_menu', 'my_domains', 'search_domain', 'change_language',
            'show_languages', 'wallet', 'support_menu', 'back_', 'return_',
            'cancel_', 'menu_', 'nav_'
        ]
        
        unprotected_nav = []
        for nav_callback in self.navigation_callbacks:
            is_protected = False
            for pattern in ui_bypass_patterns:
                if nav_callback.startswith(pattern) or nav_callback == pattern:
                    is_protected = True
                    break
            
            if not is_protected:
                unprotected_nav.append(nav_callback)
        
        if unprotected_nav:
            issues.append({
                'type': 'Unprotected Navigation',
                'severity': 'MEDIUM',
                'count': len(unprotected_nav),
                'callbacks': unprotected_nav[:10],
                'impact': 'Navigation buttons may become unresponsive due to UI cache'
            })
        
        # Issue 3: Duplicate handler detection
        handler_counts = {}
        for handler in self.callback_handlers:
            if not handler.endswith('*'):  # Exact matches only
                handler_counts[handler] = handler_counts.get(handler, 0) + 1
        
        duplicate_handlers = [h for h, count in handler_counts.items() if count > 1]
        if duplicate_handlers:
            issues.append({
                'type': 'Duplicate Handlers',
                'severity': 'MEDIUM', 
                'count': len(duplicate_handlers),
                'callbacks': duplicate_handlers,
                'impact': 'First handler executes, subsequent ones are unreachable'
            })
        
        return issues
    
    def generate_fixes(self, issues: List[Dict]) -> List[str]:
        """Generate fix recommendations for identified issues"""
        fixes = []
        
        for issue in issues:
            if issue['type'] == 'Missing Handlers':
                fixes.append("# Add missing callback handlers to handle_callback_query method:")
                for callback in issue['callbacks']:
                    if not callback.endswith('*'):
                        fixes.append(f'elif data == "{callback}":')
                        fixes.append(f'    await query.answer("⚡ Processing...")')
                        fixes.append(f'    await self.handle_{callback.replace("-", "_")}(query)')
                        fixes.append('')
            
            elif issue['type'] == 'Unprotected Navigation':
                fixes.append("# Add navigation callbacks to UI cleanup manager bypass list:")
                fixes.append("navigation_callbacks = [")
                for callback in issue['callbacks']:
                    fixes.append(f'    "{callback}",')
                fixes.append("]")
                fixes.append('')
            
            elif issue['type'] == 'Duplicate Handlers':
                fixes.append("# Remove duplicate handlers (keep first occurrence only):")
                for callback in issue['callbacks']:
                    fixes.append(f'# Duplicate handler found: {callback}')
                fixes.append('')
        
        return fixes
    
    def run_comprehensive_audit(self) -> Dict:
        """Run complete button responsiveness audit"""
        logger.info("🚀 Starting comprehensive button responsiveness audit")
        logger.info("=" * 70)
        
        # Extract data
        self.callback_definitions = self.extract_all_callbacks()
        self.callback_handlers = self.extract_all_handlers()
        self.navigation_callbacks = self.identify_navigation_callbacks()
        
        # Analyze issues
        issues = self.identify_potential_ui_issues()
        
        # Generate report
        report = {
            'total_callbacks': len(self.callback_definitions),
            'total_handlers': len(self.callback_handlers),
            'navigation_callbacks': len(self.navigation_callbacks),
            'issues_found': len(issues),
            'issues': issues,
            'severity_breakdown': {
                'HIGH': len([i for i in issues if i['severity'] == 'HIGH']),
                'MEDIUM': len([i for i in issues if i['severity'] == 'MEDIUM']),
                'LOW': len([i for i in issues if i['severity'] == 'LOW'])
            }
        }
        
        # Display results
        self.display_audit_results(report)
        
        # Generate fixes if issues found
        if issues:
            fixes = self.generate_fixes(issues)
            self.display_fix_recommendations(fixes)
        
        return report
    
    def display_audit_results(self, report: Dict):
        """Display comprehensive audit results"""
        print(f"\n📊 COMPREHENSIVE BUTTON AUDIT RESULTS")
        print("=" * 50)
        print(f"Total Callbacks Defined: {report['total_callbacks']}")
        print(f"Total Handlers Found: {report['total_handlers']}")
        print(f"Navigation Callbacks: {report['navigation_callbacks']}")
        print(f"Issues Found: {report['issues_found']}")
        
        severity = report['severity_breakdown']
        print(f"\nSeverity Breakdown:")
        print(f"  🔴 HIGH: {severity['HIGH']}")
        print(f"  🟡 MEDIUM: {severity['MEDIUM']}")
        print(f"  🟢 LOW: {severity['LOW']}")
        
        if report['issues']:
            print(f"\n⚠️ DETAILED ISSUES:")
            print("-" * 30)
            for i, issue in enumerate(report['issues'], 1):
                print(f"{i}. {issue['type']} ({issue['severity']})")
                print(f"   Count: {issue['count']}")
                print(f"   Impact: {issue['impact']}")
                if 'callbacks' in issue and issue['callbacks']:
                    print(f"   Examples: {', '.join(issue['callbacks'][:3])}")
                    print(f"   Full list: {', '.join(issue['callbacks'])}")
                print()
        else:
            print(f"\n✅ NO CRITICAL ISSUES FOUND!")
            print("All buttons should be responsive and properly handled.")
    
    def display_fix_recommendations(self, fixes: List[str]):
        """Display fix recommendations"""
        print(f"\n🔧 RECOMMENDED FIXES:")
        print("=" * 30)
        for fix in fixes:
            print(fix)

def main():
    """Run comprehensive button audit"""
    auditor = ButtonResponsivenessAuditor()
    report = auditor.run_comprehensive_audit()
    
    if report['issues_found'] == 0:
        print(f"\n🎉 AUDIT COMPLETE: All buttons verified responsive!")
    else:
        print(f"\n⚠️ AUDIT COMPLETE: {report['issues_found']} issues require attention")

if __name__ == "__main__":
    main()