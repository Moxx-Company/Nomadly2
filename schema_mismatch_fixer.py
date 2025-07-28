#!/usr/bin/env python3
"""
Schema Mismatch Automatic Fixer
===============================

This script automatically fixes schema mismatches detected by the analyzer
by applying search and replace operations across all affected files.

Author: Nomadly2 Development Team
Date: July 22, 2025
"""

import os
import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class SchemaAutoFixer:
    """Automatically fix database schema mismatches in code"""
    
    # Define the fixes to apply
    FIXES = [
        {
            'description': 'Fix wallet_transactions.amount -> amount',
            'pattern': r'\bwallet_transactions\.amount\b',
            'replacement': 'wallet_transactions.amount',
            'files': ['*.py']
        },
        {
            'description': 'Fix registered_domains.expiry_date -> expiry_date', 
            'pattern': r'\bregistered_domains\.expiry_date\b',
            'replacement': 'registered_domains.expiry_date',
            'files': ['*.py']
        },
        {
            'description': 'Fix registered_domains.cloudflare_zone_id -> cloudflare_zone_id',
            'pattern': r'\bregistered_domains\.cloudflare_zone_id\b', 
            'replacement': 'registered_domains.cloudflare_zone_id',
            'files': ['*.py']
        },
        {
            'description': 'Fix orders.service_details -> service_details',
            'pattern': r'\borders\.metadata\b',
            'replacement': 'orders.service_details', 
            'files': ['*.py']
        },
        {
            'description': 'Fix bare amount references',
            'pattern': r'\bamount_usd\b(?![\'"])',
            'replacement': 'amount',
            'files': ['*.py']
        },
        {
            'description': 'Fix bare expiry_date references',
            'pattern': r'\bexpires_at\b(?![\'"])',
            'replacement': 'expiry_date',
            'files': ['*.py'] 
        },
        {
            'description': 'Fix bare cloudflare_zone_id references (context-aware)',
            'pattern': r'\bzone_id\b(?![\'"])',
            'replacement': 'cloudflare_zone_id',
            'files': ['*.py'],
            'context_required': ['registered_domains', 'cloudflare']
        }
    ]
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.fixes_applied = []
        self.files_modified = set()
        
    def find_python_files(self) -> List[str]:
        """Find all Python files in the project"""
        python_files = []
        
        for root, dirs, files in os.walk('.'):
            # Skip hidden directories and common non-code directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def should_apply_fix_to_file(self, fix: Dict, file_content: str) -> bool:
        """Determine if fix should be applied based on context"""
        if 'context_required' not in fix:
            return True
        
        # Check if any required context is present
        for context in fix['context_required']:
            if context.lower() in file_content.lower():
                return True
        
        return False
    
    def apply_fix_to_file(self, file_path: str, fix: Dict) -> Tuple[bool, int]:
        """Apply a single fix to a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Skip if fix shouldn't be applied
            if not self.should_apply_fix_to_file(fix, original_content):
                return False, 0
            
            # Apply the fix
            fixed_content, count = re.subn(
                fix['pattern'], 
                fix['replacement'], 
                original_content,
                flags=re.IGNORECASE | re.MULTILINE
            )
            
            if count > 0 and not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                self.files_modified.add(file_path)
                logger.info(f"✅ Applied fix to {file_path}: {count} replacements")
            
            return count > 0, count
            
        except Exception as e:
            logger.error(f"❌ Failed to fix {file_path}: {e}")
            return False, 0
    
    def run_all_fixes(self) -> Dict:
        """Run all schema fixes across all Python files"""
        try:
            logger.info("🔧 STARTING AUTOMATIC SCHEMA FIXES")
            logger.info("=" * 50)
            
            if self.dry_run:
                logger.info("🔍 DRY RUN MODE - No files will be modified")
            else:
                logger.info("✍️ LIVE MODE - Files will be modified")
            
            python_files = self.find_python_files()
            logger.info(f"📁 Found {len(python_files)} Python files to check")
            
            results = {
                'fixes_applied': [],
                'files_modified': [],
                'total_replacements': 0,
                'summary': {}
            }
            
            for fix in self.FIXES:
                logger.info(f"\n🔧 Applying fix: {fix['description']}")
                
                fix_results = {
                    'description': fix['description'],
                    'files_affected': [],
                    'total_replacements': 0
                }
                
                for file_path in python_files:
                    modified, count = self.apply_fix_to_file(file_path, fix)
                    
                    if modified:
                        fix_results['files_affected'].append({
                            'file': file_path,
                            'replacements': count
                        })
                        fix_results['total_replacements'] += count
                
                if fix_results['total_replacements'] > 0:
                    results['fixes_applied'].append(fix_results)
                    results['total_replacements'] += fix_results['total_replacements']
                    
                    logger.info(f"   ✅ {fix_results['total_replacements']} replacements in {len(fix_results['files_affected'])} files")
                else:
                    logger.info(f"   ℹ️ No matches found for this fix")
            
            results['files_modified'] = list(self.files_modified)
            results['summary'] = {
                'total_fixes': len(results['fixes_applied']),
                'total_files_modified': len(self.files_modified),
                'total_replacements': results['total_replacements']
            }
            
            logger.info("✅ ALL FIXES COMPLETED")
            return results
            
        except Exception as e:
            logger.error(f"❌ Fix process failed: {e}")
            return {}
    
    def generate_fix_report(self, results: Dict) -> str:
        """Generate a detailed report of fixes applied"""
        if not results:
            return "No fixes were applied."
        
        report = ["🔧 SCHEMA MISMATCH FIX REPORT", "=" * 40, ""]
        
        summary = results.get('summary', {})
        report.append(f"📊 SUMMARY:")
        report.append(f"   Total fixes applied: {summary.get('total_fixes', 0)}")
        report.append(f"   Files modified: {summary.get('total_files_modified', 0)}")
        report.append(f"   Total replacements: {summary.get('total_replacements', 0)}")
        report.append("")
        
        if results.get('fixes_applied'):
            report.append("🔍 DETAILED FIXES:")
            
            for fix in results['fixes_applied']:
                report.append(f"\n✅ {fix['description']}")
                report.append(f"   Replacements: {fix['total_replacements']}")
                
                for file_info in fix['files_affected'][:5]:  # Show first 5 files
                    report.append(f"   - {file_info['file']}: {file_info['replacements']} changes")
                
                if len(fix['files_affected']) > 5:
                    report.append(f"   ... and {len(fix['files_affected']) - 5} more files")
        
        return "\n".join(report)

def main():
    """Run the schema mismatch fixer"""
    print("🔧 AUTOMATIC SCHEMA MISMATCH FIXER")
    print("=" * 45)
    
    # Ask for confirmation unless in CI
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--apply':
        dry_run = False
        print("✍️ APPLYING FIXES TO FILES")
    else:
        dry_run = True
        print("🔍 DRY RUN MODE (use --apply to actually modify files)")
    
    try:
        fixer = SchemaAutoFixer(dry_run=dry_run)
        results = fixer.run_all_fixes()
        
        report = fixer.generate_fix_report(results)
        print(f"\n{report}")
        
        if dry_run and results.get('summary', {}).get('total_replacements', 0) > 0:
            print(f"\n💡 To apply these fixes, run:")
            print(f"   python schema_mismatch_fixer.py --apply")
        
        elif not dry_run and results:
            print(f"\n✅ ALL SCHEMA FIXES APPLIED SUCCESSFULLY")
            print(f"   Files modified: {len(results['files_modified'])}")
            print(f"   Total changes: {results['summary']['total_replacements']}")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()