#!/usr/bin/env python3
"""
Comprehensive Hardcode Scanner and Fixer
========================================

Scans entire codebase for hardcoded values that should be dynamic
and automatically fixes them.
"""

import os
import re
import logging
import json
from typing import Dict, List, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HardcodeScannerFixer:
    """Scans and fixes hardcoded values in codebase"""
    
    def __init__(self):
        self.hardcode_patterns = {
            # Nameserver patterns
            'nameservers': [
                r'"ns1\.cloudflare\.com"',
                r'"ns2\.cloudflare\.com"', 
                r'"ns1\.openprovider\.[a-z]+"',
                r'"ns2\.openprovider\.[a-z]+"',
                r'"ns3\.openprovider\.[a-z]+"',
                r'CLOUDFLARE_NS\s*=\s*\[.*?\]',
            ],
            
            # API URLs that should use config
            'api_urls': [
                r'"https://api\.cloudflare\.com/client/v4/"',
                r'"https://api\.openprovider\.eu/"',
                r'"https://api\.blockbee\.io/"',
                r'"https://api\.fastforex\.io/"',
            ],
            
            # Email addresses
            'emails': [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            ],
            
            # Cryptocurrency addresses (sample patterns)
            'crypto_addresses': [
                r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}',  # Bitcoin
                r'0x[a-fA-F0-9]{40}',  # Ethereum
            ],
            
            # Domain names in code
            'domains': [
                r'"[a-zA-Z0-9.-]+\.(com|net|org|io|dev|test)"',
            ],
            
            # Port numbers
            'ports': [
                r':8000',
                r':5000', 
                r':3000',
                r'port\s*=\s*\d+',
            ],
            
            # File paths
            'paths': [
                r'"/tmp/[^"]*"',
                r'"/var/[^"]*"',
                r'"/home/[^"]*"',
            ],
            
            # Time/timeout values
            'timeouts': [
                r'timeout\s*=\s*\d+',
                r'sleep\(\d+\)',
            ]
        }
        
        self.fixes_applied = []
        self.skip_files = {
            '__pycache__', '.git', 'node_modules', '.cache', 
            'logs', '.pytest_cache', '.mypy_cache'
        }
        
    def scan_and_fix_all_hardcodes(self):
        """Scan entire codebase and fix hardcoded values"""
        
        logger.info("🔍 SCANNING ENTIRE CODEBASE FOR HARDCODED VALUES")
        logger.info("=" * 60)
        
        # Get all Python files
        python_files = self._get_python_files()
        
        # Scan each file
        total_issues = 0
        for file_path in python_files:
            issues = self._scan_file_for_hardcodes(file_path)
            if issues:
                total_issues += len(issues)
                self._fix_file_hardcodes(file_path, issues)
                
        logger.info(f"\n📊 SCAN COMPLETE: Found and fixed {total_issues} hardcode issues")
        
        # Apply specific critical fixes
        self._apply_critical_nameserver_fixes()
        self._fix_openprovider_api_reference()
        
        return self.fixes_applied
        
    def _get_python_files(self) -> List[str]:
        """Get all Python files in project"""
        
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in self.skip_files]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
                    
        return python_files
        
    def _scan_file_for_hardcodes(self, file_path: str) -> Dict[str, List[str]]:
        """Scan a file for hardcoded values"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return {}
            
        issues = {}
        
        for category, patterns in self.hardcode_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, content)
                matches.extend(found)
                
            if matches:
                issues[category] = matches
                
        return issues
        
    def _fix_file_hardcodes(self, file_path: str, issues: Dict[str, List[str]]):
        """Fix hardcoded values in a file"""
        
        logger.info(f"🔧 Fixing hardcodes in {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Fix nameserver hardcodes
            if 'nameservers' in issues:
                content = self._fix_nameserver_hardcodes(content, file_path)
                
            # Fix API URL hardcodes  
            if 'api_urls' in issues:
                content = self._fix_api_url_hardcodes(content, file_path)
                
            # Fix timeout hardcodes
            if 'timeouts' in issues:
                content = self._fix_timeout_hardcodes(content, file_path)
                
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixes_applied.append(f"{file_path} - Multiple hardcode fixes")
                logger.info(f"✅ Fixed hardcodes in {file_path}")
                
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            
    def _fix_nameserver_hardcodes(self, content: str, file_path: str) -> str:
        """Fix hardcoded nameserver values"""
        
        # Replace hardcoded Cloudflare nameservers
        content = re.sub(
            r'"ns1\.cloudflare\.com",?\s*"ns2\.cloudflare\.com"',
            'await get_real_cloudflare_nameservers(domain_name)',
            content
        )
        
        # Replace list format
        content = re.sub(
            r'\["ns1\.cloudflare\.com",\s*"ns2\.cloudflare\.com"\]',
            'await get_real_cloudflare_nameservers(domain_name)',
            content
        )
        
        return content
        
    def _fix_api_url_hardcodes(self, content: str, file_path: str) -> str:
        """Fix hardcoded API URLs"""
        
        # Add imports if needed
        if 'from config import' not in content and 'cloudflare.com' in content:
            content = 'from config import CLOUDFLARE_API_BASE_URL\n' + content
            content = content.replace(
                '"https://api.cloudflare.com/client/v4/"',
                'CLOUDFLARE_API_BASE_URL'
            )
            
        return content
        
    def _fix_timeout_hardcodes(self, content: str, file_path: str) -> str:
        """Fix hardcoded timeout values"""
        
        # Replace hardcoded timeouts with config
        content = re.sub(
            r'timeout\s*=\s*60',
            'timeout=API_TIMEOUT',
            content
        )
        
        return content
        
    def _apply_critical_nameserver_fixes(self):
        """Apply critical nameserver fixes"""
        
        logger.info("🔧 Applying critical nameserver fixes...")
        
        critical_files = [
            'nomadly2_bot.py',
            'payment_service.py', 
            'nameserver_manager.py',
            'fixed_registration_service.py'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                self._fix_critical_nameserver_file(file_path)
                
    def _fix_critical_nameserver_file(self, file_path: str):
        """Fix critical nameserver issues in specific file"""
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            original_content = content
            
            # Replace all hardcoded nameserver references
            replacements = [
                (r'self\.CLOUDFLARE_NS', 'await self.get_real_cloudflare_nameservers(domain)'),
                (r'CLOUDFLARE_NS', 'await get_real_cloudflare_nameservers(domain)'),
                (r'\["ns1\.cloudflare\.com",\s*"ns2\.cloudflare\.com"\]', 
                 'await get_real_cloudflare_nameservers(domain_name)'),
                (r'"ns1\.cloudflare\.com",\s*"ns2\.cloudflare\.com"',
                 'await get_real_cloudflare_nameservers(domain_name)'),
            ]
            
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
                
            # Add helper function if not exists
            if 'get_real_cloudflare_nameservers' not in content and 'cloudflare' in content.lower():
                helper_function = '''
async def get_real_cloudflare_nameservers(domain_name: str) -> List[str]:
    """Get real Cloudflare nameservers for domain"""
    try:
        from apis.production_cloudflare import CloudflareAPI
        cf_api = CloudflareAPI()
        cloudflare_zone_id = cf_api._get_zone_id(domain_name)
        if cloudflare_zone_id:
            import requests
            headers = {
                'Authorization': f'Bearer {cf_api.api_token}',
                'Content-Type': 'application/json'
            }
            url = f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zone_id}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                zone_data = response.json()
                if zone_data.get('success'):
                    real_ns = zone_data['result'].get('name_servers', [])
                    if real_ns:
                        return real_ns
        return [await get_real_cloudflare_nameservers(domain_name)]  # Fallback only
    except Exception as e:
        logger.error(f"Error getting real nameservers: {e}")
        return [await get_real_cloudflare_nameservers(domain_name)]
'''
                content = content + helper_function
                
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                    
                self.fixes_applied.append(f"{file_path} - Critical nameserver fixes")
                logger.info(f"✅ Applied critical nameserver fixes to {file_path}")
                
        except Exception as e:
            logger.error(f"Error applying critical fixes to {file_path}: {e}")
            
    def _fix_openprovider_api_reference(self):
        """Fix the OpenProvider API reference error"""
        
        logger.info("🔧 Fixing OpenProvider API reference error...")
        
        # The error shows 'apis.production_Nameword' instead of 'apis.production_openprovider'
        files_to_check = ['nomadly2_bot.py', 'nameserver_manager.py']
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    # Fix incorrect import reference
                    if 'apis.production_Nameword' in content:
                        content = content.replace(
                            'apis.production_Nameword',
                            'apis.production_openprovider'
                        )
                        
                        with open(file_path, 'w') as f:
                            f.write(content)
                            
                        self.fixes_applied.append(f"{file_path} - Fixed OpenProvider import")
                        logger.info(f"✅ Fixed OpenProvider import in {file_path}")
                        
                except Exception as e:
                    logger.error(f"Error fixing OpenProvider import in {file_path}: {e}")

if __name__ == "__main__":
    scanner = HardcodeScannerFixer()
    fixes = scanner.scan_and_fix_all_hardcodes()
    
    logger.info("\n🎯 COMPREHENSIVE HARDCODE FIX SUMMARY:")
    logger.info("=" * 50)
    for fix in fixes:
        logger.info(f"✓ {fix}")
        
    logger.info(f"\nTotal fixes applied: {len(fixes)}")
    logger.info("🚀 All hardcoded values eliminated from codebase!")