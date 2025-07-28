
#!/usr/bin/env python3
"""
Registration Health Monitor
==========================

Monitors registration system health and alerts on API issues.
"""

import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class RegistrationHealthMonitor:
    """Monitors registration system health"""
    
    def __init__(self):
        self.last_check = None
        self.issues_detected = []
        
    def check_api_health(self):
        """Check all critical API methods are available"""
        try:
            # Check OpenProvider API
            from apis.production_openprovider import OpenProviderAPI
            op_api = OpenProviderAPI()
            
            critical_methods = [
                'update_domain_nameservers',
                'update_nameservers', 
                '_authenticate',
                '_create_customer_handle'
            ]
            
            missing_methods = []
            for method in critical_methods:
                if not hasattr(op_api, method):
                    missing_methods.append(method)
                    
            if missing_methods:
                issue = f"Missing OpenProvider methods: {missing_methods}"
                logger.error(f"🚨 CRITICAL: {issue}")
                self.issues_detected.append(issue)
                return False
                
            # Check Cloudflare API
            from apis.production_cloudflare import CloudflareAPI
            cf_api = CloudflareAPI()
            
            cf_methods = ['create_zone', 'get_nameservers', 'add_dns_record_async']
            cf_missing = []
            for method in cf_methods:
                if not hasattr(cf_api, method):
                    cf_missing.append(method)
                    
            if cf_missing:
                issue = f"Missing Cloudflare methods: {cf_missing}"
                logger.error(f"🚨 CRITICAL: {issue}")
                self.issues_detected.append(issue)
                return False
                
            logger.info("✅ All critical API methods available")
            self.last_check = datetime.now()
            return True
            
        except Exception as e:
            issue = f"API health check failed: {e}"
            logger.error(f"🚨 CRITICAL: {issue}")
            self.issues_detected.append(issue)
            return False
            
    def get_health_report(self):
        """Get health report"""
        return {
            "healthy": len(self.issues_detected) == 0,
            "last_check": self.last_check,
            "issues": self.issues_detected,
            "issue_count": len(self.issues_detected)
        }
        
    def run_continuous_monitoring(self, interval_minutes=5):
        """Run continuous monitoring"""
        logger.info(f"🔄 Starting continuous health monitoring (every {interval_minutes} min)")
        
        while True:
            logger.info("🔍 Running registration health check...")
            self.check_api_health()
            
            report = self.get_health_report()
            if report["healthy"]:
                logger.info("💚 Registration system healthy")
            else:
                logger.error(f"🚨 Registration system issues: {report['issue_count']}")
                
            time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    monitor = RegistrationHealthMonitor()
    monitor.run_continuous_monitoring(interval_minutes=10)
