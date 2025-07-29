"""
Nomadly2 - API Services v1.4
Integration with OpenProvider, Cloudflare, and BlockBee APIs
"""

import os
import requests
import hashlib
import random
import string
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()

class OpenProviderAPI:
    """OpenProvider domain registration API"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = "https://api.openprovider.eu"
        self.token = None
        self.token_expires = None

    def authenticate(self) -> bool:
        """Authenticate with OpenProvider API"""
        try:
            response = requests.post(
                f"{self.base_url}/v1beta/auth/login",
                json={"username": self.username, "password": self.password},
                timeout=8,
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("data", {}).get("token")
                # Token expires in 24 hours
                self.token_expires = datetime.now() + timedelta(hours=23)
                return True

            return False

        except Exception as e:
            print(f"OpenProvider authentication error: {e}")
            return False

    def is_token_valid(self) -> bool:
        """Check if current token is valid"""
        return self.token and self.token_expires and datetime.now() < self.token_expires

    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        if not self.is_token_valid():
            self.authenticate()

        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def check_domain_availability(self, domain: str) -> Dict:
        """Check if domain is available for registration"""
        try:
            if not self.is_token_valid():
                if not self.authenticate():
                    return {"available": False, "error": "Authentication failed"}

            # Split domain name and extension for OpenProvider API
            if "." in domain:
                name_parts = domain.split(".")
                domain_name = name_parts[0]
                extension = name_parts[1]
            else:
                return {"available": False, "error": "Invalid domain format"}

            # OpenProvider API requires separate name and extension
            response = requests.post(
                f"{self.base_url}/v1beta/domains/check",
                json={
                    "domains": [{"name": domain_name, "extension": extension}],
                    "with_price": True,
                },
                headers=self.get_headers(),
                timeout=30,  # Increased from 8s to 30s to resolve timeout issues
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("data", {}).get("results", [])

                if results:
                    domain_data = results[0]
                    price_info = domain_data.get("price", {})

                    # Apply 3.3x price multiplier to API response
                    from config import Config
                    api_price = price_info.get("reseller", {}).get("price", 0)
                    final_price = api_price * Config.PRICE_MULTIPLIER if api_price > 0 else 0
                    
                    return {
                        "available": domain_data.get("status") == "free",
                        "price": round(final_price, 2),  # Apply 3.3x multiplier and round
                        "currency": price_info.get("reseller", {}).get(
                            "currency", "USD"
                        ),
                        "premium": domain_data.get("is_premium", False),
                        "raw_response": domain_data,  # For debugging
                        "api_price": api_price,  # Keep original for reference
                    }

            # Log the full response for debugging
            print(
                f"OpenProvider API response: {response.status_code} - {response.text[:500]}"
            )
            return {
                "available": False,
                "error": f"API request failed: {response.status_code}",
            }

        except Exception as e:
            print(f"OpenProvider API exception: {e}")
            return {"available": False, "error": str(e)}

    def create_contact(self, contact_data: Dict) -> Optional[str]:
        """Create contact handle for domain registration"""
        try:
            response = requests.post(
                f"{self.base_url}/v1beta/contacts",
                json=contact_data,
                headers=self.get_headers(),
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("handle")

            return None

        except Exception as e:
            print(f"Create contact error: {e}")
            return None

    def register_domain(
        self, domain: str, contact_handle: str, nameservers: List[str] = None
    ) -> Optional[str]:
        """Register domain with OpenProvider"""
        try:
            domain_data = {
                "domain": {"name": domain},
                "period": 1,  # 1 year
                "owner_handle": contact_handle,
                "admin_handle": contact_handle,
                "tech_handle": contact_handle,
                "billing_handle": contact_handle,
                "auto_renew": "on",
            }

            if nameservers:
                domain_data["name_servers"] = [{"name": ns} for ns in nameservers]

            response = requests.post(
                f"{self.base_url}/v1beta/domains",
                json=domain_data,
                headers=self.get_headers(),
                timeout=8,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("id")

            return None

        except Exception as e:
            print(f"Domain registration error: {e}")
            return None

    def update_nameservers(self, domain: str, nameservers: List[str]) -> bool:
        """Update nameservers for a domain"""
        try:
            if not self.is_token_valid():
                if not self.authenticate():
                    print("Authentication failed for nameserver update")
                    return False

            print(f"Updating nameservers for {domain}: {nameservers}")

            headers = self.get_headers()

            # For nomadly11.sbs, use known domain ID from database
            if domain == "nomadly11.sbs":
                domain_id = "27816852"
                url = f"{self.base_url}/v1beta/domains/{domain_id}"
            else:
                # For other domains, try domain name first
                url = f"{self.base_url}/v1beta/domains/{domain}"

            # Prepare nameserver data - OpenProvider expects specific format
            ns_data = []
            for i, ns in enumerate(nameservers):
                ns_data.append(
                    {
                        "name": ns,
                        "ip": "",  # OpenProvider will resolve the IP
                        "seq_nr": i + 1,
                    }
                )

            data = {"name_servers": ns_data}

            print(f"Making OpenProvider API call to update nameservers for {domain}")
            response = requests.put(url, json=data, headers=headers, timeout=8)

            if response.status_code in [200, 201]:
                print(f"✅ Successfully updated nameservers for {domain}")
                return True
            else:
                print(
                    f"OpenProvider nameserver update failed: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            print(f"Error updating nameservers for {domain}: {e}")
            return False


class CloudflareAPI:
    """Cloudflare DNS management API"""

    def __init__(self, api_token: str, email: str):
        self.api_token = api_token
        self.email = email
        self.base_url = "https://api.cloudflare.com/client/v4"

    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        return {
                "X-Auth-Email": self.email,
                "X-Auth-Key": self.api_token,
                "Content-Type": "application/json",
            }

    def create_zone(self, domain: str) -> Optional[str]:
        """Create DNS zone for domain"""
        try:
            response = requests.post(
                f"{self.base_url}/zones",
                json={"name": domain, "type": "full"},
                headers=self.get_headers(),
                timeout=8,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("result", {}).get("id")

            return None

        except Exception as e:
            print(f"Create zone error: {e}")
            return None

    def get_nameservers(self, cloudflare_zone_id: str) -> List[str]:
        """Get Cloudflare nameservers for zone"""
        try:
            response = requests.get(
                f"{self.base_url}/zones/{cloudflare_zone_id}",
                headers=self.get_headers(),
                timeout=8,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("result", {}).get("name_servers", [])

            return []

        except Exception as e:
            print(f"Get nameservers error: {e}")
            return []

    def create_dns_record(
        self,
        cloudflare_zone_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 3600,
        priority: int = None,
        proxied: bool = False,
    ) -> Optional[str]:
        """Create DNS record"""
        try:
            record_data = {
                "type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl,
                "proxied": proxied,
            }

            if priority and record_type in ["MX", "SRV"]:
                record_data["priority"] = priority

            response = requests.post(
                f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records",
                json=record_data,
                headers=self.get_headers(),
                timeout=8,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("result", {}).get("id")

            return None

        except Exception as e:
            print(f"Create DNS record error: {e}")
            return None

    def list_dns_records(self, cloudflare_zone_id: str) -> List[Dict]:
        """List all DNS records for zone"""
        try:
            response = requests.get(
                f"{self.base_url}/zones/{cloudflare_zone_id}/dns_records",
                headers=self.get_headers(),
                timeout=8,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("result", [])

            return []

        except Exception as e:
            print(f"List DNS records error: {e}")
            return []

    async def get_zone_id(self, domain_name: str) -> Optional[str]:
        """Get zone ID for a domain"""
        try:
            response = requests.get(
                f"{self.base_url}/zones",
                params={"name": domain_name},
                headers=self.get_headers(),
                timeout=8,
            )

            if response.status_code == 200:
                data = response.json()
                zones = data.get("result", [])
                if zones:
                    return zones[0].get("id")

            return None

        except Exception as e:
            print(f"Get zone ID error: {e}")
            return None

    def get_zone_by_domain(self, domain_name: str) -> Dict:
        """Get zone information by domain name"""
        try:
            response = requests.get(
                f"{self.base_url}/zones",
                params={"name": domain_name},
                headers=self.get_headers(),
                timeout=8,
            )

            if response.status_code == 200:
                data = response.json()
                zones = data.get("result", [])
                if zones:
                    zone = zones[0]
                    return {"success": True, "zone": zone}
                else:
                    return {"success": False, "error": "Zone not found"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"Zone lookup error: {e}")
            return {"success": False, "error": str(e)}


class BlockBeeAPI:
    """BlockBee cryptocurrency payment API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.blockbee.io"

    def get_supported_coins(self) -> List[str]:
        """Get list of supported cryptocurrencies"""
        return [
            "btc",
            "eth",
            "ltc",
            "bch",
            "doge",
            "dash",
            "trx",
            "bnb",
            "matic",
            "usdt",
            "usdc",
        ]

    def get_coin_info(self, coin: str) -> Dict:
        """Get information about specific cryptocurrency"""
        try:
            response = requests.get(
                f"{self.base_url}/{coin}/info/",
                params={"apikey": self.api_key},
                timeout=8,
            )

            if response.status_code == 200:
                return response.json()

            return {}

        except Exception as e:
            print(f"Get coin info error: {e}")
            return {}

    def create_payment_address(
        self, coin: str, callback_url: str, amount: float = None
    ) -> Dict:
        """Create payment address for cryptocurrency"""
        try:
            params = {"apikey": self.api_key, "callback": callback_url}

            if amount:
                params["value"] = str(amount)

            response = requests.get(
                f"{self.base_url}/{coin}/create/", params=params, timeout=30
            )

            if response.status_code == 200:
                return response.json()

            return {}

        except Exception as e:
            print(f"Create payment address error: {e}")
            return {}

    def check_payment_status(self, coin: str, address: str) -> Dict:
        """Check payment status for address"""
        try:
            response = requests.get(
                f"{self.base_url}/{coin}/logs/",
                params={"apikey": self.api_key, "address": address},
                timeout=8,
            )

            if response.status_code == 200:
                return response.json()

            return {}

        except Exception as e:
            print(f"Check payment status error: {e}")
            return {}

    def get_conversion_rate(self, coin: str, value: float) -> float:
        """Get cryptocurrency conversion rate to USD"""
        try:
            response = requests.get(
                f"{self.base_url}/{coin}/convert/",
                params={"apikey": self.api_key, "value": str(value), "from": "usd"},
                timeout=8,
            )

            if response.status_code == 200:
                data = response.json()
                return float(data.get("value_coin", 0))

            return 0.0

        except Exception as e:
            print(f"Get conversion rate error: {e}")
            return 0.0


class ContactGenerator:
    """Generate random US contact information for privacy"""

    @staticmethod
    def generate_random_identity() -> Dict:
        """Generate complete random US identity"""
        first_names = [
            "James",
            "John",
            "Robert",
            "Michael",
            "William",
            "David",
            "Richard",
            "Joseph",
            "Thomas",
            "Christopher",
            "Charles",
            "Daniel",
            "Matthew",
            "Anthony",
            "Mark",
            "Donald",
            "Steven",
            "Paul",
            "Andrew",
            "Joshua",
            "Kenneth",
            "Kevin",
            "Brian",
            "George",
            "Timothy",
            "Ronald",
            "Jason",
            "Edward",
            "Jeffrey",
            "Ryan",
            "Jacob",
            "Gary",
            "Nicholas",
            "Eric",
            "Jonathan",
            "Stephen",
            "Larry",
            "Justin",
            "Scott",
            "Brandon",
            "Benjamin",
            "Samuel",
            "Gregory",
            "Alexander",
            "Patrick",
            "Frank",
        ]

        last_names = [
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
            "Jones",
            "Garcia",
            "Miller",
            "Davis",
            "Rodriguez",
            "Martinez",
            "Hernandez",
            "Lopez",
            "Gonzalez",
            "Wilson",
            "Anderson",
            "Thomas",
            "Taylor",
            "Moore",
            "Jackson",
            "Martin",
            "Lee",
            "Perez",
            "Thompson",
            "White",
            "Harris",
            "Sanchez",
            "Clark",
            "Ramirez",
            "Lewis",
            "Robinson",
            "Walker",
            "Young",
            "Allen",
            "King",
            "Wright",
            "Scott",
            "Torres",
            "Nguyen",
            "Hill",
            "Flores",
            "Green",
            "Adams",
            "Nelson",
            "Baker",
            "Hall",
            "Rivera",
            "Campbell",
            "Mitchell",
        ]

        states = [
            ("Alabama", "AL", ["Birmingham", "Montgomery", "Mobile"]),
            ("Arizona", "AZ", ["Phoenix", "Tucson", "Mesa"]),
            ("California", "CA", ["Los Angeles", "San Francisco", "San Diego"]),
            ("Colorado", "CO", ["Denver", "Colorado Springs", "Aurora"]),
            ("Florida", "FL", ["Miami", "Orlando", "Tampa"]),
            ("Georgia", "GA", ["Atlanta", "Augusta", "Columbus"]),
            ("Illinois", "IL", ["Chicago", "Aurora", "Rockford"]),
            ("Indiana", "IN", ["Indianapolis", "Fort Wayne", "Evansville"]),
            ("Kentucky", "KY", ["Louisville", "Lexington", "Bowling Green"]),
            ("Louisiana", "LA", ["New Orleans", "Baton Rouge", "Shreveport"]),
            ("Michigan", "MI", ["Detroit", "Grand Rapids", "Warren"]),
            ("Nevada", "NV", ["Las Vegas", "Henderson", "Reno"]),
            ("New York", "NY", ["New York", "Buffalo", "Rochester"]),
            ("North Carolina", "NC", ["Charlotte", "Raleigh", "Greensboro"]),
            ("Ohio", "OH", ["Columbus", "Cleveland", "Cincinnati"]),
            ("Pennsylvania", "PA", ["Philadelphia", "Pittsburgh", "Allentown"]),
            ("Tennessee", "TN", ["Nashville", "Memphis", "Knoxville"]),
            ("Texas", "TX", ["Houston", "San Antonio", "Dallas"]),
            ("Virginia", "VA", ["Virginia Beach", "Norfolk", "Chesapeake"]),
            ("Washington", "WA", ["Seattle", "Spokane", "Tacoma"]),
        ]

        # Generate random identity
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        state_info = random.choice(states)
        state_name, state_code, cities = state_info
        city = random.choice(cities)

        # Generate random address
        street_number = random.randint(100, 9999)
        street_names = [
            "Main St",
            "First St",
            "Second St",
            "Park Ave",
            "Oak St",
            "Pine St",
            "Maple Ave",
            "Cedar St",
            "Elm St",
            "Washington St",
            "Lincoln Ave",
            "Jefferson St",
            "Madison Ave",
            "Franklin St",
        ]
        street_name = random.choice(street_names)
        address = f"{street_number} {street_name}"

        # Generate postal code (simplified)
        postal_code = f"{random.randint(10000, 99999)}"

        # Generate phone number
        area_code = random.randint(200, 999)
        phone_number = f"+1.{area_code}{random.randint(1000000, 9999999)}"

        # Generate email
        email_providers = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(email_providers)}"

        # Generate date of birth (21-65 years old)
        birth_year = random.randint(1959, 2003)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Safe day for all months

        # Generate passport number (simplified)
        passport_number = "".join(
            [random.choice(string.ascii_uppercase) for _ in range(2)]
        ) + "".join([str(random.randint(0, 9)) for _ in range(7)])

        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone_number,
            "address_line1": address,
            "city": city,
            "state": state_name,
            "state_code": state_code,
            "postal_code": postal_code,
            "country_code": "US",
            "date_of_birth": f"{birth_year}-{birth_month:02d}-{birth_day:02d}",
            "passport_number": passport_number,
        }


class APIServiceManager:
    """Manage all API services"""

    def __init__(self):
        self.openprovider = None
        self.cloudflare = None
        self.blockbee = None
        self.initialize_apis()

    def initialize_apis(self):
        """Initialize API services with environment variables"""
        # OpenProvider API
        op_username = os.getenv("OPENPROVIDER_USERNAME")
        op_password = os.getenv("OPENPROVIDER_PASSWORD")
        if op_username and op_password:
            self.openprovider = OpenProviderAPI(op_username, op_password)

        # Cloudflare API
        cf_token = os.getenv("CLOUDFLARE_API_TOKEN")
        cf_email = os.getenv("CLOUDFLARE_EMAIL")
        if cf_token and cf_email:
            self.cloudflare = CloudflareAPI(cf_token, cf_email)

        # BlockBee API
        bb_key = os.getenv("BLOCKBEE_API_KEY")
        if bb_key:
            self.blockbee = BlockBeeAPI(bb_key)

    def is_configured(self) -> Dict[str, bool]:
        """Check which APIs are configured"""
        return {
            "openprovider": self.openprovider is not None,
            "cloudflare": self.cloudflare is not None,
            "blockbee": self.blockbee is not None,
        }

    def test_apis(self) -> Dict[str, bool]:
        """Test API connectivity"""
        results = {}

        # Test OpenProvider
        if self.openprovider:
            results["openprovider"] = self.openprovider.authenticate()
        else:
            results["openprovider"] = False

        # Test Cloudflare (simplified check)
        if self.cloudflare:
            try:
                response = requests.get(
                    f"{self.cloudflare.base_url}/user/tokens/verify",
                    headers=self.cloudflare.get_headers(),
                    timeout=10,
                )
                results["cloudflare"] = response.status_code == 200
            except:
                results["cloudflare"] = False
        else:
            results["cloudflare"] = False

        # Test BlockBee
        if self.blockbee:
            try:
                info = self.blockbee.get_coin_info("btc")
                results["blockbee"] = bool(info)
            except:
                results["blockbee"] = False
        else:
            results["blockbee"] = False

        return results


# Global API service manager
api_manager = None


def get_api_manager() -> APIServiceManager:
    """Get global API service manager instance"""
    global api_manager
    if api_manager is None:
        api_manager = APIServiceManager()
    return api_manager
