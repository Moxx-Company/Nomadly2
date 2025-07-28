#!/usr/bin/env python3
"""
Comprehensive Callback Handler Analyzer for Nomadly2 Bot
=========================================================

This script performs deep analysis of the bot's callback system to:
1. Find all callback patterns and handlers
2. Identify missing handlers
3. Analyze handler complexity and patterns
4. Generate deployment reports
5. Validate callback routing logic
6. Find unused or orphaned handlers

Author: Nomadly2 Bot Development Team
Date: July 21, 2025
Version: 2.0
"""

import re
import ast
import os
import json
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CallbackAnalyzer:
    """Advanced callback system analyzer"""
    
    def __init__(self, bot_file: str = "nomadly2_bot.py"):
        self.bot_file = bot_file
        self.callbacks_defined = set()
        self.callbacks_handled = set()
        self.handler_methods = {}
        self.callback_patterns = {}
        self.handler_complexity = {}
        self.unused_handlers = set()
        
    def analyze_file_content(self) -> str:
        """Read and return the bot file content"""
        try:
            with open(self.bot_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Bot file {self.bot_file} not found")
            return ""
        except Exception as e:
            logger.error(f"Error reading {self.bot_file}: {e}")
            return ""
    
    def extract_callback_definitions(self, content: str) -> Set[str]:
        """Extract all callback_data definitions from the code"""
        callback_patterns = [
            # Standard callback patterns
            r'callback_data=["\']([^"\']+)["\']',
            # F-string patterns
            r'callback_data=f["\']([^"\']+)["\']',
            # Variable patterns
            r'callback_data=([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        callbacks = set()
        
        for pattern in callback_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Handle f-string placeholders
                if '{' in match:
                    # Extract the base pattern
                    base_pattern = re.sub(r'\{[^}]+\}', '*', match)
                    callbacks.add(base_pattern)
                else:
                    callbacks.add(match)
        
        return callbacks
    
    def extract_handler_methods(self, content: str) -> Dict[str, Dict]:
        """Extract all handler methods and their information"""
        handlers = {}
        
        # Find all methods in handle_callback
        handle_callback_pattern = r'async def handle_callback\(self, query.*?\n(.*?)(?=\n    async def|\n    def|\nclass|\Z)'
        handle_callback_match = re.search(handle_callback_pattern, content, re.DOTALL)
        
        if not handle_callback_match:
            logger.warning("Could not find handle_callback method")
            return handlers
        
        handle_callback_content = handle_callback_match.group(1)
        
        # Extract elif/if conditions for callbacks
        condition_patterns = [
            r'elif data == ["\']([^"\']+)["\']:',
            r'elif data and data\.startswith\(["\']([^"\']+)["\']',
            r'if data == ["\']([^"\']+)["\']:',
            r'if data and data\.startswith\(["\']([^"\']+)["\']',
        ]
        
        for pattern in condition_patterns:
            matches = re.findall(pattern, handle_callback_content)
            for match in matches:
                handlers[match] = {
                    'type': 'inline',
                    'pattern': pattern,
                    'complexity': 'simple'
                }
        
        # Find separate handler methods
        method_pattern = r'async def (handle_[a-zA-Z_]+)\(self[^)]*\):'
        method_matches = re.findall(method_pattern, content)
        
        for method_name in method_matches:
            handlers[method_name] = {
                'type': 'method',
                'pattern': f'async def {method_name}',
                'complexity': 'complex'
            }
        
        return handlers
    
    def analyze_handler_complexity(self, content: str) -> Dict[str, int]:
        """Analyze the complexity of each handler method"""
        complexity = {}
        
        # Find all handler methods
        handler_pattern = r'async def (handle_[a-zA-Z_]+)\(.*?\):(.*?)(?=\n    async def|\n    def|\nclass|\Z)'
        handlers = re.findall(handler_pattern, content, re.DOTALL)
        
        for handler_name, handler_body in handlers:
            # Count lines of code (excluding comments and empty lines)
            lines = [line.strip() for line in handler_body.split('\n') 
                    if line.strip() and not line.strip().startswith('#')]
            
            # Count complexity indicators
            complexity_score = len(lines)
            complexity_score += handler_body.count('if ')
            complexity_score += handler_body.count('elif ')
            complexity_score += handler_body.count('for ')
            complexity_score += handler_body.count('while ')
            complexity_score += handler_body.count('try:')
            complexity_score += handler_body.count('await ')
            
            complexity[handler_name] = complexity_score
        
        return complexity
    
    def find_missing_handlers(self) -> List[str]:
        """Find callbacks that don't have corresponding handlers"""
        missing = []
        
        for callback in self.callbacks_defined:
            # Skip variable callbacks and complex patterns
            if callback.startswith('f"') or '{' in callback:
                continue
                
            # Check for exact match
            if callback not in self.callbacks_handled:
                # Check for pattern match
                pattern_matched = False
                for handled_pattern in self.callbacks_handled:
                    if '*' in handled_pattern:
                        # Convert pattern to regex
                        regex_pattern = handled_pattern.replace('*', '.*')
                        if re.match(f'^{regex_pattern}$', callback):
                            pattern_matched = True
                            break
                
                if not pattern_matched:
                    missing.append(callback)
        
        return missing
    
    def find_unused_handlers(self) -> List[str]:
        """Find handlers that don't match any defined callbacks"""
        unused = []
        
        for handler in self.callbacks_handled:
            if '*' not in handler:  # Skip pattern handlers
                if handler not in self.callbacks_defined:
                    unused.append(handler)
        
        return unused
    
    def generate_coverage_report(self) -> Dict:
        """Generate comprehensive coverage report"""
        missing_handlers = self.find_missing_handlers()
        unused_handlers = self.find_unused_handlers()
        
        total_callbacks = len(self.callbacks_defined)
        handled_callbacks = total_callbacks - len(missing_handlers)
        coverage_rate = (handled_callbacks / total_callbacks * 100) if total_callbacks > 0 else 0
        
        return {
            'total_callbacks': total_callbacks,
            'handled_callbacks': handled_callbacks,
            'missing_callbacks': len(missing_handlers),
            'unused_handlers': len(unused_handlers),
            'coverage_rate': coverage_rate,
            'missing_handlers': missing_handlers,
            'unused_handlers': unused_handlers,
            'handler_complexity': self.handler_complexity,
            'callbacks_defined': sorted(list(self.callbacks_defined)),
            'callbacks_handled': sorted(list(self.callbacks_handled))
        }
    
    def analyze_callback_patterns(self) -> Dict[str, List[str]]:
        """Analyze callback patterns and group similar ones"""
        patterns = defaultdict(list)
        
        for callback in self.callbacks_defined:
            if '_' in callback:
                prefix = callback.split('_')[0]
                patterns[prefix].append(callback)
            else:
                patterns['simple'].append(callback)
        
        return dict(patterns)
    
    def validate_routing_logic(self, content: str) -> List[str]:
        """Validate callback routing logic for potential issues"""
        issues = []
        
        # Check for duplicate handlers
        handler_patterns = re.findall(r'elif data == ["\']([^"\']+)["\']:', content)
        seen_handlers = set()
        for handler in handler_patterns:
            if handler in seen_handlers:
                issues.append(f"Duplicate handler found: {handler}")
            seen_handlers.add(handler)
        
        # Check for unreachable code (handlers after catch-all patterns)
        lines = content.split('\n')
        found_catchall = False
        for i, line in enumerate(lines):
            if 'data.startswith(' in line and found_catchall:
                issues.append(f"Potential unreachable handler at line {i+1}: {line.strip()}")
            if 'else:' in line and 'handle_callback' in content[max(0, content.find(line) - 1000):content.find(line)]:
                found_catchall = True
        
        return issues
    
    def run_comprehensive_analysis(self) -> Dict:
        """Run complete analysis and return results"""
        logger.info(f"🔍 Starting comprehensive analysis of {self.bot_file}")
        
        content = self.analyze_file_content()
        if not content:
            return {"error": "Could not read bot file"}
        
        # Extract data
        logger.info("📋 Extracting callback definitions...")
        self.callbacks_defined = self.extract_callback_definitions(content)
        
        logger.info("🔧 Extracting handler methods...")
        self.handler_methods = self.extract_handler_methods(content)
        self.callbacks_handled = set(self.handler_methods.keys())
        
        logger.info("📊 Analyzing handler complexity...")
        self.handler_complexity = self.analyze_handler_complexity(content)
        
        logger.info("🔍 Analyzing callback patterns...")
        callback_patterns = self.analyze_callback_patterns()
        
        logger.info("✅ Validating routing logic...")
        routing_issues = self.validate_routing_logic(content)
        
        logger.info("📈 Generating coverage report...")
        coverage_report = self.generate_coverage_report()
        
        # Compile comprehensive report
        comprehensive_report = {
            **coverage_report,
            'callback_patterns': callback_patterns,
            'routing_issues': routing_issues,
            'analysis_metadata': {
                'file_analyzed': self.bot_file,
                'total_lines': len(content.split('\n')),
                'total_methods': len(re.findall(r'async def \w+', content)),
                'analysis_timestamp': __import__('datetime').datetime.now().isoformat()
            }
        }
        
        return comprehensive_report
    
    def print_detailed_report(self, report: Dict):
        """Print a detailed formatted report"""
        print("\n" + "="*60)
        print("🚀 COMPREHENSIVE CALLBACK ANALYSIS REPORT")
        print("="*60)
        
        # Coverage Summary
        print(f"\n📊 COVERAGE SUMMARY")
        print("-" * 30)
        print(f"Total callbacks defined: {report['total_callbacks']}")
        print(f"Callbacks handled: {report['handled_callbacks']}")
        print(f"Missing handlers: {report['missing_callbacks']}")
        print(f"Unused handlers: {report['unused_handlers']}")
        print(f"Coverage rate: {report['coverage_rate']:.1f}%")
        
        # Missing Handlers
        if report['missing_handlers']:
            print(f"\n❌ MISSING HANDLERS ({len(report['missing_handlers'])})")
            print("-" * 30)
            for handler in sorted(report['missing_handlers']):
                print(f"   • {handler}")
        else:
            print(f"\n✅ NO MISSING HANDLERS FOUND!")
        
        # Unused Handlers
        if report['unused_handlers']:
            print(f"\n⚠️  UNUSED HANDLERS ({len(report['unused_handlers'])})")
            print("-" * 30)
            for handler in sorted(report['unused_handlers']):
                print(f"   • {handler}")
        
        # Handler Complexity
        if report['handler_complexity']:
            print(f"\n🔧 HANDLER COMPLEXITY ANALYSIS")
            print("-" * 30)
            sorted_complexity = sorted(report['handler_complexity'].items(), 
                                     key=lambda x: x[1], reverse=True)
            for handler, complexity in sorted_complexity[:10]:  # Top 10 most complex
                print(f"   • {handler}: {complexity} points")
        
        # Callback Patterns
        print(f"\n📋 CALLBACK PATTERNS")
        print("-" * 30)
        for pattern, callbacks in report['callback_patterns'].items():
            print(f"   • {pattern}: {len(callbacks)} callbacks")
        
        # Routing Issues
        if report['routing_issues']:
            print(f"\n⚠️  ROUTING ISSUES ({len(report['routing_issues'])})")
            print("-" * 30)
            for issue in report['routing_issues']:
                print(f"   • {issue}")
        else:
            print(f"\n✅ NO ROUTING ISSUES FOUND!")
        
        # Analysis Metadata
        metadata = report['analysis_metadata']
        print(f"\n📈 ANALYSIS METADATA")
        print("-" * 30)
        print(f"File analyzed: {metadata['file_analyzed']}")
        print(f"Total lines: {metadata['total_lines']}")
        print(f"Total methods: {metadata['total_methods']}")
        print(f"Analysis time: {metadata['analysis_timestamp']}")
        
        print("\n" + "="*60)
    
    def save_report(self, report: Dict, filename: str = "callback_analysis_report.json"):
        """Save the analysis report to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, sort_keys=True)
            logger.info(f"📄 Report saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")

def main():
    """Main execution function"""
    print("🚀 NOMADLY2 COMPREHENSIVE CALLBACK ANALYZER")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = CallbackAnalyzer()
    
    # Run analysis
    report = analyzer.run_comprehensive_analysis()
    
    if "error" in report:
        print(f"❌ Analysis failed: {report['error']}")
        return
    
    # Print detailed report
    analyzer.print_detailed_report(report)
    
    # Save report
    analyzer.save_report(report)
    
    # Generate deployment recommendations
    print("\n🎯 DEPLOYMENT RECOMMENDATIONS")
    print("-" * 30)
    
    if report['missing_callbacks'] == 0:
        print("✅ System ready for deployment - 100% callback coverage achieved!")
    else:
        print(f"⚠️  {report['missing_callbacks']} missing handlers need implementation before deployment")
    
    if report['routing_issues']:
        print(f"⚠️  {len(report['routing_issues'])} routing issues need resolution")
    else:
        print("✅ No routing issues detected")
    
    if report['coverage_rate'] >= 95:
        print("✅ Excellent callback coverage - system is production ready")
    elif report['coverage_rate'] >= 90:
        print("⚠️  Good callback coverage - minor improvements recommended")
    else:
        print("❌ Poor callback coverage - significant work needed before deployment")

if __name__ == "__main__":
    main()