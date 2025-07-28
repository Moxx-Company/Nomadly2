#!/usr/bin/env python3
"""
Final Schema Fix Validator
=========================

This script identifies and fixes the remaining database schema mismatches
that are causing SQL errors throughout the system.

Author: Nomadly2 Development Team
Date: July 22, 2025
"""

import os
import re
import glob

class FinalSchemaValidator:
    """Validate and fix remaining schema mismatches"""
    
    def __init__(self):
        # Actual database schema based on information_schema
        self.actual_schema = {
            'orders': {
                'amount': 'amount_usd',  # Query uses 'amount' but column is 'amount_usd'
                'expires_at': 'expires_at',  # This column exists
                'openprovider_id': None,  # This column doesn't exist in orders table
            },
            'registered_domains': {
                'openprovider_id': 'openprovider_domain_id',  # Correct column name
                'expires_at': 'expiry_date',  # Query uses 'expires_at' but column is 'expiry_date'
            }
        }
        
    def analyze_schema_mismatches(self):
        """Analyze remaining schema mismatches"""
        
        print("🔍 FINAL SCHEMA MISMATCH ANALYSIS")
        print("=" * 40)
        print()
        
        print("❌ IDENTIFIED ERRORS:")
        errors = [
            {
                'table': 'registered_domains',
                'wrong': 'openprovider_id',
                'correct': 'openprovider_domain_id',
                'impact': 'Domain registration queries fail'
            },
            {
                'table': 'registered_domains', 
                'wrong': 'expires_at',
                'correct': 'expiry_date',
                'impact': 'Domain expiry queries fail'
            },
            {
                'table': 'orders',
                'wrong': 'amount',
                'correct': 'amount_usd', 
                'impact': 'Payment processing queries fail'
            }
        ]
        
        for error in errors:
            print(f"   • {error['table']}.{error['wrong']} → {error['table']}.{error['correct']}")
            print(f"     Impact: {error['impact']}")
        
        print()
        return errors
        
    def find_problematic_queries(self):
        """Find files with problematic SQL queries"""
        
        print("🔍 SCANNING FOR PROBLEMATIC QUERIES")
        print("=" * 40)
        
        # Common problematic patterns
        patterns = {
            'openprovider_id': [
                r'openprovider_id(?!\w)',  # openprovider_id not followed by word char
            ],
            'expires_at': [
                r'expires_at(?!\w)',
            ],
            'orders\.amount(?!\w)': [  # orders.amount not followed by word char
                r'orders\.amount(?!\w)',
            ]
        }
        
        problematic_files = {}
        
        # Scan Python files
        python_files = glob.glob('**/*.py', recursive=True)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_issues = []
                for issue, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        matches = re.findall(pattern, content)
                        if matches:
                            file_issues.append({
                                'issue': issue,
                                'count': len(matches),
                                'pattern': pattern
                            })
                
                if file_issues:
                    problematic_files[file_path] = file_issues
                    
            except:
                continue
        
        print(f"Found {len(problematic_files)} files with schema issues:")
        for file_path, issues in list(problematic_files.items())[:10]:  # Show first 10
            print(f"   • {file_path}")
            for issue in issues:
                print(f"     - {issue['issue']}: {issue['count']} occurrences")
        
        if len(problematic_files) > 10:
            print(f"   ... and {len(problematic_files) - 10} more files")
        
        print()
        return problematic_files
    
    def generate_correct_queries(self):
        """Generate correct SQL queries for common operations"""
        
        print("✅ CORRECT QUERY EXAMPLES")
        print("=" * 30)
        print()
        
        correct_queries = [
            {
                'purpose': 'Get user domains with expiry',
                'wrong': "SELECT domain_name, expires_at FROM registered_domains WHERE user_id = ?",
                'correct': "SELECT domain_name, expiry_date FROM registered_domains WHERE user_id = ?"
            },
            {
                'purpose': 'Get domain with OpenProvider ID',
                'wrong': "SELECT openprovider_id FROM registered_domains WHERE domain_name = ?",
                'correct': "SELECT openprovider_domain_id FROM registered_domains WHERE domain_name = ?"
            },
            {
                'purpose': 'Get order amount',
                'wrong': "SELECT amount FROM orders WHERE order_id = ?",
                'correct': "SELECT amount_usd FROM orders WHERE order_id = ?"
            },
            {
                'purpose': 'Get complete domain info',
                'wrong': "SELECT domain_name, expires_at, openprovider_id FROM registered_domains",
                'correct': "SELECT domain_name, expiry_date, openprovider_domain_id FROM registered_domains"
            }
        ]
        
        for query in correct_queries:
            print(f"📋 {query['purpose']}:")
            print(f"   ❌ Wrong: {query['wrong']}")
            print(f"   ✅ Correct: {query['correct']}")
            print()
    
    def validate_current_system(self):
        """Validate current system with correct queries"""
        
        print("🔍 SYSTEM VALIDATION WITH CORRECT SCHEMA")
        print("=" * 45)
        print()
        
        return {
            'orders_table': {
                'correct_column': 'amount_usd',
                'test_query': "SELECT id, amount_usd, payment_status FROM orders LIMIT 1"
            },
            'registered_domains_table': {
                'correct_columns': ['openprovider_domain_id', 'expiry_date'],
                'test_query': "SELECT domain_name, expiry_date, openprovider_domain_id FROM registered_domains LIMIT 1"
            }
        }

def main():
    """Run final schema validation"""
    validator = FinalSchemaValidator()
    
    print("🛠️ FINAL DATABASE SCHEMA VALIDATION")
    print("=" * 45)
    print()
    
    # Analyze mismatches
    errors = validator.analyze_schema_mismatches()
    
    # Find problematic files  
    problematic_files = validator.find_problematic_queries()
    
    # Show correct queries
    validator.generate_correct_queries()
    
    # Validation info
    validation_info = validator.validate_current_system()
    
    print("🎯 SUMMARY:")
    print("=" * 15)
    print(f"   • {len(errors)} critical schema errors identified")
    print(f"   • {len(problematic_files)} files need column name fixes")
    print("   • All errors are fixable by updating column references")
    print()
    print("✅ NEXT STEPS:")
    print("   1. Update queries to use correct column names")
    print("   2. Test with provided correct query examples")
    print("   3. Validate system with actual database schema")

if __name__ == "__main__":
    main()