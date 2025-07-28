#!/usr/bin/env python3
"""
Comprehensive OpenProvider Trustee Service Pricing Analysis
Test actual domain registration with trustee services to get real costs
"""

import logging
import requests
import json
from apis.production_openprovider import OpenProviderAPI
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_trustee_pricing():
    """Comprehensive analysis of trustee service pricing"""
    
    logger.info("🔍 COMPREHENSIVE OPENPROVIDER TRUSTEE PRICING ANALYSIS")
    logger.info("=" * 70)
    
    # Test domains for different TLD categories
    test_scenarios = {
        # Free trustee services (should be included)
        'free_trustee': {
            'domains': ['testprice123.com.br', 'testprice456.hu', 'testprice789.jp'],
            'expected_cost': 'FREE (included in domain price)'
        },
        
        # Paid trustee services (additional cost)
        'paid_trustee': {
            'domains': ['testprice123.fr', 'testprice456.eu', 'testprice789.ca'],
            'expected_cost': 'PAID (additional fee required)'
        },
        
        # No trustee available (blocked by our system)
        'blocked': {
            'domains': ['testprice123.it'],
            'expected_cost': 'BLOCKED (impossible without EEA residency)'
        }
    }
    
    results = {}
    
    try:
        openprovider = OpenProviderAPI()
        
        headers = {
            "Authorization": f"Bearer {openprovider.token}",
            "Content-Type": "application/json",
        }
        
        logger.info("🧪 Testing domain pricing scenarios...")
        
        for scenario_name, scenario in test_scenarios.items():
            logger.info(f"\n📋 Testing {scenario_name.upper()} scenario:")
            logger.info(f"   Expected: {scenario['expected_cost']}")
            
            scenario_results = []
            
            for test_domain in scenario['domains']:
                logger.info(f"\n🔍 Testing domain: {test_domain}")
                
                try:
                    # Method 1: Domain Check API to get pricing
                    url = f"{openprovider.base_url}/v1beta/domains/check"
                    data = {
                        "domains": [{"name": test_domain}],
                        "with_price": True
                    }
                    
                    response = requests.post(url, json=data, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if 'data' in result and 'results' in result['data']:
                            domain_results = result['data']['results']
                            
                            if domain_results:
                                domain_data = domain_results[0]
                                
                                # Extract pricing information
                                pricing_info = {
                                    'domain': test_domain,
                                    'status': domain_data.get('status', 'unknown'),
                                    'is_premium': domain_data.get('is_premium', False),
                                    'base_price': None,
                                    'additional_services': [],
                                    'trustee_cost': 'Unknown'
                                }
                                
                                # Get base pricing
                                if 'price' in domain_data:
                                    price_data = domain_data['price']
                                    if 'reseller' in price_data and 'register' in price_data['reseller']:
                                        pricing_info['base_price'] = price_data['reseller']['register']
                                
                                # Look for additional services or trustee indicators
                                if 'additional_data' in domain_data:
                                    additional_data = domain_data['additional_data']
                                    logger.info(f"   Additional data found: {json.dumps(additional_data, indent=2)}")
                                
                                # Check for premium pricing (might indicate trustee costs)
                                if 'premium' in domain_data:
                                    premium_data = domain_data['premium']
                                    if 'price' in premium_data:
                                        pricing_info['premium_price'] = premium_data['price']
                                
                                scenario_results.append(pricing_info)
                                
                                logger.info(f"   ✅ Base price: ${pricing_info['base_price']}")
                                logger.info(f"   ✅ Status: {pricing_info['status']}")
                                logger.info(f"   ✅ Premium: {pricing_info['is_premium']}")
                                
                            else:
                                logger.warning(f"   ❌ No results for {test_domain}")
                                
                    else:
                        logger.warning(f"   ❌ API error for {test_domain}: {response.status_code}")
                        logger.warning(f"   Response: {response.text}")
                        
                except Exception as e:
                    logger.error(f"   ❌ Error testing {test_domain}: {e}")
                    
            results[scenario_name] = scenario_results
        
        # Method 2: Try to get specific TLD information
        logger.info(f"\n🏢 Getting TLD-specific trustee information...")
        
        trustee_tlds = ['fr', 'eu', 'ca', 'au', 'de', 'br']
        
        for tld in trustee_tlds:
            try:
                url = f"{openprovider.base_url}/v1beta/tlds/{tld}"
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    tld_data = response.json()
                    
                    if 'data' in tld_data:
                        tld_info = tld_data['data']
                        
                        logger.info(f"\n📋 .{tld} TLD Information:")
                        
                        # Check for trustee/local presence requirements
                        if 'requirements' in tld_info:
                            requirements = tld_info['requirements']
                            logger.info(f"   Requirements: {json.dumps(requirements, indent=2)}")
                        
                        if 'additional_data' in tld_info:
                            additional_data = tld_info['additional_data']
                            logger.info(f"   Additional data: {json.dumps(additional_data, indent=2)}")
                        
                        # Look for pricing-related information
                        if 'price' in tld_info:
                            price_info = tld_info['price']
                            logger.info(f"   Pricing info: {json.dumps(price_info, indent=2)}")
                        
                        # Check for service information
                        if 'services' in tld_info:
                            services = tld_info['services']
                            logger.info(f"   Services: {json.dumps(services, indent=2)}")
                            
                else:
                    logger.warning(f"   ❌ Could not get .{tld} TLD info: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"   ❌ Error getting .{tld} TLD info: {e}")
        
        # Generate summary report
        logger.info(f"\n" + "=" * 70)
        logger.info("📊 TRUSTEE PRICING ANALYSIS SUMMARY")
        logger.info("=" * 70)
        
        for scenario_name, scenario_results in results.items():
            logger.info(f"\n{scenario_name.upper()} SCENARIO:")
            
            if scenario_results:
                for result in scenario_results:
                    domain = result['domain']
                    base_price = result['base_price']
                    status = result['status']
                    
                    logger.info(f"  • {domain}: ${base_price} ({status})")
            else:
                logger.info("  • No results obtained")
        
        # Generate invoice recommendations
        logger.info(f"\n💰 INVOICE CALCULATION RECOMMENDATIONS:")
        logger.info("=" * 40)
        logger.info("1. FREE TRUSTEE TLDs (.com.br, .hu, .jp, .kr, .sg):")
        logger.info("   - No additional cost to customer")
        logger.info("   - Include in standard 3.3x markup")
        logger.info("")
        logger.info("2. PAID TRUSTEE TLDs (.fr, .eu, .ca, .au):")
        logger.info("   - Estimated €10-25 additional cost per year")
        logger.info("   - Options:")
        logger.info("     a) Absorb cost in 3.3x markup")
        logger.info("     b) Add separate line item to invoice")
        logger.info("     c) Higher markup for these TLDs")
        logger.info("")
        logger.info("3. BLOCKED TLDs (.it):")
        logger.info("   - Cannot register - system blocks automatically")
        logger.info("   - No trustee service available")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return None

def generate_invoice_helper():
    """Generate helper for customer invoice calculations"""
    
    logger.info(f"\n🧮 INVOICE CALCULATION HELPER")
    logger.info("=" * 40)
    
    # Trustee service cost estimates based on research
    trustee_costs = {
        # Free trustee services
        '.com.br': {'cost': 0, 'included': True, 'description': 'Free local presence'},
        '.hu': {'cost': 0, 'included': True, 'description': 'Free local presence'},
        '.jp': {'cost': 0, 'included': True, 'description': 'Free local presence'}, 
        '.kr': {'cost': 0, 'included': True, 'description': 'Free local presence'},
        '.sg': {'cost': 0, 'included': True, 'description': 'Free local presence'},
        
        # Paid trustee services (estimates)
        '.fr': {'cost': 15, 'included': False, 'description': 'EU local presence'},
        '.eu': {'cost': 15, 'included': False, 'description': 'EU local presence'},
        '.ca': {'cost': 20, 'included': False, 'description': 'Canadian local presence'},
        '.au': {'cost': 25, 'included': False, 'description': 'Australian local presence'},
        '.de': {'cost': 10, 'included': False, 'description': 'German trustee (optional)'},
        
        # Blocked TLDs
        '.it': {'cost': 'N/A', 'included': False, 'description': 'Registration blocked - requires EEA residency + fiscal code'},
    }
    
    logger.info("TLD TRUSTEE SERVICE COSTS (USD estimates):")
    logger.info("-" * 50)
    
    for tld, info in trustee_costs.items():
        if info['included']:
            logger.info(f"{tld:10} | FREE      | {info['description']}")
        elif info['cost'] == 'N/A':
            logger.info(f"{tld:10} | BLOCKED   | {info['description']}")
        else:
            logger.info(f"{tld:10} | ${info['cost']:3}       | {info['description']}")
    
    logger.info("\nINVOICE CALCULATION FORMULA:")
    logger.info("Base Domain Price * 3.3x + Trustee Cost (if applicable)")
    logger.info("\nExample calculations:")
    logger.info("• .com domain: $12 * 3.3 = $39.60 (no trustee)")
    logger.info("• .fr domain: $15 * 3.3 + $15 = $64.50 (with trustee)")
    logger.info("• .com.br domain: $18 * 3.3 = $59.40 (free trustee)")

if __name__ == "__main__":
    # Run comprehensive analysis
    results = analyze_trustee_pricing()
    
    # Generate invoice helper
    generate_invoice_helper()
    
    print("\n" + "="*70)
    if results:
        print("✅ TRUSTEE PRICING ANALYSIS COMPLETED")
        print("Check logs above for detailed cost information")
    else:
        print("❌ TRUSTEE PRICING ANALYSIS FAILED")
    print("="*70)