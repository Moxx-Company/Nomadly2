#!/usr/bin/env python3
"""
Database Schema Mismatch Analyzer
=================================

This script analyzes the entire codebase to detect mismatched column names
between what the code expects and what actually exists in the database.

It performs:
1. Database schema inspection (actual columns)
2. Code analysis for SQL queries and ORM references
3. Mismatch detection and reporting
4. Suggested fixes generation

Author: Nomadly2 Development Team
Date: July 22, 2025
"""

import os
import re
import logging
from typing import Dict, List, Set, Tuple
from database import get_db_manager
from sqlalchemy import text, inspect

logger = logging.getLogger(__name__)

class DatabaseSchemaMismatchDetector:
    """Detect mismatches between database schema and code expectations"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.actual_schema = {}
        self.code_references = {}
        self.mismatches = []
        
    def get_actual_database_schema(self) -> Dict[str, Dict[str, str]]:
        """Get the actual database schema with all tables and columns"""
        try:
            logger.info("🔍 Analyzing actual database schema...")
            
            with self.db.get_session() as session:
                # Get all tables and their columns
                schema_query = text("""
                    SELECT table_name, column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position;
                """)
                
                result = session.execute(schema_query)
                rows = result.fetchall()
                
                schema = {}
                for row in rows:
                    table_name = row.table_name
                    if table_name not in schema:
                        schema[table_name] = {}
                    
                    schema[table_name][row.column_name] = {
                        'type': row.data_type,
                        'nullable': row.is_nullable
                    }
                
                logger.info(f"✅ Found {len(schema)} tables with {sum(len(cols) for cols in schema.values())} columns")
                return schema
                
        except Exception as e:
            logger.error(f"❌ Failed to get database schema: {e}")
            return {}
    
    def analyze_code_for_column_references(self) -> Dict[str, Set[str]]:
        """Analyze all Python files for database column references"""
        try:
            logger.info("🔍 Analyzing code for column references...")
            
            references = {}
            python_files = []
            
            # Find all Python files
            for root, dirs, files in os.walk('.'):
                # Skip hidden directories and common non-code directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            logger.info(f"📁 Analyzing {len(python_files)} Python files...")
            
            # Patterns to detect column references
            patterns = {
                'sql_select': r'SELECT\s+([^FROM]+)\s+FROM\s+(\w+)',
                'sql_where': r'WHERE\s+(\w+)\.(\w+)',
                'sql_join': r'JOIN\s+\w+\s+\w+\s+ON\s+(\w+)\.(\w+)',
                'sql_column': r'(\w+)\.(\w+)\s*[=<>!]',
                'jsonb_access': r'(\w+)->>\s*[\'"](\w+)[\'"]',
                'model_attr': r'(\w+)\.(\w+)\s*[,\s]',
                'dict_access': r'[\'"](\w+)[\'"]\s*:\s*',
            }
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Extract table.column references
                    for pattern_name, pattern in patterns.items():
                        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                        
                        for match in matches:
                            if isinstance(match, tuple) and len(match) == 2:
                                table, column = match
                                
                                # Filter likely table names
                                likely_tables = ['users', 'orders', 'registered_domains', 'wallet_transactions', 'user_states']
                                if table.lower() in likely_tables:
                                    if table not in references:
                                        references[table] = set()
                                    references[table].add(column)
                
                except Exception as e:
                    logger.debug(f"Skipping {file_path}: {e}")
            
            logger.info(f"✅ Found references to {len(references)} tables")
            return references
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze code: {e}")
            return {}
    
    def detect_mismatches(self) -> List[Dict]:
        """Compare actual schema with code references to find mismatches"""
        try:
            logger.info("🔍 Detecting schema mismatches...")
            
            mismatches = []
            
            for table_name, referenced_columns in self.code_references.items():
                if table_name not in self.actual_schema:
                    mismatches.append({
                        'type': 'missing_table',
                        'table': table_name,
                        'issue': f'Table {table_name} referenced in code but does not exist',
                        'severity': 'high'
                    })
                    continue
                
                actual_columns = set(self.actual_schema[table_name].keys())
                
                for column in referenced_columns:
                    if column not in actual_columns:
                        # Try to find similar column names
                        similar = self.find_similar_columns(column, actual_columns)
                        
                        mismatches.append({
                            'type': 'missing_column',
                            'table': table_name,
                            'expected_column': column,
                            'actual_columns': list(actual_columns),
                            'similar_columns': similar,
                            'issue': f'Column {table_name}.{column} referenced in code but does not exist',
                            'severity': 'high' if not similar else 'medium',
                            'suggested_fix': similar[0] if similar else None
                        })
            
            logger.info(f"🔍 Found {len(mismatches)} potential mismatches")
            return mismatches
            
        except Exception as e:
            logger.error(f"❌ Failed to detect mismatches: {e}")
            return []
    
    def find_similar_columns(self, target_column: str, actual_columns: Set[str]) -> List[str]:
        """Find similar column names using fuzzy matching"""
        similar = []
        target_lower = target_column.lower()
        
        for col in actual_columns:
            col_lower = col.lower()
            
            # Exact substring match
            if target_lower in col_lower or col_lower in target_lower:
                similar.append(col)
            
            # Common column name mappings
            mappings = {
                'amount_usd': 'amount',
                'expires_at': 'expiry_date', 
                'zone_id': 'cloudflare_zone_id',
                'metadata': 'service_details',
                'transaction_id': 'order_id'
            }
            
            if target_lower in mappings and mappings[target_lower] == col_lower:
                similar.append(col)
        
        return similar[:3]  # Return top 3 matches
    
    def analyze_specific_files_for_sql(self) -> Dict[str, List[str]]:
        """Analyze specific files known to contain SQL queries"""
        sql_files = [
            'nomadly2_bot.py',
            'payment_service.py', 
            'domain_service.py',
            'fixed_registration_service.py',
            'live_order_monitor.py',
            'models.py'
        ]
        
        sql_issues = {}
        
        for file_name in sql_files:
            if os.path.exists(file_name):
                try:
                    with open(file_name, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for common problematic patterns
                    issues = []
                    
                    # Check for amount vs amount
                    if 'amount_usd' in content and 'wallet_transactions' in content:
                        issues.append('Uses amount instead of amount in wallet_transactions')
                    
                    # Check for expiry_date vs expiry_date  
                    if 'expires_at' in content and 'registered_domains' in content:
                        issues.append('Uses expiry_date instead of expiry_date in registered_domains')
                    
                    # Check for cloudflare_zone_id vs cloudflare_zone_id
                    if re.search(r'\bzone_id\b', content) and 'registered_domains' in content:
                        issues.append('Uses cloudflare_zone_id instead of cloudflare_zone_id in registered_domains')
                    
                    # Check for JSONB without casting
                    if re.search(r'service_details\s+LIKE', content, re.IGNORECASE):
                        issues.append('JSONB LIKE without ::text casting')
                    
                    if issues:
                        sql_issues[file_name] = issues
                        
                except Exception as e:
                    logger.debug(f"Could not analyze {file_name}: {e}")
        
        return sql_issues
    
    def generate_fix_script(self, mismatches: List[Dict]) -> str:
        """Generate a Python script to fix the detected issues"""
        fixes = []
        
        for mismatch in mismatches:
            if mismatch['type'] == 'missing_column' and mismatch.get('suggested_fix'):
                table = mismatch['table']
                wrong_col = mismatch['expected_column'] 
                correct_col = mismatch['suggested_fix']
                
                fixes.append(f"# Fix {table}.{wrong_col} -> {table}.{correct_col}")
                fixes.append(f'# Search and replace: "{table}.{wrong_col}" with "{table}.{correct_col}"')
                fixes.append("")
        
        return "\n".join(fixes)
    
    def run_complete_analysis(self) -> Dict:
        """Run complete schema mismatch analysis"""
        try:
            logger.info("🚀 STARTING COMPLETE DATABASE SCHEMA ANALYSIS")
            logger.info("=" * 60)
            
            # Step 1: Get actual database schema
            self.actual_schema = self.get_actual_database_schema()
            
            # Step 2: Analyze code for column references
            self.code_references = self.analyze_code_for_column_references()
            
            # Step 3: Detect mismatches
            self.mismatches = self.detect_mismatches()
            
            # Step 4: Analyze SQL files for known issues
            sql_issues = self.analyze_specific_files_for_sql()
            
            # Step 5: Generate report
            report = {
                'actual_schema': self.actual_schema,
                'code_references': {k: list(v) for k, v in self.code_references.items()},
                'mismatches': self.mismatches,
                'sql_file_issues': sql_issues,
                'summary': {
                    'total_tables': len(self.actual_schema),
                    'total_mismatches': len(self.mismatches),
                    'high_severity': len([m for m in self.mismatches if m['severity'] == 'high']),
                    'files_with_sql_issues': len(sql_issues)
                }
            }
            
            logger.info("✅ ANALYSIS COMPLETE")
            return report
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return {}

def main():
    """Run the database schema mismatch detection"""
    print("🔍 DATABASE SCHEMA MISMATCH ANALYZER")
    print("=" * 50)
    
    try:
        analyzer = DatabaseSchemaMismatchDetector()
        report = analyzer.run_complete_analysis()
        
        if report:
            print(f"\n📊 ANALYSIS RESULTS:")
            print(f"   Tables in database: {report['summary']['total_tables']}")
            print(f"   Schema mismatches found: {report['summary']['total_mismatches']}")
            print(f"   High severity issues: {report['summary']['high_severity']}")
            print(f"   Files with SQL issues: {report['summary']['files_with_sql_issues']}")
            
            print(f"\n🔍 DETAILED MISMATCHES:")
            for mismatch in report['mismatches']:
                severity_icon = "🔥" if mismatch['severity'] == 'high' else "⚠️"
                print(f"   {severity_icon} {mismatch['issue']}")
                if mismatch.get('suggested_fix'):
                    print(f"      💡 Suggested fix: Use '{mismatch['suggested_fix']}' instead")
            
            print(f"\n🔍 SQL FILE ISSUES:")
            for file_name, issues in report['sql_file_issues'].items():
                print(f"   📁 {file_name}:")
                for issue in issues:
                    print(f"      ⚠️ {issue}")
            
            if report['mismatches'] or report['sql_file_issues']:
                print(f"\n💡 RECOMMENDATION: Review and fix these schema mismatches")
                print(f"   Use the corrected_sql_queries.py reference for proper column names")
            else:
                print(f"\n✅ NO SCHEMA MISMATCHES DETECTED")
                print(f"   Database schema and code references are aligned")
            
        else:
            print("\n❌ ANALYSIS FAILED - Check logs for details")
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()