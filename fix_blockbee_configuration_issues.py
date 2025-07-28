#!/usr/bin/env python3
"""
FIX BLOCKBEE CONFIGURATION ISSUES
Identifies cryptocurrencies that have configuration issues and provides appropriate handling
"""

import logging
import os
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_blockbee_cryptocurrencies():
    """Test all cryptocurrencies to identify configuration issues"""
    
    logger.info("🔍 TESTING BLOCKBEE CRYPTOCURRENCY CONFIGURATION")
    
    # Get API key
    api_key = os.environ.get('BLOCKBEE_API_KEY')
    if not api_key:
        logger.error("❌ BLOCKBEE_API_KEY not found in environment")
        return {}
    
    # Cryptocurrency mapping used in our system
    crypto_mapping = {
        "btc": "btc",
        "eth": "eth", 
        "ltc": "ltc",
        "usdt": "usdt_erc20",
        "doge": "doge",
        "trx": "trx",
        "bnb": "bnb_bsc",       # BNB -> bnb_bsc
        "bch": "bch",
        "dash": "dash",
        "xmr": "monero",        # XMR -> monero
        "matic": "polygon",     # MATIC -> polygon
    }
    
    test_results = {}
    
    for crypto, api_crypto in crypto_mapping.items():
        logger.info(f"Testing {crypto.upper()} (API: {api_crypto})")
        
        try:
            url = f"https://api.blockbee.io/{api_crypto}/create/"
            params = {
                "apikey": api_key,
                "callback": "https://test.example.com"
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if response.status_code == 200 and result.get("status") == "success":
                test_results[crypto] = {
                    "status": "✅ WORKING",
                    "api_crypto": api_crypto,
                    "address": result.get("address_in", "Unknown")[:20] + "..."
                }
                logger.info(f"   ✅ {crypto.upper()}: Working")
                
            elif result.get("status") == "error":
                error_msg = result.get("error", "Unknown error")
                test_results[crypto] = {
                    "status": "❌ CONFIGURATION_ISSUE",
                    "api_crypto": api_crypto,
                    "error": error_msg
                }
                logger.error(f"   ❌ {crypto.upper()}: {error_msg}")
                
            else:
                test_results[crypto] = {
                    "status": "⚠️ OTHER_ISSUE", 
                    "api_crypto": api_crypto,
                    "response": result
                }
                logger.warning(f"   ⚠️ {crypto.upper()}: Unexpected response")
                
        except Exception as e:
            test_results[crypto] = {
                "status": "❌ NETWORK_ERROR",
                "api_crypto": api_crypto,
                "error": str(e)
            }
            logger.error(f"   ❌ {crypto.upper()}: {e}")
    
    return test_results

def create_cryptocurrency_availability_update(test_results):
    """Update payment service with actual cryptocurrency availability"""
    
    logger.info("🔧 UPDATING CRYPTOCURRENCY AVAILABILITY")
    
    # Identify working cryptocurrencies
    working_cryptos = []
    broken_cryptos = []
    
    for crypto, result in test_results.items():
        if result["status"] == "✅ WORKING":
            working_cryptos.append(crypto)
        else:
            broken_cryptos.append(crypto)
    
    logger.info(f"✅ Working cryptocurrencies: {', '.join(working_cryptos).upper()}")
    logger.info(f"❌ Configuration issues: {', '.join(broken_cryptos).upper()}")
    
    # Create updated payment service configuration
    try:
        with open('payment_service.py', 'r') as f:
            content = f.read()
        
        # Generate configuration update
        config_update = f'''
# BLOCKBEE CRYPTOCURRENCY AVAILABILITY STATUS (Updated: 2025-07-22)
# Working: {', '.join(working_cryptos).upper()}
# Configuration Issues: {', '.join(broken_cryptos).upper()}

    def get_available_cryptocurrencies(self):
        """Get list of actually working cryptocurrencies"""
        available_cryptos = {{}}
        
        # Working cryptocurrencies (confirmed with BlockBee API)
        working_cryptos = {working_cryptos}
        
        for crypto in working_cryptos:
            if crypto in self.supported_cryptos:
                available_cryptos[crypto] = self.supported_cryptos[crypto]
        
        return available_cryptos
    
    def is_cryptocurrency_available(self, crypto):
        """Check if cryptocurrency is actually available"""
        working_cryptos = {working_cryptos}
        return crypto.lower() in working_cryptos
'''
        
        # Find where to insert the update
        if "def get_available_cryptocurrencies" not in content:
            # Insert after the __init__ method
            init_end = content.find("def __init__", content.find("def __init__") + 1)
            if init_end == -1:
                # Find end of class
                insert_pos = content.rfind("}")
            else:
                insert_pos = content.find("\n\n", init_end)
            
            if insert_pos != -1:
                updated_content = content[:insert_pos] + config_update + content[insert_pos:]
                
                with open('payment_service.py', 'w') as f:
                    f.write(updated_content)
                
                logger.info("✅ Payment service updated with cryptocurrency availability")
            else:
                logger.error("❌ Could not find insertion point in payment_service.py")
        else:
            logger.info("ℹ️ Cryptocurrency availability methods already exist")
            
    except Exception as e:
        logger.error(f"❌ Error updating payment service: {e}")

def create_user_friendly_error_handling():
    """Create better error messages for configuration issues"""
    
    logger.info("📝 CREATING USER-FRIENDLY ERROR HANDLING")
    
    error_handling_code = '''
def get_cryptocurrency_error_message(crypto, error_type):
    """Get user-friendly error message for cryptocurrency issues"""
    
    crypto_names = {
        "btc": "Bitcoin",
        "eth": "Ethereum", 
        "ltc": "Litecoin",
        "usdt": "Tether",
        "doge": "Dogecoin",
        "trx": "TRON",
        "bnb": "Binance Coin",
        "bch": "Bitcoin Cash",
        "dash": "Dash",
        "xmr": "Monero",
        "matic": "Polygon"
    }
    
    crypto_name = crypto_names.get(crypto, crypto.upper())
    
    if error_type == "Address not set on admin panel and not sent":
        return f"""❌ {crypto_name} Temporarily Unavailable
        
{crypto_name} payments require additional configuration on our payment provider.

**Available alternatives:**
• Bitcoin Cash (BCH) - ✅ Working
• Ethereum (ETH) - Check status  
• Bitcoin (BTC) - Check status

Would you like to try a different cryptocurrency or use balance payment?"""
    
    elif error_type == "Unknown error" or error_type == "{}":
        return f"""❌ {crypto_name} Service Unavailable

Our payment provider is experiencing issues with {crypto_name}.

**Please try:**
1. Different cryptocurrency
2. Balance payment 
3. Contact support if issue persists

We apologize for the inconvenience."""
    
    else:
        return f"""❌ {crypto_name} Payment Issue
        
Technical error: {error_type}

Please try a different payment method or contact support."""
'''
    
    # Save error handling utilities
    with open('cryptocurrency_error_handler.py', 'w') as f:
        f.write(error_handling_code)
    
    logger.info("✅ Created cryptocurrency_error_handler.py")

def main():
    """Main testing and fixing function"""
    
    logger.info("🚀 STARTING BLOCKBEE CONFIGURATION DIAGNOSIS AND FIX")
    
    # Test all cryptocurrencies
    test_results = test_blockbee_cryptocurrencies()
    
    # Generate summary report
    logger.info("\n📊 BLOCKBEE CRYPTOCURRENCY TEST SUMMARY")
    logger.info("=" * 50)
    
    working = []
    issues = []
    
    for crypto, result in test_results.items():
        if result["status"] == "✅ WORKING":
            working.append(crypto.upper())
        else:
            issues.append(f"{crypto.upper()} ({result.get('error', 'Unknown issue')})")
    
    logger.info(f"✅ Working ({len(working)}): {', '.join(working)}")
    logger.info(f"❌ Issues ({len(issues)}): {', '.join(issues)}")
    
    # Create fixes
    create_cryptocurrency_availability_update(test_results)
    create_user_friendly_error_handling()
    
    # Recommendations
    logger.info("\n🎯 RECOMMENDATIONS:")
    if len(working) >= 5:
        logger.info(f"✅ {len(working)} cryptocurrencies are working - system is functional")
    else:
        logger.info(f"⚠️ Only {len(working)} cryptocurrencies working - may need provider configuration")
    
    logger.info("\n💡 IMMEDIATE FIXES NEEDED:")
    for crypto, result in test_results.items():
        if "Address not set on admin panel" in result.get("error", ""):
            logger.info(f"• {crypto.upper()}: Configure receiving address in BlockBee admin panel")
    
    return test_results

if __name__ == "__main__":
    results = main()
    
    # Create final status report
    with open('blockbee_configuration_report.json', 'w') as f:
        json.dump({
            'timestamp': '2025-07-22T13:31:30Z',
            'total_tested': len(results),
            'working_count': len([r for r in results.values() if r["status"] == "✅ WORKING"]),
            'issue_count': len([r for r in results.values() if r["status"] != "✅ WORKING"]),
            'detailed_results': results
        }, f, indent=2)