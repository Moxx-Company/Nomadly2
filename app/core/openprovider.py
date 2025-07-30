"""
Production OpenProvider API - Mystery Milestone Compatible
Handles domain registration using the proven working approach
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Tuple, Any
import json
from enhanced_tld_requirements_system import get_enhanced_tld_system

logger = logging.getLogger(__name__)


class OpenProviderAPI:
    """Production OpenProvider API using Mystery milestone approach"""

    def __init__(self):
        """Initialize with credentials validation"""
        self.username = os.getenv("OPENPROVIDER_USERNAME")
        self.password = os.getenv("OPENPROVIDER_PASSWORD")

        if not self.username or not self.password:
            raise Exception(
                "OpenProvider credentials required: OPENPROVIDER_USERNAME and OPENPROVIDER_PASSWORD"
            )

        self.base_url = "https://api.openprovider.eu"
        self.token = None
        self.tld_system = get_enhanced_tld_system()
        self._authenticate()

    def _authenticate(self):
        """Authenticate with OpenProvider - ENHANCED TIMEOUT CONFIGURATION"""
        try:
            url = f"{self.base_url}/v1beta/auth/login"
            data = {"username": self.username, "password": self.password}

            # 🔧 INCREASED TIMEOUT: From 8s to 45s to resolve customer timeouts
            response = requests.post(url, json=data, timeout=45)

            if response.status_code == 200:
                result = response.json()
                self.token = result.get("data", {}).get("token")
                logger.info("OpenProvider authentication successful")
                return True
            else:
                raise Exception(f"Authentication failed: {response.status_code}")

        except Exception as e:
            logger.error(f"OpenProvider authentication error: {e}")
            raise Exception(f"OpenProvider authentication failed: {e}")

    async def _authenticate_openprovider(self):
        """Async authentication method - Missing method fix"""
        try:
            return self._authenticate()
        except Exception as e:
            logger.error(f"Async auth error: {e}")
            return None

    async def _auth_request(self):
        """Async authentication method for compatibility"""
        try:
            return self._authenticate()
        except Exception as e:
            logger.error(f"Async auth error: {e}")
            return None

    def update_nameservers(self, domain: str, nameservers: List[str]) -> bool:
        """Update nameservers for a domain - FIXED IMPLEMENTATION"""
        try:
            logger.info(f"🔧 FIXING: Updating nameservers for {domain}: {nameservers}")

            if not self.token:
                self._authenticate()

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            # Try to get domain ID from database first
            domain_id = None
            try:
                from database import get_db_manager

                db_manager = get_db_manager()
                # Use proper method to get domain
                domain_record = db_manager.get_domain_by_name(domain)
                if domain_record is not None and hasattr(domain_record, 'openprovider_domain_id') and domain_record.openprovider_domain_id is not None:
                    domain_id_str = str(domain_record.openprovider_domain_id)
                    logger.info(f"Found domain ID in database: {domain_id_str}")
                    
                    # Check if this is a special status marker
                    if domain_id_str in ["not_manageable_account_mismatch", "already_registered", "needs_reregistration"]:
                        logger.warning(f"Domain {domain} has special status: {domain_id_str}")
                        logger.warning(f"Cannot update nameservers for domain marked as: {domain_id_str}")
                        return False
                    
                    # Validate that domain_id is numeric
                    try:
                        domain_id = int(domain_id_str)
                    except ValueError:
                        logger.error(f"Invalid domain ID format for {domain}: {domain_id_str}")
                        return False
                        
            except Exception as e:
                logger.warning(f"Could not retrieve domain ID from database: {e}")

            # Must use domain ID for nameserver updates
            if domain_id is None:
                logger.error(f"No valid OpenProvider domain ID found for {domain}")
                return False

            # 🔧 FIX: Use correct OpenProvider API endpoint and structure
            url = f"{self.base_url}/v1beta/domains/{domain_id}"
            
            # Get domain name from database for API requirement
            domain_parts = domain.split('.')
            domain_name = domain_parts[0]
            domain_extension = '.'.join(domain_parts[1:])
            
            # Format according to OpenProvider documentation
            data = {
                "domain": {
                    "name": domain_name,
                    "extension": domain_extension
                },
                "nameServers": [{"name": ns} for ns in nameservers]
            }

            logger.info(
                f"Making OpenProvider API call to update nameservers for {domain}"
            )
            
            # 🔧 ENHANCED TIMEOUT & RETRY: Implement retry logic for customer reliability
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 🔧 INCREASED TIMEOUT: 60s for nameserver updates with 3-retry logic
                    response = requests.put(url, headers=headers, json=data, timeout=60)

                    if response.status_code in [200, 201]:
                        logger.info(f"✅ Successfully updated nameservers for {domain} (attempt {retry_count + 1})")
                        return True
                    elif response.status_code == 401:
                        # Token expired, re-authenticate and retry
                        logger.info(f"🔄 Token expired, re-authenticating for {domain}")
                        self._authenticate()
                        headers = {
                            "Authorization": f"Bearer {self.token}",
                            "Content-Type": "application/json",
                        }
                        retry_count += 1
                        continue
                    else:
                        logger.error(f"❌ OpenProvider API error {response.status_code}: {response.text[:200]}")
                        retry_count += 1
                        
                except requests.exceptions.Timeout as e:
                    retry_count += 1
                    logger.warning(f"⏰ Timeout on attempt {retry_count} for {domain}: {e}")
                    if retry_count >= max_retries:
                        logger.error(f"❌ Max retries reached for {domain} nameserver update")
                        return False
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"⚠️ Error on attempt {retry_count} for {domain}: {e}")
                    if retry_count >= max_retries:
                        logger.error(f"❌ Max retries reached for {domain} due to error: {e}")
                        return False
            
            # If all retries failed
            logger.error(f"❌ All {max_retries} attempts failed for {domain} nameserver update")
            return False

        except Exception as e:
            logger.error(f"Error updating nameservers for {domain}: {e}")
            return False

    def update_domain_nameservers(self, domain_id: int, nameservers: List[str]) -> bool:
        """Update domain nameservers using domain ID - Bot compatibility method"""
        try:
            logger.info(f"🔧 Updating nameservers for domain ID {domain_id}: {nameservers}")

            if not self.token:
                self._authenticate()

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            # 🔧 Use correct OpenProvider API endpoint for domain modification
            url = f"{self.base_url}/v1beta/domains/{domain_id}"
            
            # Format nameservers according to OpenProvider v1beta documentation
            data = {
                "nameServers": [{"name": ns} for ns in nameservers]
            }

            logger.info(f"Making OpenProvider API call: PUT {url}")
            logger.info(f"Data: {data}")
            
            # 🔧 Enhanced timeout for nameserver updates (60s with retry logic)
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = requests.put(url, headers=headers, json=data, timeout=60)

                    if response.status_code == 200:
                        logger.info(f"✅ Nameservers updated successfully for domain ID {domain_id}")
                        return True
                    elif response.status_code == 400:
                        logger.error(f"❌ Bad request (400): {response.text}")
                        return False
                    elif response.status_code == 401:
                        logger.error(f"❌ Authentication failed (401)")
                        # Try to re-authenticate once
                        if retry_count == 0:
                            logger.info("Attempting re-authentication...")
                            self._authenticate()
                            retry_count += 1
                            continue
                        return False
                    else:
                        logger.error(f"❌ OpenProvider API error {response.status_code}: {response.text}")
                        return False
                        
                except requests.Timeout:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"Timeout on attempt {retry_count}, retrying...")
                        continue
                    else:
                        logger.error(f"Failed after {max_retries} timeout attempts")
                        return False
                        
                except Exception as api_error:
                    logger.error(f"API request error: {api_error}")
                    return False

            return False

        except Exception as e:
            logger.error(f"Domain nameserver update error for ID {domain_id}: {e}")
            return False

    def get_domain_info(self, domain_name: str) -> Dict[str, Any]:
        """Get domain information from OpenProvider API"""
        try:
            if not self.token:
                self._authenticate()

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            # Try to get domain by name first
            url = f"{self.base_url}/v1beta/domains"
            params = {"domain_name_pattern": domain_name, "limit": 1}
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                domains = result.get("data", {}).get("results", [])
                
                if domains:
                    domain_data = domains[0]
                    nameservers = []
                    
                    # Extract nameservers from API response
                    ns_data = domain_data.get("name_servers", [])
                    for ns in ns_data:
                        if isinstance(ns, dict) and "name" in ns:
                            nameservers.append(ns["name"])
                        elif isinstance(ns, str):
                            nameservers.append(ns)
                    
                    return {
                        "success": True,
                        "data": {
                            "domain_id": domain_data.get("id"),
                            "domain_name": domain_data.get("domain", {}).get("name"),
                            "nameservers": nameservers,
                            "status": domain_data.get("status"),
                            "expires_at": domain_data.get("expiration_date")
                        }
                    }
                else:
                    return {"success": False, "error": "Domain not found"}
            else:
                logger.error(f"OpenProvider API error {response.status_code}: {response.text}")
                return {"success": False, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting domain info for {domain_name}: {e}")
            return {"success": False, "error": str(e)}

    def get_nameservers_fallback(self, domain: str) -> List[str]:
        """Fallback method - Get current nameservers for a domain (simple version)"""
        try:
            # In production, this would query OpenProvider API
            # For now, return the known Cloudflare nameservers for our domains
            return ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"]
        except Exception as e:
            logger.error(f"Error getting nameservers for {domain}: {e}")
            return []

    def _get_headers(self) -> Dict:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _create_customer_handle(self, technical_email: Optional[str] = None) -> Optional[str]:
        """Create customer handle using official OpenProvider documentation format (XX000001-XX)"""
        try:
            url = f"{self.base_url}/v1beta/customers"

            # Use collected technical email or fallback
            fallback_email = os.getenv("FALLBACK_CONTACT_EMAIL", "cloakhost@tutamail.com")
            email_address = technical_email if technical_email else fallback_email

            logger.info(
                f"🔧 Creating OpenProvider customer with email: {email_address[:5]}*** (Official Documentation Format)"
            )

            # Official OpenProvider v1beta customer creation format per documentation
            data = {
                "company_name": "Privacy Services LLC",
                "name": {
                    "first_name": "John",
                    "last_name": "Privacy",
                    "prefix": "",
                    "initials": "J P"
                },
                "address": {
                    "street": "123 Privacy Street",
                    "number": "1",
                    "zipcode": "89101",
                    "city": "Las Vegas",
                    "state": "NV",
                    "country": "US",
                    "suffix": ""
                },
                "phone": {
                    "country_code": "+1",
                    "area_code": "702",
                    "subscriber_number": "5551234"
                },
                "email": email_address,
                "locale": "en_US",
                "gender": "M"
            }

            # Enhanced timeout for customer creation
            response = requests.post(
                url, json=data, headers=self._get_headers(), timeout=90
            )

            if response.status_code == 200:
                result = response.json()
                handle = result.get("data", {}).get("handle")
                if handle:
                    logger.info(f"✅ Official format customer handle created: {handle}")
                    # Validate it matches actual OpenProvider format: CC######-CC
                    if "-" in handle and len(handle.split("-")) == 2:
                        prefix, suffix = handle.split("-")
                        if (len(prefix) >= 2 and prefix[:2].isalpha() and 
                            len(suffix) == 2 and suffix.isalpha() and
                            any(c.isdigit() for c in prefix)):
                            logger.info(f"✅ Handle format validation passed: {handle} (Country-specific format)")
                        else:
                            logger.warning(f"⚠️ Unexpected handle format: {handle}")
                    else:
                        logger.warning(f"⚠️ Invalid handle format: {handle}")
                    return handle
                else:
                    logger.error(f"❌ No handle returned in response: {result}")
                    return None
            else:
                logger.error(
                    f"❌ Customer creation failed: {response.status_code} {response.text[:500]}"
                )
                return None

        except Exception as e:
            logger.error(f"❌ Customer handle creation error: {e}")
            return None

    def register_domain(
        self,
        domain_name: str,
        tld: str,
        customer_data: Dict,
        nameservers: Optional[List[str]] = None,
        technical_email: Optional[str] = None,
    ) -> Tuple[bool, Optional[int], str]:
        """Register domain using Mystery milestone approach"""
        try:
            url = f"{self.base_url}/v1beta/domains"

            # Create customer handle with technical email
            customer_handle = self._create_customer_handle(technical_email or None)
            if not customer_handle:
                return False, None, "Failed to create customer handle"

            # MINIMAL WORKING FORMAT - only essential parameters
            # Extract domain name without TLD and use TLD correctly
            if '.' in domain_name:
                domain_parts = domain_name.split('.')
                clean_domain_name = domain_parts[0]
                domain_tld = '.'.join(domain_parts[1:])
            else:
                clean_domain_name = domain_name
                domain_tld = tld
            
            data = {
                "domain": {"name": clean_domain_name, "extension": domain_tld},
                "period": 1,
                "owner_handle": customer_handle,
                "admin_handle": customer_handle,
                "tech_handle": customer_handle,
                "billing_handle": customer_handle,
            }

            # Add nameservers OR ns_group (required by OpenProvider API)
            if nameservers:
                data["nameservers"] = [{"name": ns} for ns in nameservers]
            else:
                # Use OpenProvider's DNS service as fallback
                data["ns_group"] = "dns-openprovider"
            
            # Enhanced TLD-specific handling using TLD requirements system
            user_data = {
                "email": technical_email or "contact@nameword.com",
                "company_name": "Privacy Services LLC",
                "vat_number": "",
            }
            
            # Get additional data requirements for this TLD
            additional_data = self.tld_system.prepare_additional_data_for_registration(
                f".{domain_tld}", user_data
            )
            
            # Apply TLD-specific requirements
            if domain_tld == "dk":
                # New 2025 .dk requirements
                additional_data.update({
                    "dk_acceptance": 1  # Mandatory acceptance parameter since 2025
                })
            elif domain_tld == "de":
                # .de domains - DENIC requirements + enhanced TLD system
                additional_data.update({
                    "de_accept_trustee_tac": 1,
                    "de_abuse_contact": technical_email or "abuse@nameword.com"
                })
                if nameservers:
                    ns_list = nameservers[:4]
                    data["nameservers"] = [{"name": ns} for ns in ns_list]
                    
            elif domain_tld in ["ca"]:
                # .ca domains - Canadian Presence Requirements + trustee service
                additional_data.update({
                    "ca_legal_type": "CCO",  # Corporation
                    "ca_trustee_contact": 1  # Use trustee service
                })
                
            elif domain_tld in ["au", "com.au", "net.au"]:
                # .au domains - Australian presence requirements + trustee service
                additional_data.update({
                    "au_registrant_name": "Nameword Holdings",
                    "au_registrant_id_type": "OTHER",
                    "au_trustee_contact": 1
                })
                
            elif domain_tld in ["fr"]:
                # .fr domains - EU residency requirements + trustee service
                additional_data.update({
                    "fr_accept_trustee_tac": 1,
                    "fr_contact_country": "NL"  # Use Netherlands as EU country
                })
                
            elif domain_tld in ["eu"]:
                # .eu domains - EU citizenship/residency + trustee service
                additional_data.update({
                    "eu_accept_trustee_tac": 1,
                    "eu_registrant_citizenship": "NL"
                })
            
            # Add consolidated additional_data to registration
            if additional_data:
                data["additional_data"] = additional_data
                logger.info(f"TLD {domain_tld} additional data applied: {list(additional_data.keys())}")

            logger.info(f"Registering domain with data: {data}")

            # Domain registration needs more time than searches - use 30 second timeout
            response = requests.post(
                url, json=data, headers=self._get_headers(), timeout=30
            )

            logger.info(f"Domain registration response: {response.status_code}")
            logger.info(f"Response body: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    domain_data = result.get("data", {})
                    domain_id = domain_data.get("id")
                    logger.info(
                        f"Domain registered successfully: {domain_name}.{tld} (ID: {domain_id})"
                    )
                    return True, domain_id, "Domain registered successfully"
                else:
                    error_msg = result.get("desc", "Unknown error")
                    logger.error(f"Domain registration API error: {error_msg}")
                    return False, None, error_msg
            else:
                error_text = response.text
                error_msg = f"HTTP {response.status_code}: {error_text}"
                logger.error(f"Domain registration HTTP error: {error_msg}")
                
                # ENHANCED: Handle duplicate domain gracefully - return special indicator instead of exception
                if "duplicate domain" in error_text.lower() or "cannot add duplicate domain" in error_text.lower() or '"code":346' in error_text:
                    logger.info(f"🔄 Duplicate domain detected - returning special indicator for upstream handling")
                    return False, None, f"Duplicate domain: {error_text}"
                    
                return False, None, error_msg

        except Exception as e:
            error_msg = f"Domain registration exception: {e}"
            logger.error(error_msg)
            return False, None, error_msg

    async def register_domain_with_nameservers(
        self,
        domain_name: str,
        tld: str,
        customer_data: Dict,
        nameservers: List[str],
        technical_email: Optional[str] = None,
    ) -> Tuple[bool, Optional[int], str]:
        """Async wrapper for domain registration"""
        return self.register_domain(
            domain_name, tld, customer_data, nameservers, technical_email
        )

    def get_domain_details(self, domain: str) -> Optional[Dict]:
        """Get full domain details from OpenProvider"""
        try:
            url = f"{self.base_url}/v1beta/domains/{domain}"

            # 🔧 ENHANCED TIMEOUT: Domain details query increased to 30s
            response = requests.get(url, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    domain_data = result.get("data", {})
                    logger.info(f"Retrieved domain details for {domain}")
                    return domain_data
                else:
                    logger.error(
                        f"Domain details API error: {result.get('desc', 'Unknown error')}"
                    )
                    return None
            else:
                logger.error(
                    f"Domain details HTTP error: {response.status_code} {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Domain details exception: {e}")
            return None

    def get_nameservers(self, domain: str) -> List[str]:
        """Get current nameservers for domain"""
        try:
            domain_details = self.get_domain_details(domain)
            if domain_details:
                nameservers = domain_details.get("name_servers", [])

                # Return list of nameserver names
                ns_list = []
                for ns in nameservers:
                    if isinstance(ns, dict):
                        ns_list.append(ns.get("name", ""))
                    else:
                        ns_list.append(str(ns))

                logger.info(f"Retrieved nameservers for {domain}: {ns_list}")
                return ns_list
            else:
                logger.error(f"Failed to get nameservers for domain {domain}")
                return []

        except Exception as e:
            logger.error(f"Error getting nameservers for {domain}: {e}")
            return []

    def check_domain_availability(self, domain: str) -> bool:
        """Check if domain is available for registration"""
        try:
            if not self.token:
                self._authenticate()
            
            url = f"{self.base_url}/v1beta/domains/search"
            
            # Split domain into name and extension
            domain_parts = domain.split(".")
            domain_name = domain_parts[0]
            domain_extension = ".".join(domain_parts[1:])
            
            data = {
                "domains": [{"name": domain_name, "extension": domain_extension}]
            }
            
            response = requests.post(url, headers=self._get_headers(), json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    domains_data = result.get("data", {}).get("domains", [])
                    if domains_data:
                        domain_info = domains_data[0]
                        # Domain is available if status is "available"
                        is_available = domain_info.get("status") == "available"
                        logger.info(f"Domain {domain} availability: {'available' if is_available else 'not available'}")
                        return is_available
                    else:
                        logger.warning(f"No data returned for domain {domain}")
                        return False
                else:
                    logger.error(f"Domain availability API error: {result.get('desc', 'Unknown error')}")
                    return False
            else:
                logger.error(f"Domain availability HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Domain availability check exception: {e}")
            return False

