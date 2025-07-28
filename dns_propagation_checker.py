"""
DNS Propagation Checker for Nomadly Bot
Checks DNS propagation across multiple global DNS servers
"""

import asyncio
import socket
import subprocess
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class DNSPropagationChecker:
    def __init__(self):
        # Global DNS servers to check propagation
        self.dns_servers = [
            ("8.8.8.8", "Google"),
            ("1.1.1.1", "Cloudflare"),
            ("208.67.222.222", "OpenDNS"),
            ("9.9.9.9", "Quad9"),
            ("8.26.56.26", "Comodo"),
            ("64.6.64.6", "Verisign"),
            ("77.88.8.8", "Yandex"),
            ("156.154.70.1", "Neustar")
        ]
    
    async def check_nameserver_propagation(self, domain: str) -> Dict[str, any]:
        """Check nameserver propagation across multiple DNS servers using nslookup"""
        results = {}
        total_servers = len(self.dns_servers)
        propagated_count = 0
        nameservers_found = set()
        
        try:
            for dns_server, provider in self.dns_servers:
                try:
                    # Use nslookup command to query NS records
                    process = await asyncio.create_subprocess_exec(
                        'nslookup', '-type=NS', domain, dns_server,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
                    
                    if process.returncode == 0:
                        output = stdout.decode('utf-8', errors='ignore')
                        
                        # Parse nameservers from nslookup output
                        ns_list = []
                        for line in output.split('\n'):
                            if 'nameserver' in line.lower() and '=' in line:
                                ns = line.split('=')[-1].strip().rstrip('.')
                                if ns and not ns.startswith('127.'):
                                    ns_list.append(ns)
                        
                        if ns_list:
                            results[provider] = {
                                "status": "✅ Propagated",
                                "nameservers": ns_list,
                                "response_time": "fast"
                            }
                            propagated_count += 1
                            nameservers_found.update(ns_list)
                        else:
                            results[provider] = {
                                "status": "⚠️ No NS records",
                                "nameservers": [],
                                "response_time": "N/A"
                            }
                    else:
                        results[provider] = {
                            "status": "❌ Domain not found",
                            "nameservers": [],
                            "response_time": "N/A"
                        }
                    
                except asyncio.TimeoutError:
                    results[provider] = {
                        "status": "⏱️ Timeout",
                        "nameservers": [],
                        "response_time": "slow"
                    }
                except Exception as e:
                    results[provider] = {
                        "status": f"⚠️ Error: {str(e)[:30]}",
                        "nameservers": [],
                        "response_time": "error"
                    }
                
                # Small delay between checks
                await asyncio.sleep(0.2)
        
        except Exception as e:
            logger.error(f"DNS propagation check failed: {e}")
            return self._create_error_result(domain)
        
        # Calculate propagation percentage
        propagation_percentage = (propagated_count / total_servers) * 100
        
        # Determine overall status
        if propagation_percentage >= 80:
            overall_status = "✅ Fully Propagated"
            status_emoji = "✅"
        elif propagation_percentage >= 50:
            overall_status = "🟡 Partially Propagated"
            status_emoji = "🟡"
        else:
            overall_status = "❌ Not Propagated"
            status_emoji = "❌"
        
        return {
            "domain": domain,
            "overall_status": overall_status,
            "status_emoji": status_emoji,
            "propagation_percentage": round(propagation_percentage, 1),
            "propagated_servers": propagated_count,
            "total_servers": total_servers,
            "nameservers": list(nameservers_found),
            "server_results": results
        }
    
    async def check_dns_record_propagation(self, domain: str, record_type: str = "A") -> Dict[str, any]:
        """Check DNS record propagation for specific record type using nslookup"""
        results = {}
        total_servers = len(self.dns_servers)
        propagated_count = 0
        records_found = set()
        
        try:
            for dns_server, provider in self.dns_servers:
                try:
                    # Use nslookup command to query specific record type
                    process = await asyncio.create_subprocess_exec(
                        'nslookup', '-type=' + record_type, domain, dns_server,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
                    
                    if process.returncode == 0:
                        output = stdout.decode('utf-8', errors='ignore')
                        
                        # Parse records from nslookup output
                        record_values = []
                        for line in output.split('\n'):
                            if record_type.lower() in line.lower() and '=' in line:
                                value = line.split('=')[-1].strip()
                                if value and not value.startswith('127.'):
                                    record_values.append(value)
                        
                        if record_values:
                            results[provider] = {
                                "status": "✅ Found",
                                "records": record_values,
                                "count": len(record_values)
                            }
                            propagated_count += 1
                            records_found.update(record_values)
                        else:
                            results[provider] = {
                                "status": f"⚠️ No {record_type} records",
                                "records": [],
                                "count": 0
                            }
                    else:
                        results[provider] = {
                            "status": "❌ Domain not found",
                            "records": [],
                            "count": 0
                        }
                    
                except asyncio.TimeoutError:
                    results[provider] = {
                        "status": "⏱️ Timeout",
                        "records": [],
                        "count": 0
                    }
                except Exception as e:
                    results[provider] = {
                        "status": f"⚠️ Error: {str(e)[:20]}",
                        "records": [],
                        "count": 0
                    }
                
                await asyncio.sleep(0.2)
        
        except Exception as e:
            logger.error(f"DNS record propagation check failed: {e}")
            return self._create_error_result(domain, record_type)
        
        propagation_percentage = (propagated_count / total_servers) * 100
        
        if propagation_percentage >= 80:
            overall_status = "✅ Fully Propagated"
        elif propagation_percentage >= 50:
            overall_status = "🟡 Partially Propagated"
        else:
            overall_status = "❌ Not Propagated"
        
        return {
            "domain": domain,
            "record_type": record_type,
            "overall_status": overall_status,
            "propagation_percentage": round(propagation_percentage, 1),
            "propagated_servers": propagated_count,
            "total_servers": total_servers,
            "unique_records": list(records_found),
            "server_results": results
        }
    
    def _create_error_result(self, domain: str, record_type: str = "NS") -> Dict[str, any]:
        """Create error result when propagation check fails"""
        return {
            "domain": domain,
            "record_type": record_type,
            "overall_status": "⚠️ Check Failed",
            "propagation_percentage": 0,
            "propagated_servers": 0,
            "total_servers": len(self.dns_servers),
            "unique_records": [],
            "server_results": {},
            "error": True
        }

# Global propagation checker instance
propagation_checker = DNSPropagationChecker()