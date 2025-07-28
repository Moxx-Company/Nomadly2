#!/usr/bin/env python3
"""
Complete OpenProvider Fix - Implement correct contact handle system
Based on official OpenProvider documentation
"""

import logging
import requests
import os
import json
from datetime import datetime
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorrectOpenProviderAPI:
    """Correct OpenProvider API implementation following official docs"""

    def __init__(self):
        self.username = os.getenv("OPENPROVIDER_USERNAME")
        self.password = os.getenv("OPENPROVIDER_PASSWORD")
        self.base_url = "https://api.openprovider.eu"
        self.token = None
        
        if not self.username or not self.password:
            raise Exception("OpenProvider credentials required")
            
        self._authenticate()

    def _authenticate(self):
        """Authenticate with OpenProvider API"""
        try:
            url = f"{self.base_url}/v1beta/auth/login"
            data = {"username": self.username, "password": self.password}
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    self.token = result.get("data", {}).get("token")
                    logger.info("✅ OpenProvider authentication successful")
                    return True
                else:
                    logger.error(f"Auth API error: {result.get('desc')}")
                    return False
            else:
                logger.error(f"Auth HTTP error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def _get_headers(self):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def create_customer_handle(self, user_data: dict) -> str:
        """Create customer handle following OpenProvider docs format"""
        try:
            if not self.token:
                self._authenticate()
                
            url = f"{self.base_url}/v1beta/customers"
            
            # Prepare data following OpenProvider documentation
            customer_data = {
                "name": {
                    "first_name": user_data.get('first_name', 'John'),
                    "last_name": user_data.get('last_name', 'Doe')
                },
                "email": user_data.get('email', 'contact@example.com'),
                "phone": {
                    "country_code": user_data.get('country_code', '+1'),
                    "area_code": user_data.get('area_code', '555'),
                    "subscriber_number": user_data.get('phone', '1234567')
                },
                "address": {
                    "street": user_data.get('street', 'Main Street'),
                    "number": user_data.get('number', '123'),
                    "city": user_data.get('city', 'New York'),
                    "state": user_data.get('state', 'NY'),
                    "zipcode": user_data.get('zipcode', '10001'),
                    "country": user_data.get('country', 'US')
                }
            }
            
            # Add company name if provided
            if user_data.get('company_name'):
                customer_data["company_name"] = user_data['company_name']
            
            response = requests.post(url, json=customer_data, headers=self._get_headers(), timeout=API_TIMEOUT)
            
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('code') == 0:
                    handle = result.get('data', {}).get('handle')
                    logger.info(f"✅ Customer handle created: {handle}")
                    return handle
                else:
                    logger.error(f"Customer creation API error: {result.get('desc')}")
                    return None
            else:
                logger.error(f"Customer creation HTTP error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Customer handle creation error: {e}")
            return None

    def register_domain_with_handle(self, domain_name: str, customer_handle: str, nameservers: list = None) -> dict:
        """Register domain using customer handle following OpenProvider docs"""
        try:
            if not self.token:
                self._authenticate()
                
            # Split domain into name and extension
            domain_parts = domain_name.split('.')
            domain = domain_parts[0]
            extension = '.'.join(domain_parts[1:])
            
            url = f"{self.base_url}/v1beta/domains"
            
            # Prepare registration data following OpenProvider documentation
            registration_data = {
                "domain": {
                    "name": domain,
                    "extension": extension
                },
                "period": 1,  # 1 year
                "owner_handle": customer_handle,
                "admin_handle": customer_handle,
                "tech_handle": customer_handle,
                "billing_handle": customer_handle
            }
            
            # Add nameservers if provided
            if nameservers:
                registration_data["nameservers"] = [{"name": ns} for ns in nameservers]
            else:
                # Use default OpenProvider nameservers
                registration_data["ns_group"] = "dns-openprovider"
            
            response = requests.post(url, json=registration_data, headers=self._get_headers(), timeout=90)
            
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('code') == 0:
                    domain_id = result.get('data', {}).get('id')
                    logger.info(f"✅ Domain registered successfully: {domain_name} (ID: {domain_id})")
                    return {
                        'success': True,
                        'domain_id': domain_id,
                        'handle': customer_handle,
                        'result': result
                    }
                else:
                    error_desc = result.get('desc', 'Unknown error')
                    error_code = result.get('code', 0)
                    logger.error(f"Domain registration API error {error_code}: {error_desc}")
                    return {
                        'success': False,
                        'error_code': error_code,
                        'error_desc': error_desc
                    }
            else:
                logger.error(f"Domain registration HTTP error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Domain registration error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def list_domains(self) -> list:
        """List all domains in the account"""
        try:
            if not self.token:
                self._authenticate()
                
            url = f"{self.base_url}/v1beta/domains"
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    domains = result.get('data', {}).get('results', [])
                    return domains
                else:
                    logger.error(f"Domain list API error: {result.get('desc')}")
                    return []
            else:
                logger.error(f"Domain list HTTP error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Domain list error: {e}")
            return []

async def fix_customer_registrations():
    """Fix customer @folly542 registrations using correct OpenProvider API"""
    logger.info("🔧 FIXING CUSTOMER REGISTRATIONS WITH CORRECT OPENPROVIDER API")
    logger.info("=" * 70)
    
    try:
        # Initialize correct API
        api = CorrectOpenProviderAPI()
        
        # Check what domains we actually have in OpenProvider
        logger.info("🔍 CHECKING ACTUAL DOMAINS IN OPENPROVIDER ACCOUNT")
        logger.info("-" * 50)
        
        domains = api.list_domains()
        logger.info(f"Found {len(domains)} domains in OpenProvider account:")
        
        checktat_domains = []
        for domain in domains:
            domain_name = domain.get('domain', {}).get('name')
            domain_ext = domain.get('domain', {}).get('extension')
            if domain_name and 'checktat' in domain_name:
                full_domain = f"{domain_name}.{domain_ext}"
                domain_id = domain.get('id')
                checktat_domains.append((full_domain, domain_id))
                logger.info(f"  ✅ {full_domain} - ID: {domain_id}")
        
        if not checktat_domains:
            logger.info("  ❌ No checktat domains found in OpenProvider account")
            logger.info("  This confirms domains were never actually registered")
        
        # Customer data for consistent handle creation
        logger.info(f"\n💡 CUSTOMER CONTACT STRATEGY")
        logger.info("-" * 50)
        
        # Get customer info from database
        db_manager = get_db_manager()
        telegram_id = 6896666427  # Customer @folly542
        user = db_manager.get_user_by_telegram_id(telegram_id)
        
        # Create consistent customer data
        customer_data = {
            'first_name': 'John',  # Anonymous contact as per privacy policy
            'last_name': 'Smith',
            'email': user.technical_email if user and user.technical_email else 'contact@privacy.example.com',
            'street': 'Privacy Street',
            'number': '123',
            'city': 'New York',
            'state': 'NY', 
            'zipcode': '10001',
            'country': 'US',
            'country_code': '+1',
            'area_code': '555',
            'phone': '1234567'
        }
        
        logger.info("Customer data prepared for consistent handle creation:")
        logger.info(f"  Name: {customer_data['first_name']} {customer_data['last_name']}")
        logger.info(f"  Email: {customer_data['email']}")
        logger.info(f"  Country: {customer_data['country']}")
        
        # Create customer handle for future registrations
        logger.info(f"\n🔧 CREATING CONSISTENT CUSTOMER HANDLE")
        logger.info("-" * 50)
        
        customer_handle = api.create_customer_handle(customer_data)
        if customer_handle:
            logger.info(f"✅ Customer handle created: {customer_handle}")
            logger.info("This handle should be used for all future domain registrations")
            
            # Update database with consistent handle for customer
            try:
                session = db_manager.get_session()
                from sqlalchemy import text
                
                # Update all customer domains to use consistent handle
                update_query = text("""
                    UPDATE registered_domains 
                    SET openprovider_contact_handle = :handle
                    WHERE telegram_id = :telegram_id
                """)
                
                session.execute(update_query, {
                    'handle': customer_handle,
                    'telegram_id': telegram_id
                })
                session.commit()
                
                logger.info(f"✅ Updated database with consistent handle: {customer_handle}")
                
            except Exception as db_error:
                logger.error(f"Database update error: {db_error}")
            finally:
                session.close()
        
        else:
            logger.error("❌ Failed to create customer handle")
        
        logger.info(f"\n📊 SUMMARY")
        logger.info("-" * 50)
        logger.info(f"OpenProvider domains found: {len(checktat_domains)}")
        logger.info(f"Consistent customer handle: {customer_handle or 'FAILED'}")
        logger.info("Next steps:")
        logger.info("1. Use this customer handle for any re-registration attempts")
        logger.info("2. Update registration service to reuse customer handles")
        logger.info("3. Fix duplicate domain handling to prevent race conditions")
        
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(fix_customer_registrations())