"""
OpenProvider API Integration
Handles domain registration, availability checking, and domain management
"""

import requests
import logging
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class OpenProviderAPI:
    def __init__(self, username: str, password: str, test_mode: bool = True):
        self.username = username
        self.password = password
        self.test_mode = test_mode
        self.base_url = "https://api.openprovider.eu"
        self.token = None

    def authenticate(self) -> bool:
        """Authenticate with OpenProvider API"""
        try:
            url = f"{self.base_url}/v1beta/auth/login"
            data = {"username": self.username, "password": self.password}

            response = requests.post(url, json=data, timeout=8)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("data", {}).get("token")
                logger.info("OpenProvider authentication successful")
                return True
            else:
                logger.error(
                    f"OpenProvider authentication failed: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"OpenProvider authentication error: {e}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self.token:
            self.authenticate()

        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def check_domain_availability(
        self, domain_name: str, tld: str
    ) -> Tuple[bool, float]:
        """Check if domain is available and get price"""
        try:
            url = f"{self.base_url}/v1beta/domains/check"
            data = {"domains": [{"name": domain_name, "extension": tld}]}

            response = requests.post(url, json=data, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                result = response.json()
                domains_data = result.get("data", {}).get("results", [])

                if domains_data:
                    domain_data = domains_data[0]
                    is_available = domain_data.get("status") == "free"

                    # Get pricing
                    price = self._get_domain_price(tld)

                    return is_available, price

            logger.error(f"Domain availability check failed: {response.status_code}")
            return False, 0.0

        except Exception as e:
            logger.error(f"Domain availability check error: {e}")
            return False, 0.0

    def _get_domain_price(self, tld: str) -> float:
        """Get domain registration price"""
        try:
            url = f"{self.base_url}/v1beta/domains/extensions"
            response = requests.get(url, headers=self._get_headers(), timeout=8)

            if response.status_code == 200:
                result = response.json()
                extensions = result.get("data", {}).get("results", [])

                for ext in extensions:
                    if ext.get("name") == tld:
                        prices = ext.get("prices", {})
                        create_price = prices.get("create", {})
                        api_price = float(create_price.get("price", 15.99))
                        # Apply 3.3x price multiplier
                        from config import Config
                        return round(api_price * Config.PRICE_MULTIPLIER, 2)

            # Fallback prices with 3.3x multiplier already applied
            from config import Config
            base_fallback_prices = {
                "com": 15.99,
                "net": 16.99,
                "org": 14.99,
                "info": 12.99,
                "biz": 13.99,
                "sbs": 8.99,
            }
            base_price = base_fallback_prices.get(tld, 15.99)
            return round(base_price * Config.PRICE_MULTIPLIER, 2)

        except Exception as e:
            logger.error(f"Price lookup error: {e}")
            return 15.99

    def register_domain(
        self, domain_name: str, tld: str, customer_data: Dict
    ) -> Tuple[bool, Optional[int], str]:
        """Register a domain and return success, domain_id, and message"""
        try:
            url = f"{self.base_url}/v1beta/domains"

            # Prepare domain registration data
            data = {
                "domain": {"name": domain_name, "extension": tld},
                "period": 1,  # 1 year
                "owner_handle": customer_data.get("handle_id"),
                "admin_handle": customer_data.get("handle_id"),
                "tech_handle": customer_data.get("handle_id"),
                "billing_handle": customer_data.get("handle_id"),
                "nameservers": [
                    {"name": "ns1.openprovider.nl"},
                    {"name": "ns2.openprovider.be"},
                    {"name": "ns3.openprovider.eu"},
                ],
                "use_domainlock": True,
                "autorenew": False,  # Disabled by default for privacy
                "auto_renew": False,
                "dnssec": False,  # DNSSEC disabled
            }

            response = requests.post(url, json=data, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                result = response.json()
                domain_data = result.get("data", {})
                domain_id = domain_data.get("id")

                logger.info(
                    f"Domain registered successfully: {domain_name}.{tld} (ID: {domain_id})"
                )
                return True, domain_id, "Domain registered successfully"

            else:
                error_msg = f"Domain registration failed: {response.status_code}"
                logger.error(error_msg)
                return False, None, error_msg

        except Exception as e:
            error_msg = f"Domain registration error: {e}"
            logger.error(error_msg)
            return False, None, error_msg

    def register_domain_with_nameservers(
        self, domain_name: str, tld: str, customer_data: Dict, nameservers: List[str]
    ) -> Tuple[bool, Optional[int], str]:
        """Register a domain with custom nameservers"""
        try:
            url = f"{self.base_url}/v1beta/domains"

            # Prepare nameserver data
            ns_data = (
                [{"name": ns} for ns in nameservers]
                if nameservers
                else [{"name": "ns1.openprovider.nl"}, {"name": "ns2.openprovider.be"}]
            )

            # Prepare domain registration data
            data = {
                "domain": {"name": domain_name, "extension": tld},
                "period": 1,  # 1 year
                "owner_handle": customer_data.get("handle_id"),
                "admin_handle": customer_data.get("handle_id"),
                "tech_handle": customer_data.get("handle_id"),
                "billing_handle": customer_data.get("handle_id"),
                "nameservers": ns_data,
                "use_domainlock": True,
                "autorenew": False,  # Disabled by default for privacy
                "auto_renew": False,
                "dnssec": False,  # DNSSEC disabled
            }

            response = requests.post(url, json=data, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                result = response.json()
                domain_data = result.get("data", {})
                domain_id = domain_data.get("id")

                logger.info(
                    f"Domain registered with custom nameservers: {domain_name}.{tld} (ID: {domain_id})"
                )
                return True, domain_id, "Domain registered successfully"

            else:
                error_msg = f"Domain registration failed: {response.status_code}"
                logger.error(error_msg)
                return False, None, error_msg

        except Exception as e:
            error_msg = f"Domain registration error: {e}"
            logger.error(error_msg)
            return False, None, error_msg

    def update_nameservers(self, domain_id: int, nameservers: List[str]) -> bool:
        """Update domain nameservers"""
        try:
            url = f"{self.base_url}/v1beta/domains/{domain_id}/nameservers"

            ns_data = [{"name": ns} for ns in nameservers]
            data = {"nameservers": ns_data}

            response = requests.put(url, json=data, headers=self._get_headers(), timeout=8)

            if response.status_code == 200:
                logger.info(f"Nameservers updated for domain {domain_id}")
                return True
            else:
                logger.error(f"Failed to update nameservers: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Nameserver update error: {e}")
            return False

    def create_customer_handle(self, user_data: Dict) -> Optional[str]:
        """Create customer handle for domain registration"""
        try:
            url = f"{self.base_url}/v1beta/customers"

            data = {
                "company_name": user_data.get("company_name", "Individual"),
                "name": {
                    "first_name": user_data.get("first_name", "John"),
                    "last_name": user_data.get("last_name", "Doe"),
                },
                "address": {
                    "street": user_data.get("street", "123 Main St"),
                    "number": "1",
                    "zipcode": user_data.get("zipcode", "12345"),
                    "city": user_data.get("city", "Anytown"),
                    "state": user_data.get("state", ""),
                    "country": user_data.get("country", "US"),
                },
                "phone": {
                    "country_code": user_data.get("phone_country", "+1"),
                    "area_code": user_data.get("area_code", "212"),
                    "subscriber_number": user_data.get("phone", "5551234"),
                },
                "email": user_data.get("email", "noreply@nomadly.com"),
                "birth_date": user_data.get("birth_date", "1980-01-01"),
            }

            response = requests.post(url, json=data, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                result = response.json()
                handle_id = result.get("data", {}).get("handle")
                logger.info(f"Customer handle created: {handle_id}")
                return handle_id
            else:
                logger.error(f"Customer handle creation failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Customer handle creation error: {e}")
            return None

    def update_nameservers(self, domain_id: int, nameservers: List[str]) -> bool:
        """Update domain nameservers"""
        try:
            url = f"{self.base_url}/v1beta/domains/{domain_id}"

            ns_list = [{"name": ns} for ns in nameservers]
            data = {"nameservers": ns_list}

            response = requests.put(url, json=data, headers=self._get_headers(), timeout=8)

            if response.status_code == 200:
                logger.info(f"Nameservers updated for domain ID {domain_id}")
                return True
            else:
                logger.error(f"Nameserver update failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Nameserver update error: {e}")
            return False

    def get_domain_info(self, domain_id: int) -> Optional[Dict]:
        """Get domain information"""
        try:
            url = f"{self.base_url}/v1beta/domains/{domain_id}"
            response = requests.get(url, headers=self._get_headers(), timeout=8)

            if response.status_code == 200:
                result = response.json()
                return result.get("data", {})
            else:
                logger.error(f"Domain info retrieval failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Domain info retrieval error: {e}")
            return None

    def list_domains(self, limit: int = 100) -> List[Dict]:
        """List all domains"""
        try:
            url = f"{self.base_url}/v1beta/domains"
            params = {"limit": limit}

            response = requests.get(url, params=params, headers=self._get_headers(), timeout=8)

            if response.status_code == 200:
                result = response.json()
                return result.get("data", {}).get("results", [])
            else:
                logger.error(f"Domain listing failed: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Domain listing error: {e}")
            return []
