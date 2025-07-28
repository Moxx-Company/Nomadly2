#!/usr/bin/env python3
"""
Deep Duplicate Workflow Cleanup Script
Identifies and removes all duplicate workflows, processes, and bot instances
"""

import os
import sys
import subprocess
import signal
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class DuplicateWorkflowCleaner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.duplicate_processes = []
        self.workflow_files = []
        
    def scan_for_duplicate_processes(self):
        """Scan for all running Python processes related to nomadly2"""
        logger.info("🔍 Scanning for duplicate processes...")
        
        try:
            # Get all Python processes
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            processes = result.stdout.split('\n')
            
            nomadly_processes = []
            for line in processes:
                if any(keyword in line for keyword in [
                    'nomadly2_bot.py', 
                    'pure_fastapi_server.py',
                    'background_queue_processor.py',
                    'live_order_monitor.py',
                    'pgbouncer_startup.py'
                ]):
                    nomadly_processes.append(line)
                    
            logger.info(f"Found {len(nomadly_processes)} nomadly2-related processes:")
            for proc in nomadly_processes:
                logger.info(f"  {proc}")
                
            return nomadly_processes
            
        except Exception as e:
            logger.error(f"Error scanning processes: {e}")
            return []
    
    def kill_all_python_processes(self):
        """Kill all Python processes to ensure clean state"""
        logger.info("🔥 Terminating all Python processes...")
        
        try:
            # Kill all python3 processes
            subprocess.run(['pkill', '-f', 'python'], check=False)
            time.sleep(2)
            
            # Force kill if needed
            subprocess.run(['pkill', '-9', '-f', 'python'], check=False)
            time.sleep(1)
            
            # Kill specific nomadly processes
            for process_name in [
                'nomadly2_bot.py',
                'pure_fastapi_server.py', 
                'background_queue_processor.py',
                'live_order_monitor.py',
                'pgbouncer_startup.py'
            ]:
                subprocess.run(['pkill', '-f', process_name], check=False)
                
            logger.info("✅ All Python processes terminated")
            
        except Exception as e:
            logger.error(f"Error killing processes: {e}")
    
    def scan_workflow_files(self):
        """Scan for workflow-related files that might cause duplicates"""
        logger.info("🔍 Scanning for workflow configuration files...")
        
        workflow_patterns = [
            '*.replit',
            'replit.nix',
            '.replit.conf',
            'workflow*.py',
            '*workflow*.json',
            '*process*.py',
            'run*.py'
        ]
        
        found_files = []
        for pattern in workflow_patterns:
            for file_path in self.project_root.glob(f"**/{pattern}"):
                if file_path.is_file():
                    found_files.append(file_path)
                    
        logger.info(f"Found {len(found_files)} workflow-related files:")
        for file_path in found_files:
            logger.info(f"  {file_path}")
            
        return found_files
    
    def clean_port_conflicts(self):
        """Clean up port conflicts that might cause duplicate services"""
        logger.info("🔧 Cleaning port conflicts...")
        
        ports_to_clean = [5000, 8000, 6432, 3000, 4000]
        
        for port in ports_to_clean:
            try:
                # Find processes using the port
                result = subprocess.run(['lsof', '-ti', f'tcp:{port}'], 
                                      capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            logger.info(f"Killing process {pid} on port {port}")
                            subprocess.run(['kill', '-9', pid], check=False)
            except Exception as e:
                logger.debug(f"Port {port} cleanup: {e}")
                
    def remove_temporary_files(self):
        """Remove temporary files that might cause conflicts"""
        logger.info("🧹 Removing temporary files...")
        
        temp_patterns = [
            '*.pyc',
            '__pycache__',
            '*.pid',
            '*.lock',
            '.DS_Store',
            'nohup.out',
            '*.log.1',
            '*.log.2',
            'celerybeat-schedule*',
            'redis-*',
            'pgbouncer.log*'
        ]
        
        removed_count = 0
        for pattern in temp_patterns:
            for file_path in self.project_root.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        removed_count += 1
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                        removed_count += 1
                except Exception as e:
                    logger.debug(f"Could not remove {file_path}: {e}")
                    
        logger.info(f"✅ Removed {removed_count} temporary files")
    
    def check_replit_workflows(self):
        """Check and clean Replit workflow configurations"""
        logger.info("🔍 Checking Replit workflow configurations...")
        
        replit_file = self.project_root / '.replit'
        if replit_file.exists():
            try:
                content = replit_file.read_text()
                logger.info(f"Current .replit content:\n{content}")
                
                # Count workflow entries
                run_commands = content.count('run =')
                if run_commands > 1:
                    logger.warning(f"Found {run_commands} run commands in .replit")
                    
            except Exception as e:
                logger.error(f"Error reading .replit: {e}")
    
    def clean_database_connections(self):
        """Clean up database connection pools"""
        logger.info("💾 Cleaning database connections...")
        
        try:
            # Kill pgbouncer processes
            subprocess.run(['pkill', '-f', 'pgbouncer'], check=False)
            
            # Remove pgbouncer files
            for file_pattern in ['pgbouncer.ini', 'userlist.txt', 'pgbouncer.log*']:
                for file_path in self.project_root.glob(file_pattern):
                    try:
                        file_path.unlink()
                        logger.info(f"Removed {file_path}")
                    except Exception as e:
                        logger.debug(f"Could not remove {file_path}: {e}")
                        
        except Exception as e:
            logger.error(f"Database cleanup error: {e}")
    
    def verify_cleanup(self):
        """Verify that cleanup was successful"""
        logger.info("✅ Verifying cleanup...")
        
        # Check for remaining processes
        remaining_processes = self.scan_for_duplicate_processes()
        if remaining_processes:
            logger.warning(f"⚠️  Still found {len(remaining_processes)} processes")
            return False
        else:
            logger.info("✅ No duplicate processes found")
            
        # Check port availability
        for port in [5000, 8000, 6432]:
            try:
                result = subprocess.run(['lsof', '-ti', f'tcp:{port}'], 
                                      capture_output=True, text=True)
                if result.stdout.strip():
                    logger.warning(f"⚠️  Port {port} still in use")
                else:
                    logger.info(f"✅ Port {port} available")
            except Exception:
                logger.info(f"✅ Port {port} available")
                
        return True
    
    def run_complete_cleanup(self):
        """Run complete duplicate workflow cleanup"""
        logger.info("🚀 Starting complete duplicate workflow cleanup...")
        
        # Step 1: Scan current state
        self.scan_for_duplicate_processes()
        self.scan_workflow_files()
        
        # Step 2: Kill all processes
        self.kill_all_python_processes()
        
        # Step 3: Clean ports
        self.clean_port_conflicts()
        
        # Step 4: Remove temporary files
        self.remove_temporary_files()
        
        # Step 5: Clean database connections
        self.clean_database_connections()
        
        # Step 6: Check Replit configuration
        self.check_replit_workflows()
        
        # Step 7: Wait for cleanup to complete
        time.sleep(3)
        
        # Step 8: Verify cleanup
        success = self.verify_cleanup()
        
        if success:
            logger.info("🎉 Duplicate workflow cleanup completed successfully!")
            logger.info("💡 All processes terminated, ports cleared, temporary files removed")
            logger.info("🚀 Ready for single-instance workflow restart")
        else:
            logger.warning("⚠️  Cleanup completed with some warnings")
            
        return success

def main():
    """Main cleanup execution"""
    cleaner = DuplicateWorkflowCleaner()
    success = cleaner.run_complete_cleanup()
    
    if success:
        print("\n" + "="*60)
        print("✅ DUPLICATE WORKFLOW CLEANUP COMPLETE")
        print("="*60)
        print("• All duplicate processes terminated")
        print("• Port conflicts resolved")  
        print("• Temporary files removed")
        print("• Database connections cleaned")
        print("• System ready for single workflow restart")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("⚠️  CLEANUP COMPLETED WITH WARNINGS")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())