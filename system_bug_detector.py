#!/usr/bin/env python3
"""
System Bug Detector for Nomadly2 Bot
Comprehensive testing to identify remaining system issues
"""

import asyncio
import logging
import os
import json
import traceback
from datetime import datetime
from database import get_db_manager
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BugDetector:
    def __init__(self):
        self.db = get_db_manager()
        self.bugs_found = []
        self.system_status = {}
        
    async def detect_all_bugs(self):
        """Run comprehensive bug detection across the system"""
        print("🔍 NOMADLY2 SYSTEM BUG DETECTION")
        print("=" * 40)
        
        detection_tests = [
            ("Import Dependencies", self.check_import_issues),
            ("Database Schema", self.check_database_schema),
            ("Environment Variables", self.check_environment_config),
            ("API Credentials", self.check_api_credentials),
            ("File Structure", self.check_file_structure),
            ("Webhook Configuration", self.check_webhook_config),
            ("Registration Pipeline", self.check_registration_pipeline),
            ("Notification System", self.check_notification_system),
            ("Payment Processing", self.check_payment_processing),
            ("Bot Interface", self.check_bot_interface)
        ]
        
        for test_name, test_func in detection_tests:
            print(f"\n🔍 Checking {test_name}...")
            try:
                issues = await test_func()
                if issues:
                    print(f"🐛 Found {len(issues)} issues in {test_name}")
                    for issue in issues:
                        print(f"   - {issue}")
                        self.bugs_found.append(f"{test_name}: {issue}")
                else:
                    print(f"✅ {test_name}: No issues found")
                    
            except Exception as e:
                error_msg = f"{test_name} check failed: {e}"
                print(f"❌ {error_msg}")
                self.bugs_found.append(error_msg)
        
        return self.generate_bug_report()
    
    async def check_import_issues(self):
        """Check for import-related issues"""
        issues = []
        
        critical_imports = [
            ("database", "get_db_manager"),
            ("payment_service", "get_payment_service"),
            ("services.confirmation_service", "get_confirmation_service"),
            ("apis.production_openprovider", "OpenProviderAPI"),
            ("apis.production_cloudflare", "CloudflareAPI"),
            ("domain_service", "get_domain_service"),
            ("nomadly2_bot", None)
        ]
        
        for module_name, class_name in critical_imports:
            try:
                module = __import__(module_name, fromlist=[class_name] if class_name else [])
                if class_name and not hasattr(module, class_name):
                    issues.append(f"Missing {class_name} in {module_name}")
            except ImportError as e:
                issues.append(f"Cannot import {module_name}: {e}")
                
        return issues
    
    async def check_database_schema(self):
        """Check database schema and critical tables"""
        issues = []
        
        try:
            with self.db.get_session() as session:
                # Check critical tables exist
                required_tables = ['users', 'orders', 'registered_domains']
                
                for table in required_tables:
                    try:
                        result = session.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                        count = result[0]
                        print(f"   📊 Table {table}: {count} records")
                    except Exception as e:
                        issues.append(f"Table {table} missing or inaccessible: {e}")
                
                # Check for recent order processing
                try:
                    recent_orders = session.execute(text("""
                        SELECT COUNT(*) FROM orders 
                        WHERE created_at > NOW() - INTERVAL '24 hours'
                    """)).fetchone()[0]
                    
                    if recent_orders == 0:
                        issues.append("No recent orders in last 24 hours - system may be inactive")
                        
                except Exception as e:
                    issues.append(f"Cannot check recent orders: {e}")
                    
        except Exception as e:
            issues.append(f"Database connectivity issue: {e}")
            
        return issues
    
    async def check_environment_config(self):
        """Check environment variables configuration"""
        issues = []
        
        critical_env_vars = [
            'DATABASE_URL',
            'TELEGRAM_BOT_TOKEN', 
            'BLOCKBEE_API_KEY',
            'CLOUDFLARE_API_TOKEN',
            'OPENPROVIDER_USERNAME',
            'OPENPROVIDER_PASSWORD'
        ]
        
        for var in critical_env_vars:
            value = os.getenv(var)
            if not value:
                issues.append(f"Missing environment variable: {var}")
            elif len(value) < 10:  # Basic validation
                issues.append(f"Environment variable {var} seems too short")
                
        return issues
    
    async def check_api_credentials(self):
        """Check API credentials are working"""
        issues = []
        
        # Check OpenProvider
        try:
            from apis.production_openprovider import OpenProviderAPI
            openprovider = OpenProviderAPI()
            auth_result = await openprovider._authenticate_openprovider()
            if not auth_result:
                issues.append("OpenProvider authentication failed")
        except Exception as e:
            issues.append(f"OpenProvider API error: {e}")
        
        # Check Cloudflare
        try:
            from apis.production_cloudflare import CloudflareAPI
            cf = CloudflareAPI()
            # Basic connectivity test
            if not cf._has_valid_credentials():
                issues.append("Cloudflare credentials invalid")
        except Exception as e:
            issues.append(f"Cloudflare API error: {e}")
        
        return issues
    
    async def check_file_structure(self):
        """Check critical files exist"""
        issues = []
        
        critical_files = [
            'webhook_server.py',
            'nomadly2_bot.py',
            'payment_service.py',
            'database.py',
            'domain_service.py',
            'apis/production_openprovider.py',
            'apis/production_cloudflare.py',
            'services/confirmation_service.py'
        ]
        
        for file_path in critical_files:
            if not os.path.exists(file_path):
                issues.append(f"Missing critical file: {file_path}")
                
        return issues
    
    async def check_webhook_config(self):
        """Check webhook server configuration"""
        issues = []
        
        try:
            # Check webhook server file
            with open('webhook_server.py', 'r') as f:
                content = f.read()
                
                # Check for critical webhook functions
                if 'handle_blockbee_webhook' not in content:
                    issues.append("Missing webhook handler function")
                    
                if 'process_payment_confirmation' not in content:
                    issues.append("Missing payment confirmation processor")
                    
                # Check for database query fixes
                if 'order.telegram_id' not in content:
                    issues.append("Webhook may have database query issues")
                    
        except Exception as e:
            issues.append(f"Cannot analyze webhook server: {e}")
            
        return issues
    
    async def check_registration_pipeline(self):
        """Check domain registration pipeline"""
        issues = []
        
        try:
            from fixed_registration_service import FixedRegistrationService
            registration_service = FixedRegistrationService()
            
            # Check critical methods exist
            methods_to_check = [
                '_authenticate_openprovider',
                '_create_or_get_customer', 
                '_register_domain_with_openprovider',
                '_save_domain_to_database'
            ]
            
            for method in methods_to_check:
                if not hasattr(registration_service, method):
                    issues.append(f"Missing registration method: {method}")
                    
        except ImportError:
            issues.append("Cannot import FixedRegistrationService")
        except Exception as e:
            issues.append(f"Registration service check failed: {e}")
            
        return issues
    
    async def check_notification_system(self):
        """Check notification system functionality"""
        issues = []
        
        try:
            from services.confirmation_service import get_confirmation_service
            confirmation_service = get_confirmation_service()
            
            # Check critical methods
            methods_to_check = [
                'send_payment_confirmation',
                'send_domain_registration_confirmation'
            ]
            
            for method in methods_to_check:
                if not hasattr(confirmation_service, method):
                    issues.append(f"Missing notification method: {method}")
                    
        except Exception as e:
            issues.append(f"Notification service check failed: {e}")
            
        return issues
    
    async def check_payment_processing(self):
        """Check payment processing pipeline"""
        issues = []
        
        try:
            from payment_service import get_payment_service
            payment_service = get_payment_service()
            
            # Check critical methods
            methods_to_check = [
                'complete_domain_registration',
                'create_crypto_payment',
                'process_wallet_deposit_with_any_amount'
            ]
            
            for method in methods_to_check:
                if not hasattr(payment_service, method):
                    issues.append(f"Missing payment method: {method}")
                    
        except Exception as e:
            issues.append(f"Payment service check failed: {e}")
            
        return issues
    
    async def check_bot_interface(self):
        """Check bot interface functionality"""
        issues = []
        
        try:
            # Check if bot file exists and has basic structure
            with open('nomadly2_bot.py', 'r') as f:
                content = f.read()
                
                # Check for critical bot functions
                if 'Application' not in content:
                    issues.append("Bot may not have proper Application setup")
                    
                if 'MessageHandler' not in content:
                    issues.append("Bot may be missing message handlers")
                    
                if 'CallbackQueryHandler' not in content:
                    issues.append("Bot may be missing callback handlers")
                    
        except Exception as e:
            issues.append(f"Cannot analyze bot interface: {e}")
            
        return issues
    
    def generate_bug_report(self):
        """Generate comprehensive bug report"""
        print(f"\n📋 COMPREHENSIVE BUG REPORT")
        print("=" * 35)
        
        if not self.bugs_found:
            print("✅ NO CRITICAL BUGS DETECTED!")
            print("System appears to be operational.")
            return {"status": "healthy", "bugs": []}
        
        print(f"🐛 FOUND {len(self.bugs_found)} ISSUES:")
        
        # Categorize bugs
        critical_bugs = []
        warning_issues = []
        
        for bug in self.bugs_found:
            if any(keyword in bug.lower() for keyword in ['missing', 'failed', 'error', 'cannot']):
                critical_bugs.append(bug)
            else:
                warning_issues.append(bug)
        
        if critical_bugs:
            print(f"\n🚨 CRITICAL ISSUES ({len(critical_bugs)}):")
            for i, bug in enumerate(critical_bugs, 1):
                print(f"   {i}. {bug}")
        
        if warning_issues:
            print(f"\n⚠️  WARNINGS ({len(warning_issues)}):")
            for i, bug in enumerate(warning_issues, 1):
                print(f"   {i}. {bug}")
        
        # Generate recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if any('import' in bug.lower() for bug in self.bugs_found):
            print("   - Fix import/dependency issues first")
        if any('database' in bug.lower() for bug in self.bugs_found):
            print("   - Check database connectivity and schema")
        if any('environment' in bug.lower() for bug in self.bugs_found):
            print("   - Verify environment variable configuration")
        if any('api' in bug.lower() for bug in self.bugs_found):
            print("   - Validate API credentials and connectivity")
        
        return {
            "status": "needs_attention",
            "total_bugs": len(self.bugs_found),
            "critical": critical_bugs,
            "warnings": warning_issues
        }

async def main():
    """Run comprehensive bug detection"""
    detector = BugDetector()
    report = await detector.detect_all_bugs()
    
    print(f"\n🎯 SYSTEM STATUS: {report['status'].upper()}")
    if report['status'] == 'needs_attention':
        print(f"   Priority: Fix {len(report.get('critical', []))} critical issues first")

if __name__ == "__main__":
    asyncio.run(main())