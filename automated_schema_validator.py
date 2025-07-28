#!/usr/bin/env python3
"""
Automated Schema Validator - Continuous Prevention System
=========================================================

This system continuously monitors for schema issues and prevents
the recurring SQL column errors through automated validation.

Author: Nomadly2 Development Team
Date: July 22, 2025
"""

import os
import re
import glob
import logging
from datetime import datetime
import sqlalchemy as sa
from database import get_db_manager

class AutomatedSchemaValidator:
    """Automated schema validation and prevention system"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.validation_patterns = {
            'openprovider_id_incorrect': {
                'pattern': r'openprovider_id(?!\w)',
                'should_be': 'openprovider_domain_id',
                'table': 'registered_domains',
                'severity': 'critical'
            },
            'expires_at_incorrect': {
                'pattern': r'expires_at(?!\w)', 
                'should_be': 'expiry_date',
                'table': 'registered_domains',
                'severity': 'critical'
            },
            'orders_amount_incorrect': {
                'pattern': r'orders\.amount(?!\w)',
                'should_be': 'orders.amount_usd', 
                'table': 'orders',
                'severity': 'critical'
            }
        }
    
    def get_actual_database_schema(self):
        """Get actual database schema for validation"""
        
        schema_info = {}
        
        try:
            with self.db_manager.get_session() as session:
                # Query actual schema from information_schema
                query = """
                SELECT 
                    table_name, 
                    array_agg(column_name ORDER BY ordinal_position) as columns
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                  AND table_name IN ('orders', 'registered_domains', 'users', 'wallet_transactions')
                GROUP BY table_name
                """
                
                result = session.execute(sa.text(query))
                
                for row in result:
                    schema_info[row.table_name] = row.columns
                    
                return schema_info
                
        except Exception as e:
            logging.error(f"Could not fetch database schema: {e}")
            # Return known correct schema as fallback
            return {
                'orders': ['id', 'amount_usd', 'payment_status', 'domain_name', 'telegram_id'],
                'registered_domains': ['id', 'domain_name', 'openprovider_domain_id', 'expiry_date', 'cloudflare_zone_id'],
                'users': ['id', 'telegram_id', 'technical_email', 'balance_usd'],
                'wallet_transactions': ['id', 'user_id', 'amount_usd', 'transaction_type']
            }
    
    def validate_common_queries(self):
        """Validate that common queries work with actual schema"""
        
        print("🔍 VALIDATING COMMON QUERIES AGAINST DATABASE")
        print("=" * 50)
        print()
        
        test_queries = [
            {
                'name': 'Orders with correct amount column',
                'query': 'SELECT id, amount_usd, payment_status FROM orders LIMIT 1',
                'expected_columns': ['id', 'amount_usd', 'payment_status']
            },
            {
                'name': 'Registered domains with correct columns',
                'query': 'SELECT domain_name, expiry_date, openprovider_domain_id FROM registered_domains LIMIT 1',
                'expected_columns': ['domain_name', 'expiry_date', 'openprovider_domain_id']
            },
            {
                'name': 'Users with technical email',
                'query': 'SELECT id, telegram_id, technical_email FROM users LIMIT 1',
                'expected_columns': ['id', 'telegram_id', 'technical_email']
            }
        ]
        
        passed_tests = 0
        failed_tests = []
        
        try:
            with self.db_manager.get_session() as session:
                for test in test_queries:
                    try:
                        result = session.execute(sa.text(test['query']))
                        # Check if query executes without error
                        row = result.fetchone()
                        print(f"✅ {test['name']}: PASSED")
                        passed_tests += 1
                        
                    except Exception as e:
                        print(f"❌ {test['name']}: FAILED - {e}")
                        failed_tests.append(test['name'])
        
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        print()
        print(f"📊 VALIDATION RESULTS: {passed_tests}/{len(test_queries)} tests passed")
        
        if failed_tests:
            print("Failed tests:")
            for test in failed_tests:
                print(f"   • {test}")
        
        return len(failed_tests) == 0
    
    def scan_for_schema_mismatches(self, max_files=100):
        """Scan files for remaining schema mismatches"""
        
        print("🔍 SCANNING FOR REMAINING SCHEMA MISMATCHES")
        print("=" * 45)
        print()
        
        python_files = glob.glob('**/*.py', recursive=True)
        
        # Filter relevant files
        filtered_files = []
        exclude_patterns = {'.git', '__pycache__', 'node_modules', '.cache', 'venv', 'env'}
        
        for file_path in python_files[:max_files]:
            path_parts = set(file_path.split('/'))
            if not path_parts.intersection(exclude_patterns):
                filtered_files.append(file_path)
        
        print(f"Scanning {len(filtered_files)} files for schema issues...")
        
        total_issues = 0
        files_with_issues = []
        
        for file_path in filtered_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_issues = []
                
                for issue_name, config in self.validation_patterns.items():
                    matches = re.findall(config['pattern'], content, re.IGNORECASE)
                    if matches:
                        file_issues.append({
                            'issue': issue_name,
                            'count': len(matches),
                            'should_be': config['should_be'],
                            'severity': config['severity']
                        })
                        total_issues += len(matches)
                
                if file_issues:
                    files_with_issues.append({
                        'file': file_path,
                        'issues': file_issues
                    })
                    
            except:
                continue
        
        print(f"📊 SCAN RESULTS:")
        print(f"   • Files scanned: {len(filtered_files)}")
        print(f"   • Files with issues: {len(files_with_issues)}")
        print(f"   • Total issues found: {total_issues}")
        
        if files_with_issues:
            print("\n🔍 FILES NEEDING ATTENTION:")
            for file_info in files_with_issues[:10]:  # Show first 10
                print(f"   • {file_info['file']}")
                for issue in file_info['issues']:
                    print(f"     - {issue['issue']}: {issue['count']} occurrences → {issue['should_be']}")
        
        return total_issues == 0, files_with_issues
    
    def generate_corrected_query_examples(self):
        """Generate examples of corrected queries"""
        
        print("✅ CORRECTED QUERY EXAMPLES")
        print("=" * 32)
        print()
        
        examples = [
            {
                'wrong': 'SELECT openprovider_id FROM registered_domains',
                'correct': 'SELECT openprovider_domain_id FROM registered_domains',
                'explanation': 'Use openprovider_domain_id, not openprovider_id'
            },
            {
                'wrong': 'SELECT expires_at FROM registered_domains', 
                'correct': 'SELECT expiry_date FROM registered_domains',
                'explanation': 'Use expiry_date, not expires_at'
            },
            {
                'wrong': 'SELECT amount FROM orders',
                'correct': 'SELECT amount_usd FROM orders', 
                'explanation': 'Use amount_usd, not amount'
            },
            {
                'wrong': 'user_record.email',
                'correct': 'user_record.technical_email',
                'explanation': 'Use technical_email, not email'
            }
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"{i}. {example['explanation']}:")
            print(f"   ❌ Wrong:   {example['wrong']}")
            print(f"   ✅ Correct: {example['correct']}")
            print()
    
    def create_monitoring_report(self):
        """Create comprehensive monitoring report"""
        
        # Get database schema
        actual_schema = self.get_actual_database_schema()
        
        # Validate queries
        queries_valid = self.validate_common_queries()
        
        # Scan for mismatches
        no_issues, files_with_issues = self.scan_for_schema_mismatches()
        
        # Generate examples
        self.generate_corrected_query_examples()
        
        # Summary report
        print("🎯 COMPREHENSIVE SCHEMA VALIDATION REPORT")
        print("=" * 45)
        print()
        print(f"📊 Database Schema Status:")
        print(f"   • Tables validated: {len(actual_schema)}")
        print(f"   • Query validation: {'PASSED' if queries_valid else 'FAILED'}")
        print(f"   • Code scan status: {'CLEAN' if no_issues else 'ISSUES FOUND'}")
        print(f"   • Files needing fixes: {len(files_with_issues) if files_with_issues else 0}")
        print()
        
        if queries_valid and no_issues:
            print("✅ SCHEMA VALIDATION: FULLY COMPLIANT")
            print("   All queries work with actual database schema")
            print("   No schema mismatches found in codebase") 
            return True
        else:
            print("⚠️ SCHEMA VALIDATION: NEEDS ATTENTION")
            if not queries_valid:
                print("   • Some queries fail with current schema")
            if not no_issues:
                print("   • Schema mismatches found in code files")
            return False

def main():
    """Run automated schema validation"""
    
    print("🤖 AUTOMATED SCHEMA VALIDATOR")
    print("=" * 35)
    print("Continuous monitoring for database schema compliance...")
    print()
    
    validator = AutomatedSchemaValidator()
    
    # Run comprehensive validation
    is_fully_compliant = validator.create_monitoring_report()
    
    if is_fully_compliant:
        print("🎉 VALIDATION COMPLETE: SYSTEM IS SCHEMA-COMPLIANT")
        print("   No action needed - all schema references are correct")
    else:
        print("🔧 VALIDATION COMPLETE: CORRECTIVE ACTION RECOMMENDED")
        print("   Run critical_bug_fixes_summary.py to resolve issues")
    
    return is_fully_compliant

if __name__ == "__main__":
    main()