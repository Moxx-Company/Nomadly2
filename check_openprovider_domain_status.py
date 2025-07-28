#!/usr/bin/env python3
"""
Check OpenProvider Domain Status - Verify actual domain ownership
"""

import logging
import requests
import os
from apis.production_openprovider import OpenProviderAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_domain_status():
    """Check the actual status of customer domains in OpenProvider"""
    logger.info("🔍 CHECKING OPENPROVIDER DOMAIN STATUS")
    logger.info("=" * 60)
    
    try:
        api = OpenProviderAPI()
        
        # Test domains
        domains_to_check = [
            ("checktat-atoocol.info", "27820900"),
            ("checktat-attoof.info", "27820901"), 
            ("checktat-atooc.info", "27820902")
        ]
        
        logger.info("📊 DOMAIN OWNERSHIP VERIFICATION")
        logger.info("-" * 50)
        
        # First, let's try to authenticate and get our account domains
        try:
            token = api._authenticate()
            if token:
                logger.info("✅ OpenProvider authentication successful")
                api.token = token
                
                # Try to get domain list from our account
                url = f"{api.base_url}/v1beta/domains"
                headers = api._get_headers()
                
                response = requests.get(url, headers=headers, timeout=30)
                logger.info(f"Domain list response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 0 and 'data' in result:
                        domains = result['data'].get('results', [])
                        logger.info(f"Found {len(domains)} domains in our OpenProvider account:")
                        
                        checktat_domains = []
                        for domain in domains:
                            domain_name = domain.get('domain', {}).get('name')
                            domain_id = domain.get('id')
                            if domain_name and 'checktat' in domain_name:
                                checktat_domains.append((domain_name, domain_id))
                                logger.info(f"  ✅ {domain_name} - ID: {domain_id}")
                        
                        if not checktat_domains:
                            logger.info("  ❌ No checktat domains found in our account")
                            logger.info("  This explains the 'not in your account' error!")
                        
                    else:
                        logger.error(f"API error: {result.get('desc', 'Unknown error')}")
                else:
                    logger.error(f"Failed to get domain list: {response.status_code} - {response.text}")
            else:
                logger.error("❌ OpenProvider authentication failed")
                
        except Exception as auth_error:
            logger.error(f"❌ Authentication/API error: {auth_error}")
        
        # Now check individual domains
        logger.info("\n🔍 INDIVIDUAL DOMAIN CHECKS")
        logger.info("-" * 50)
        
        for domain_name, expected_id in domains_to_check:
            logger.info(f"Checking {domain_name} (expected ID: {expected_id})")
            
            try:
                # Try to get domain details
                url = f"{api.base_url}/v1beta/domains/{expected_id}"
                headers = api._get_headers()
                
                response = requests.get(url, headers=headers, timeout=30)
                logger.info(f"  Response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 0:
                        logger.info(f"  ✅ Domain found in our account")
                    else:
                        logger.info(f"  ❌ API error: {result.get('desc')}")
                elif response.status_code == 404:
                    logger.info(f"  ❌ Domain ID {expected_id} not found")
                elif response.status_code == 403:
                    logger.info(f"  ❌ Access denied - domain not in our account")
                else:
                    logger.info(f"  ❌ HTTP {response.status_code}: {response.text}")
                    
            except Exception as domain_error:
                logger.error(f"  ❌ Error checking {domain_name}: {domain_error}")
        
        logger.info("\n💡 CONCLUSION")
        logger.info("-" * 50)
        logger.info("The OpenProvider error 'domain is not in your account' suggests:")
        logger.info("1. Domain IDs 27820900, 27820901, 27820902 are incorrect")
        logger.info("2. These domains were never actually registered in our OpenProvider account")
        logger.info("3. The 'duplicate domain' errors prevented successful registration")
        logger.info("4. Customer cannot update nameservers because we don't own the domains")
        
    except Exception as e:
        logger.error(f"❌ Check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_domain_status())