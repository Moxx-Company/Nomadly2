#!/usr/bin/env python3
"""
Comprehensive Nomadly3 Project Audit
Checks for accuracy, bugs, duplicates, and production readiness
"""

import os
import re
import ast
import json
from pathlib import Path
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class Nomadly3ProjectAuditor:
    """Comprehensive project auditor for 100% coverage"""
    
    def __init__(self):
        self.issues = []
        self.duplicates = []
        self.bugs = []
        self.missing_components = []
        self.bot_files = []
        self.controller_files = []
        self.api_routes = []
        
    def run_comprehensive_audit(self):
        """Execute complete project audit"""
        print("🔍 NOMADLY3 COMPREHENSIVE PROJECT AUDIT")
        print("=" * 50)
        
        # 1. Identify all bot files and check for duplicates
        self.audit_bot_files()
        
        # 2. Check database integrity and models
        self.audit_database_layer()
        
        # 3. Validate API endpoints and routes
        self.audit_api_layer()
        
        # 4. Check for controller/handler duplicates
        self.audit_controller_layer()
        
        # 5. Validate schema consistency
        self.audit_schema_layer()
        
        # 6. Check service layer completeness
        self.audit_service_layer()
        
        # 7. Validate workflow configurations
        self.audit_workflow_configurations()
        
        # 8. Check for production readiness issues
        self.audit_production_readiness()
        
        # Generate comprehensive report
        self.generate_audit_report()
        
        return {
            'total_issues': len(self.issues),
            'bugs_found': len(self.bugs),
            'duplicates': len(self.duplicates),
            'missing_components': len(self.missing_components)
        }
    
    def audit_bot_files(self):
        """Audit bot files for duplicates and consistency"""
        print("\n📱 1. BOT FILES AUDIT")
        print("-" * 30)
        
        # Find all bot files
        bot_patterns = [
            "*bot*.py",
            "*nomadly*.py", 
            "*telegram*.py"
        ]
        
        for pattern in bot_patterns:
            for file in Path(".").glob(pattern):
                if file.is_file() and file.suffix == ".py":
                    self.bot_files.append(str(file))
                    
        print(f"Found {len(self.bot_files)} bot files:")
        for bot_file in self.bot_files:
            print(f"  - {bot_file}")
            
        # Check for duplicate bot implementations
        if len(self.bot_files) > 3:
            self.issues.append(f"Multiple bot files detected ({len(self.bot_files)}) - potential duplicates")
            
        # Analyze main bot file for issues
        self.analyze_main_bot_file()
    
    def analyze_main_bot_file(self):
        """Analyze nomadly3_fixed_bot.py for issues"""
        bot_file = "nomadly3_fixed_bot.py"
        
        if not os.path.exists(bot_file):
            self.bugs.append("Main bot file nomadly3_fixed_bot.py not found")
            return
            
        try:
            with open(bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for token exposure
            if "8058274028:" in content:
                self.bugs.append("Bot token exposed in source code")
                
            # Check for proper error handling
            if "try:" not in content:
                self.issues.append("Bot lacks proper error handling")
                
            # Check for callback handler completeness
            callback_handlers = re.findall(r'elif.*data.*==.*["\']([^"\']+)["\']', content)
            callback_definitions = re.findall(r'callback_data=["\']([^"\']+)["\']', content)
            
            missing_handlers = set(callback_definitions) - set(callback_handlers)
            if missing_handlers:
                self.bugs.append(f"Missing callback handlers: {missing_handlers}")
                
            print(f"  ✅ Analyzed {bot_file}")
            print(f"    - Callback handlers: {len(callback_handlers)}")
            print(f"    - Callback definitions: {len(callback_definitions)}")
            if missing_handlers:
                print(f"    - Missing handlers: {missing_handlers}")
                
        except Exception as e:
            self.bugs.append(f"Error analyzing bot file: {e}")
    
    def audit_database_layer(self):
        """Audit database models and connections"""
        print("\n💾 2. DATABASE LAYER AUDIT")
        print("-" * 30)
        
        # Check for database files
        db_files = [
            "database.py",
            "fresh_database.py", 
            "models.py",
            "app/models/*.py"
        ]
        
        found_db_files = []
        for pattern in db_files:
            if '*' in pattern:
                for file in Path(".").glob(pattern):
                    found_db_files.append(str(file))
            elif os.path.exists(pattern):
                found_db_files.append(pattern)
                
        print(f"Found {len(found_db_files)} database files:")
        for db_file in found_db_files:
            print(f"  - {db_file}")
            
        # Check for model conflicts
        if len(found_db_files) > 2:
            self.issues.append("Multiple database model files - potential conflicts")
            
        # Validate fresh_database.py
        self.validate_database_models()
    
    def validate_database_models(self):
        """Validate database model definitions"""
        if os.path.exists("fresh_database.py"):
            try:
                with open("fresh_database.py", 'r') as f:
                    content = f.read()
                    
                # Check for table definitions
                tables = re.findall(r'class (\w+)\(.*Base.*\):', content)
                print(f"  Database tables found: {len(tables)}")
                for table in tables[:5]:  # Show first 5
                    print(f"    - {table}")
                if len(tables) > 5:
                    print(f"    ... and {len(tables) - 5} more")
                    
                # Check for foreign key relationships
                foreign_keys = re.findall(r'ForeignKey\(["\']([^"\']+)["\']', content)
                print(f"  Foreign key relationships: {len(foreign_keys)}")
                
            except Exception as e:
                self.bugs.append(f"Error validating database models: {e}")
    
    def audit_api_layer(self):
        """Audit API routes and endpoints"""
        print("\n🌐 3. API LAYER AUDIT")
        print("-" * 30)
        
        # Find API route files
        api_patterns = [
            "app/api/routes/*.py",
            "app/routes/*.py",
            "*routes*.py"
        ]
        
        for pattern in api_patterns:
            for file in Path(".").glob(pattern):
                if file.is_file() and file.suffix == ".py":
                    self.api_routes.append(str(file))
                    
        print(f"Found {len(self.api_routes)} API route files:")
        for route_file in self.api_routes:
            print(f"  - {route_file}")
            
        # Check for duplicate routes
        self.check_duplicate_routes()
    
    def check_duplicate_routes(self):
        """Check for duplicate API routes"""
        all_routes = {}
        
        for route_file in self.api_routes:
            try:
                with open(route_file, 'r') as f:
                    content = f.read()
                    
                # Find route definitions
                routes = re.findall(r'@\w+\.(?:get|post|put|delete)\(["\']([^"\']+)["\']', content)
                
                for route in routes:
                    if route in all_routes:
                        self.duplicates.append(f"Duplicate route {route} in {route_file} and {all_routes[route]}")
                    else:
                        all_routes[route] = route_file
                        
            except Exception as e:
                self.bugs.append(f"Error analyzing route file {route_file}: {e}")
    
    def audit_controller_layer(self):
        """Audit controllers for duplicates"""
        print("\n🎮 4. CONTROLLER LAYER AUDIT")
        print("-" * 30)
        
        # Find controller files
        controller_patterns = [
            "app/controllers/*.py",
            "*controller*.py"
        ]
        
        for pattern in controller_patterns:
            for file in Path(".").glob(pattern):
                if file.is_file() and file.suffix == ".py":
                    self.controller_files.append(str(file))
                    
        print(f"Found {len(self.controller_files)} controller files:")
        for controller_file in self.controller_files:
            print(f"  - {controller_file}")
            
        # Check for duplicate methods
        self.check_duplicate_controller_methods()
    
    def check_duplicate_controller_methods(self):
        """Check for duplicate controller methods"""
        all_methods = defaultdict(list)
        
        for controller_file in self.controller_files:
            try:
                with open(controller_file, 'r') as f:
                    content = f.read()
                    
                # Find method definitions
                methods = re.findall(r'async def (\w+)\(', content)
                
                for method in methods:
                    all_methods[method].append(controller_file)
                    
            except Exception as e:
                self.bugs.append(f"Error analyzing controller {controller_file}: {e}")
                
        # Report duplicates
        for method, files in all_methods.items():
            if len(files) > 1:
                self.duplicates.append(f"Duplicate method {method} in: {files}")
    
    def audit_schema_layer(self):
        """Audit Pydantic schemas"""
        print("\n📋 5. SCHEMA LAYER AUDIT")
        print("-" * 30)
        
        schema_dir = Path("app/schemas")
        if not schema_dir.exists():
            self.missing_components.append("app/schemas directory missing")
            return
            
        schema_files = list(schema_dir.glob("*.py"))
        print(f"Found {len(schema_files)} schema files:")
        
        for schema_file in schema_files:
            print(f"  - {schema_file}")
            
        # Check for required schemas
        required_schemas = [
            "domain_schemas.py",
            "dns_schemas.py", 
            "user_schemas.py",
            "wallet_schemas.py"
        ]
        
        for required in required_schemas:
            if not (schema_dir / required).exists():
                self.missing_components.append(f"Missing required schema: {required}")
    
    def audit_service_layer(self):
        """Audit service layer completeness"""
        print("\n⚙️ 6. SERVICE LAYER AUDIT")
        print("-" * 30)
        
        service_dir = Path("app/services")
        if not service_dir.exists():
            self.missing_components.append("app/services directory missing")
            return
            
        service_files = list(service_dir.glob("*.py"))
        print(f"Found {len(service_files)} service files:")
        
        for service_file in service_files:
            print(f"  - {service_file}")
    
    def audit_workflow_configurations(self):
        """Audit workflow configurations"""
        print("\n🔄 7. WORKFLOW CONFIGURATION AUDIT")
        print("-" * 30)
        
        # Check for multiple workflow conflicts
        workflow_files = [
            "nomadly3_fixed_bot.py",
            "simple_admin_app.py",
            "start_fastapi_server.py"
        ]
        
        active_workflows = []
        for workflow_file in workflow_files:
            if os.path.exists(workflow_file):
                active_workflows.append(workflow_file)
                
        print(f"Active workflow files: {len(active_workflows)}")
        for workflow in active_workflows:
            print(f"  - {workflow}")
            
        # Check for bot token conflicts
        self.check_bot_token_conflicts()
    
    def check_bot_token_conflicts(self):
        """Check for bot token conflicts between files"""
        token_usage = {}
        
        for bot_file in self.bot_files:
            try:
                with open(bot_file, 'r') as f:
                    content = f.read()
                    
                tokens = re.findall(r'[0-9]+:[A-Za-z0-9_-]+', content)
                for token in tokens:
                    if token in token_usage:
                        self.issues.append(f"Bot token {token[:10]}... used in multiple files")
                    else:
                        token_usage[token] = bot_file
                        
            except Exception as e:
                self.bugs.append(f"Error checking tokens in {bot_file}: {e}")
    
    def audit_production_readiness(self):
        """Check production readiness issues"""
        print("\n🚀 8. PRODUCTION READINESS AUDIT")
        print("-" * 30)
        
        # Check for hardcoded secrets
        self.check_hardcoded_secrets()
        
        # Check for proper error handling
        self.check_error_handling()
        
        # Check for logging configuration
        self.check_logging_configuration()
    
    def check_hardcoded_secrets(self):
        """Check for hardcoded secrets in code"""
        secret_patterns = [
            r'[0-9]+:[A-Za-z0-9_-]+',  # Bot tokens
            r'sk_[A-Za-z0-9_-]+',      # API keys
            r'password\s*=\s*["\'][^"\']+["\']',  # Passwords
        ]
        
        for bot_file in self.bot_files + self.api_routes + self.controller_files:
            if not os.path.exists(bot_file):
                continue
                
            try:
                with open(bot_file, 'r') as f:
                    content = f.read()
                    
                for pattern in secret_patterns:
                    if re.search(pattern, content):
                        self.issues.append(f"Hardcoded secret pattern found in {bot_file}")
                        
            except Exception as e:
                continue
    
    def check_error_handling(self):
        """Check for proper error handling"""
        for bot_file in self.bot_files:
            if not os.path.exists(bot_file):
                continue
                
            try:
                with open(bot_file, 'r') as f:
                    content = f.read()
                    
                try_count = content.count('try:')
                except_count = content.count('except')
                
                if try_count == 0:
                    self.issues.append(f"No error handling in {bot_file}")
                elif except_count < try_count:
                    self.issues.append(f"Incomplete error handling in {bot_file}")
                    
            except Exception as e:
                continue
    
    def check_logging_configuration(self):
        """Check logging configuration"""
        logging_files = []
        
        for file_path in [*self.bot_files, *self.api_routes]:
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                if 'logging' in content:
                    logging_files.append(file_path)
                    
            except Exception:
                continue
                
        if not logging_files:
            self.issues.append("No logging configuration found")
        else:
            print(f"  Logging found in {len(logging_files)} files")
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print(f"\n📊 COMPREHENSIVE AUDIT REPORT")
        print("=" * 40)
        
        # Summary statistics
        total_issues = len(self.issues) + len(self.bugs) + len(self.duplicates) + len(self.missing_components)
        
        print(f"🔍 AUDIT SUMMARY:")
        print(f"  Total Issues Found: {total_issues}")
        print(f"  Bugs: {len(self.bugs)}")
        print(f"  Duplicates: {len(self.duplicates)}")
        print(f"  Missing Components: {len(self.missing_components)}")
        print(f"  General Issues: {len(self.issues)}")
        
        # Detailed findings
        if self.bugs:
            print(f"\n🐛 CRITICAL BUGS ({len(self.bugs)}):")
            for i, bug in enumerate(self.bugs, 1):
                print(f"  {i}. {bug}")
        
        if self.duplicates:
            print(f"\n📋 DUPLICATES ({len(self.duplicates)}):")
            for i, duplicate in enumerate(self.duplicates, 1):
                print(f"  {i}. {duplicate}")
        
        if self.missing_components:
            print(f"\n⚠️ MISSING COMPONENTS ({len(self.missing_components)}):")
            for i, missing in enumerate(self.missing_components, 1):
                print(f"  {i}. {missing}")
        
        if self.issues:
            print(f"\n📝 GENERAL ISSUES ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if total_issues == 0:
            print("  ✅ Project appears to be in good condition!")
        else:
            print("  1. Fix critical bugs immediately")
            print("  2. Remove duplicate implementations")
            print("  3. Add missing components")
            print("  4. Address production readiness issues")
            print("  5. Implement comprehensive error handling")
        
        return {
            'total_issues': total_issues,
            'bugs': self.bugs,
            'duplicates': self.duplicates,
            'missing': self.missing_components,
            'issues': self.issues
        }

if __name__ == "__main__":
    auditor = Nomadly3ProjectAuditor()
    results = auditor.run_comprehensive_audit()
    
    print(f"\n🎯 AUDIT COMPLETE")
    print(f"Results: {results['total_issues']} total issues found")