#!/usr/bin/env python3
"""
Get OpenProvider trustee service pricing via API
Query real-time pricing for different TLD trustee services
"""

import logging
import requests
from apis.production_openprovider import OpenProviderAPI
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_trustee_pricing():
    """Get trustee service pricing from OpenProvider API"""
    
    # TLDs that require trustee services based on our enhanced system
    trustee_tlds = [
        '.ca',   # Canada - requires trustee
        '.au',   # Australia - requires trustee  
        '.br',   # Brazil - may require trustee
        '.fr',   # France - requires EU presence
        '.eu',   # European Union - requires EU residency
        '.de',   # Germany - may require trustee for non-residents
        '.dk',   # Denmark - new 2025 requirements
    ]
    
    logger.info("🔍 Querying OpenProvider for trustee service pricing...")
    
    try:
        openprovider = OpenProviderAPI()
        
        # Method 1: Try to get extension information
        logger.info("\n📋 Method 1: Getting extension information...")
        
        for tld in trustee_tlds:
            try:
                # Try to get extension details
                headers = {
                    "Authorization": f"Bearer {openprovider.token}",
                    "Content-Type": "application/json",
                }
                
                # Query extension information
                url = f"{openprovider.base_url}/v1beta/tlds/{tld.replace('.', '')}"
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ {tld} extension data retrieved")
                    
                    # Look for trustee/local presence information
                    extension_data = data.get('data', {})
                    
                    # Check for trustee service indicators
                    trustee_info = {}
                    if 'requirements' in extension_data:
                        trustee_info['requirements'] = extension_data['requirements']
                    if 'restrictions' in extension_data:
                        trustee_info['restrictions'] = extension_data['restrictions']
                    if 'additional_data' in extension_data:
                        trustee_info['additional_data'] = extension_data['additional_data']
                        
                    if trustee_info:
                        logger.info(f"   {tld} trustee info: {json.dumps(trustee_info, indent=2)}")
                    else:
                        logger.info(f"   {tld} no specific trustee information found")
                        
                else:
                    logger.warning(f"❌ {tld} extension query failed: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"❌ Error querying {tld}: {e}")
        
        # Method 2: Try to get pricing for domain + trustee service
        logger.info("\n💰 Method 2: Testing domain pricing with trustee services...")
        
        test_domains = {
            'testdomain.ca': '.ca',
            'testdomain.au': '.au', 
            'testdomain.fr': '.fr',
            'testdomain.eu': '.eu',
        }
        
        for domain, tld in test_domains.items():
            try:
                # Query domain pricing
                url = f"{openprovider.base_url}/v1beta/domains/check"
                data = {
                    "domains": [
                        {"name": domain}
                    ]
                }
                
                response = requests.post(url, json=data, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    domains_data = result.get('data', {}).get('results', [])
                    
                    if domains_data:
                        domain_data = domains_data[0]
                        logger.info(f"✅ {domain} pricing data:")
                        
                        # Extract pricing information
                        if 'price' in domain_data:
                            price_info = domain_data['price']
                            logger.info(f"   Registration: {price_info.get('reseller', {}).get('register')}")
                            logger.info(f"   Renewal: {price_info.get('reseller', {}).get('renew')}")
                            logger.info(f"   Transfer: {price_info.get('reseller', {}).get('transfer')}")
                        
                        # Look for additional services
                        if 'additional_services' in domain_data:
                            services = domain_data['additional_services']
                            logger.info(f"   Additional services: {json.dumps(services, indent=2)}")
                        
                        # Look for requirements
                        if 'requirements' in domain_data:
                            requirements = domain_data['requirements']
                            logger.info(f"   Requirements: {json.dumps(requirements, indent=2)}")
                            
                else:
                    logger.warning(f"❌ {domain} pricing query failed: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"❌ Error querying {domain} pricing: {e}")
        
        # Method 3: Check if there's a dedicated trustee services endpoint
        logger.info("\n🏢 Method 3: Looking for trustee service endpoints...")
        
        trustee_endpoints = [
            "/v1beta/products",
            "/v1beta/services", 
            "/v1beta/additional-products",
            "/v1beta/trustee-services"
        ]
        
        for endpoint in trustee_endpoints:
            try:
                url = f"{openprovider.base_url}{endpoint}"
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ {endpoint} endpoint found")
                    logger.info(f"   Response: {json.dumps(data, indent=2)[:500]}...")
                else:
                    logger.info(f"❌ {endpoint} not available: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"❌ Error checking {endpoint}: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to query trustee pricing: {e}")
        return False

if __name__ == "__main__":
    success = get_trustee_pricing()
    
    print("\n" + "="*60)
    if success:
        print("✅ TRUSTEE PRICING QUERY COMPLETED")
        print("Check logs above for detailed pricing information")
    else:
        print("❌ TRUSTEE PRICING QUERY FAILED")
    print("="*60)