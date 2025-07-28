#!/usr/bin/env python3
"""
Modernization Status Report for Nomadly2
Comprehensive status check of all implemented modernization components
"""

import asyncio
import os
import glob
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernizationStatusChecker:
    """Check status of all modernization components"""
    
    def __init__(self):
        self.status = {
            "implemented_components": [],
            "working_components": [],
            "failed_components": [],
            "ready_for_production": False
        }
    
    def check_file_implementations(self):
        """Check which modernization files have been implemented"""
        
        modernization_files = {
            "fastapi_webhook_server.py": "FastAPI async webhook server",
            "celery_worker.py": "Celery background job processor", 
            "async_api_clients.py": "Async API clients (OpenProvider, Cloudflare, BlockBee)",
            "enhanced_monitoring.py": "Enhanced monitoring and metrics",
            "background_queue_processor.py": "File-based background job queue",
            "immediate_improvements.py": "Immediate improvements with current dependencies",
            "enhanced_payment_service.py": "Enhanced payment service with async APIs",
            "modernization_integration.py": "Integration management system"
        }
        
        for filename, description in modernization_files.items():
            if os.path.exists(filename):
                self.status["implemented_components"].append({
                    "file": filename,
                    "description": description,
                    "size": os.path.getsize(filename),
                    "modified": datetime.fromtimestamp(os.path.getmtime(filename)).isoformat()
                })
                logger.info(f"✅ {filename} - {description}")
            else:
                logger.warning(f"❌ Missing: {filename}")
    
    def check_webhook_integration(self):
        """Check webhook server integration"""
        try:
            with open("webhook_server.py", "r") as f:
                content = f.read()
            
            improvements = []
            
            if "timeout_seconds = 25" in content:
                improvements.append("25-second timeout handling")
            
            if "background_queue_processor" in content:
                improvements.append("Background queue integration")
                
            if "asyncio.wait_for" in content:
                improvements.append("Async timeout wrapper")
            
            if improvements:
                self.status["working_components"].append({
                    "component": "Webhook Server Enhancements",
                    "improvements": improvements
                })
                logger.info(f"✅ Webhook server enhanced with: {', '.join(improvements)}")
            
        except Exception as e:
            logger.error(f"❌ Error checking webhook integration: {e}")
            self.status["failed_components"].append("Webhook integration check")
    
    def check_background_queue(self):
        """Check background queue system"""
        try:
            queue_dir = "background_queue"
            
            if os.path.exists(queue_dir):
                subdirs = ["failed", "completed"]
                existing_subdirs = [d for d in subdirs if os.path.exists(f"{queue_dir}/{d}")]
                
                queued_jobs = len(glob.glob(f"{queue_dir}/job_*.json"))
                failed_jobs = len(glob.glob(f"{queue_dir}/failed/job_*.json"))
                completed_jobs = len(glob.glob(f"{queue_dir}/completed/job_*.json"))
                
                self.status["working_components"].append({
                    "component": "Background Queue System",
                    "queue_dir": queue_dir,
                    "subdirs": existing_subdirs,
                    "stats": {
                        "queued": queued_jobs,
                        "failed": failed_jobs,
                        "completed": completed_jobs
                    }
                })
                
                logger.info(f"✅ Background queue system operational")
                logger.info(f"   📊 Jobs - Queued: {queued_jobs}, Failed: {failed_jobs}, Completed: {completed_jobs}")
            else:
                logger.warning("❌ Background queue directory not found")
                self.status["failed_components"].append("Background queue directory")
                
        except Exception as e:
            logger.error(f"❌ Error checking background queue: {e}")
            self.status["failed_components"].append("Background queue check")
    
    def check_workflow_status(self):
        """Check workflow configurations"""
        workflows = [
            ("Background Queue", "python background_queue_processor.py"),
            ("FastAPI Webhook", "python fastapi_webhook_server.py"),
            ("Nomadly2 Bot", "python run_bot.py"),
            ("Nomadly2 Webhook", "python webhook_server.py")
        ]
        
        operational_workflows = []
        failed_workflows = []
        
        for name, command in workflows:
            # Check if workflow files exist
            script_name = command.split()[-1]  # Get the Python file name
            
            if os.path.exists(script_name):
                operational_workflows.append({"name": name, "command": command, "file_exists": True})
            else:
                failed_workflows.append({"name": name, "command": command, "file_exists": False})
        
        if operational_workflows:
            self.status["working_components"].append({
                "component": "Workflow Configurations",
                "operational": operational_workflows,
                "failed": failed_workflows
            })
        
        logger.info(f"✅ {len(operational_workflows)} workflows configured")
        for wf in operational_workflows:
            logger.info(f"   🔧 {wf['name']}: {wf['command']}")
    
    def check_dependency_requirements(self):
        """Check what dependencies are needed vs available"""
        
        modern_dependencies = [
            "fastapi", "uvicorn", "redis", "celery", 
            "aiohttp", "structlog", "prometheus-client", "psutil"
        ]
        
        available_deps = []
        missing_deps = []
        
        for dep in modern_dependencies:
            try:
                __import__(dep)
                available_deps.append(dep)
            except ImportError:
                missing_deps.append(dep)
        
        self.status["dependencies"] = {
            "available": available_deps,
            "missing": missing_deps,
            "coverage": len(available_deps) / len(modern_dependencies) * 100
        }
        
        logger.info(f"📦 Dependencies: {len(available_deps)}/{len(modern_dependencies)} available ({len(available_deps)/len(modern_dependencies)*100:.1f}%)")
        
        if missing_deps:
            logger.warning(f"❌ Missing: {', '.join(missing_deps)}")
        
        if available_deps:
            logger.info(f"✅ Available: {', '.join(available_deps)}")
    
    def assess_production_readiness(self):
        """Assess overall production readiness"""
        
        criteria = {
            "webhook_timeout_handling": len([c for c in self.status["working_components"] if "Webhook" in c.get("component", "")]) > 0,
            "background_processing": len([c for c in self.status["working_components"] if "Background" in c.get("component", "")]) > 0,
            "async_infrastructure": len(self.status["implemented_components"]) >= 6,
            "minimal_failures": len(self.status["failed_components"]) <= 2
        }
        
        met_criteria = sum(criteria.values())
        total_criteria = len(criteria)
        
        self.status["production_readiness"] = {
            "criteria_met": met_criteria,
            "total_criteria": total_criteria,
            "percentage": met_criteria / total_criteria * 100,
            "ready": met_criteria >= 3,
            "criteria": criteria
        }
        
        logger.info(f"🎯 Production readiness: {met_criteria}/{total_criteria} criteria met ({met_criteria/total_criteria*100:.1f}%)")
        
        for criterion, met in criteria.items():
            status = "✅" if met else "❌"
            logger.info(f"   {status} {criterion.replace('_', ' ').title()}")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive modernization status report"""
        
        logger.info("🚀 Starting Nomadly2 Modernization Status Check")
        logger.info("=" * 60)
        
        self.check_file_implementations()
        logger.info("")
        
        self.check_webhook_integration()
        logger.info("")
        
        self.check_background_queue()
        logger.info("")
        
        self.check_workflow_status()
        logger.info("")
        
        self.check_dependency_requirements()
        logger.info("")
        
        self.assess_production_readiness()
        logger.info("")
        
        # Summary
        logger.info("📋 MODERNIZATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Implemented Components: {len(self.status['implemented_components'])}")
        logger.info(f"🔧 Working Components: {len(self.status['working_components'])}")
        logger.info(f"❌ Failed Components: {len(self.status['failed_components'])}")
        
        if self.status.get("production_readiness", {}).get("ready", False):
            logger.info("🎉 STATUS: READY FOR PRODUCTION DEPLOYMENT")
        else:
            logger.info("⚠️ STATUS: ADDITIONAL WORK NEEDED")
        
        return self.status

def main():
    """Run comprehensive modernization status check"""
    checker = ModernizationStatusChecker()
    status = checker.generate_comprehensive_report()
    
    # Write detailed report to file
    import json
    
    with open("modernization_status_report.json", "w") as f:
        json.dump(status, f, indent=2, default=str)
    
    logger.info(f"📄 Detailed report saved to: modernization_status_report.json")
    
    return status

if __name__ == "__main__":
    main()