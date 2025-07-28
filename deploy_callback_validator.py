#!/usr/bin/env python3
"""
Production Callback Validator - Deployment Ready Script
======================================================

This script validates the callback system for production deployment.
Specifically designed for ongoing maintenance and deployment validation.

Features:
- Real-time callback validation
- Production readiness assessment
- Automated deployment checks
- Performance analysis
- Error detection and reporting

Author: Nomadly2 Bot Development Team
Date: July 21, 2025
Version: 1.0 - Production Ready
"""

import re
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Set, Tuple
import logging

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('callback_validator.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class ProductionCallbackValidator:
    """Production-ready callback system validator"""
    
    def __init__(self, bot_file: str = "nomadly2_bot.py"):
        self.bot_file = bot_file
        self.validation_results = {}
        self.deployment_status = "UNKNOWN"
        self.critical_issues = []
        self.warnings = []
        
    def load_bot_content(self) -> str:
        """Load bot file content with error handling"""
        try:
            with open(self.bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Successfully loaded {self.bot_file} ({len(content)} characters)")
                return content
        except FileNotFoundError:
            error_msg = f"CRITICAL: Bot file {self.bot_file} not found"
            logger.error(error_msg)
            self.critical_issues.append(error_msg)
            return ""
        except Exception as e:
            error_msg = f"CRITICAL: Error reading {self.bot_file}: {e}"
            logger.error(error_msg)
            self.critical_issues.append(error_msg)
            return ""
    
    def extract_all_callbacks(self, content: str) -> Set[str]:
        """Extract all callback patterns from the code"""
        callback_patterns = [
            # Standard patterns
            r'callback_data=["\']([^"\']+)["\']',
            # F-string patterns  
            r'callback_data=f["\']([^"\']+)["\']',
            # Variable patterns
            r'callback_data=\s*([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        all_callbacks = set()
        
        for pattern in callback_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                # Clean up callback data
                if '{' in match:
                    # Convert f-string patterns to wildcards
                    cleaned = re.sub(r'\{[^}]+\}', '*', match)
                    all_callbacks.add(cleaned)
                else:
                    all_callbacks.add(match)
        
        logger.info(f"Found {len(all_callbacks)} callback patterns")
        return all_callbacks
    
    def extract_all_handlers(self, content: str) -> Set[str]:
        """Extract all callback handlers from handle_callback method"""
        handlers = set()
        
        # Find the handle_callback method
        handle_callback_pattern = r'async def handle_callback\(self, query.*?\):(.*?)(?=\n    async def|\n    def|\n\n|\Z)'
        handle_callback_match = re.search(handle_callback_pattern, content, re.DOTALL)
        
        if not handle_callback_match:
            error_msg = "CRITICAL: handle_callback method not found"
            logger.error(error_msg)
            self.critical_issues.append(error_msg)
            return handlers
        
        callback_content = handle_callback_match.group(1)
        
        # Extract handler patterns
        handler_patterns = [
            # Exact matches
            r'(?:elif|if)\s+data\s*==\s*["\']([^"\']+)["\']:',
            # Startswith patterns
            r'(?:elif|if)\s+data(?:\.strip\(\))?\s*\.startswith\(["\']([^"\']+)["\']',
            # In patterns
            r'(?:elif|if)\s+["\']([^"\']+)["\']\s+in\s+data:',
        ]
        
        for pattern in handler_patterns:
            matches = re.findall(pattern, callback_content, re.MULTILINE)
            for match in matches:
                handlers.add(match)
                # Also add wildcard version for startswith patterns
                if '_' in match:
                    handlers.add(f"{match}*")
        
        logger.info(f"Found {len(handlers)} callback handlers")
        return handlers
    
    def validate_coverage(self, callbacks: Set[str], handlers: Set[str]) -> Dict:
        """Validate callback coverage and return detailed results"""
        missing_handlers = []
        covered_callbacks = []
        
        for callback in callbacks:
            is_covered = False
            
            # Check exact match
            if callback in handlers:
                is_covered = True
                covered_callbacks.append(callback)
            else:
                # Check pattern matches
                for handler in handlers:
                    if '*' in handler:
                        pattern = handler.replace('*', '.*')
                        if re.match(f'^{pattern}$', callback):
                            is_covered = True
                            covered_callbacks.append(callback)
                            break
            
            if not is_covered:
                missing_handlers.append(callback)
        
        total_callbacks = len(callbacks)
        covered_count = len(covered_callbacks)
        coverage_percentage = (covered_count / total_callbacks * 100) if total_callbacks > 0 else 0
        
        return {
            'total_callbacks': total_callbacks,
            'covered_callbacks': covered_count,
            'missing_handlers': missing_handlers,
            'coverage_percentage': coverage_percentage,
            'is_complete': len(missing_handlers) == 0
        }
    
    def check_deployment_readiness(self, validation_results: Dict) -> str:
        """Determine deployment readiness based on validation results"""
        if self.critical_issues:
            return "FAILED"
        
        coverage = validation_results.get('coverage_percentage', 0)
        
        if coverage == 100.0:
            return "READY"
        elif coverage >= 95.0:
            return "NEARLY_READY"
        elif coverage >= 90.0:
            return "NEEDS_WORK"
        else:
            return "NOT_READY"
    
    def generate_deployment_report(self) -> Dict:
        """Generate comprehensive deployment report"""
        return {
            'validation_timestamp': datetime.now().isoformat(),
            'deployment_status': self.deployment_status,
            'validation_results': self.validation_results,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'bot_file': self.bot_file,
            'recommendation': self.get_deployment_recommendation()
        }
    
    def get_deployment_recommendation(self) -> str:
        """Get deployment recommendation based on current state"""
        if self.deployment_status == "READY":
            return "✅ DEPLOY: System is production ready with 100% callback coverage"
        elif self.deployment_status == "NEARLY_READY":
            return "⚠️ DEPLOY WITH CAUTION: Near-complete coverage, monitor for edge cases"
        elif self.deployment_status == "NEEDS_WORK":
            return "🔧 DO NOT DEPLOY: Significant callback gaps need addressing"
        elif self.deployment_status == "NOT_READY":
            return "❌ DO NOT DEPLOY: Major callback coverage issues"
        elif self.deployment_status == "FAILED":
            return "🚨 DEPLOYMENT BLOCKED: Critical issues must be resolved"
        else:
            return "❓ UNKNOWN STATUS: Unable to assess deployment readiness"
    
    def run_validation(self) -> Dict:
        """Run complete validation process"""
        logger.info("🚀 Starting production callback validation")
        
        # Load content
        content = self.load_bot_content()
        if not content:
            self.deployment_status = "FAILED"
            return self.generate_deployment_report()
        
        # Extract callbacks and handlers
        logger.info("📋 Extracting callbacks and handlers...")
        callbacks = self.extract_all_callbacks(content)
        handlers = self.extract_all_handlers(content)
        
        # Validate coverage
        logger.info("🔍 Validating callback coverage...")
        self.validation_results = self.validate_coverage(callbacks, handlers)
        
        # Determine deployment status
        self.deployment_status = self.check_deployment_readiness(self.validation_results)
        
        # Generate final report
        report = self.generate_deployment_report()
        
        logger.info(f"✅ Validation complete - Status: {self.deployment_status}")
        return report
    
    def print_validation_summary(self, report: Dict):
        """Print a concise validation summary"""
        print("\n" + "="*50)
        print("🚀 PRODUCTION CALLBACK VALIDATION REPORT")
        print("="*50)
        
        # Status
        status = report['deployment_status']
        status_icons = {
            'READY': '✅',
            'NEARLY_READY': '⚠️',
            'NEEDS_WORK': '🔧',
            'NOT_READY': '❌',
            'FAILED': '🚨'
        }
        
        print(f"\n📊 DEPLOYMENT STATUS: {status_icons.get(status, '❓')} {status}")
        
        # Coverage details
        if 'validation_results' in report:
            results = report['validation_results']
            print(f"\n📈 COVERAGE ANALYSIS:")
            print(f"   Total Callbacks: {results['total_callbacks']}")
            print(f"   Covered: {results['covered_callbacks']}")
            print(f"   Missing: {len(results.get('missing_handlers', []))}")
            print(f"   Coverage: {results['coverage_percentage']:.1f}%")
        
        # Missing handlers
        missing = report['validation_results'].get('missing_handlers', [])
        if missing:
            print(f"\n❌ MISSING HANDLERS ({len(missing)}):")
            for handler in sorted(missing)[:10]:  # Show first 10
                print(f"   • {handler}")
            if len(missing) > 10:
                print(f"   ... and {len(missing) - 10} more")
        
        # Critical issues
        if report['critical_issues']:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in report['critical_issues']:
                print(f"   • {issue}")
        
        # Recommendation
        print(f"\n🎯 RECOMMENDATION:")
        print(f"   {report['recommendation']}")
        
        print("\n" + "="*50)
    
    def save_report(self, report: Dict, filename: str = None):
        """Save validation report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"callback_validation_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, sort_keys=True)
            logger.info(f"📄 Validation report saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")

def main():
    """Main execution function"""
    print("🔍 NOMADLY2 PRODUCTION CALLBACK VALIDATOR")
    print("=" * 45)
    
    # Initialize validator
    validator = ProductionCallbackValidator()
    
    # Run validation
    report = validator.run_validation()
    
    # Print summary
    validator.print_validation_summary(report)
    
    # Save report
    validator.save_report(report)
    
    # Exit with appropriate code
    if report['deployment_status'] in ['READY', 'NEARLY_READY']:
        print("\n✅ Validation passed - Ready for deployment consideration")
        sys.exit(0)
    else:
        print("\n❌ Validation failed - Deployment not recommended")
        sys.exit(1)

if __name__ == "__main__":
    main()