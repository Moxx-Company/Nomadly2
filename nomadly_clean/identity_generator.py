"""
Identity Generator for WHOIS Privacy Protection
Generates realistic identity data for domain privacy protection
"""

import random
import string
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class IdentityGenerator:
    """Generate identity data for domain registration privacy"""
    
    def __init__(self):
        # Nomadly offshore company data
        self.company_names = [
            "Nomadly Holdings Ltd",
            "Nomadly International Services",
            "Nomadly Digital Ventures",
            "Nomadly Privacy Protection Services",
            "Nomadly Trust Services Ltd"
        ]
        
        # Offshore addresses for privacy
        self.addresses = [
            {
                "street": "Suite 305, Griffith Corporate Centre",
                "city": "Beachmont",
                "state": "Kingstown",
                "postal_code": "VC0100",
                "country": "VC",  # Saint Vincent and the Grenadines
                "country_name": "Saint Vincent and the Grenadines"
            },
            {
                "street": "PO Box 1708, First Floor, Columbus Centre",
                "city": "Road Town",
                "state": "Tortola",
                "postal_code": "VG1110",
                "country": "VG",  # British Virgin Islands
                "country_name": "British Virgin Islands"
            },
            {
                "street": "80 Broad Street, 5th Floor",
                "city": "Monrovia",
                "state": "Montserrado",
                "postal_code": "1000",
                "country": "LR",  # Liberia
                "country_name": "Liberia"
            }
        ]
        
        # Privacy-protected contact info
        self.phone_formats = [
            "+1.2025550100",  # US format for compatibility
            "+44.2079460100",  # UK format
            "+1.8885550100"   # Toll-free format
        ]
        
        self.privacy_email = "privacy@nomadly.com"
        
    def generate_identity(self, domain_name: str = None) -> Dict[str, Any]:
        """Generate a complete identity for domain registration"""
        try:
            # Select random company and address
            company = random.choice(self.company_names)
            address = random.choice(self.addresses)
            phone = random.choice(self.phone_formats)
            
            # Generate unique identifier for this identity
            identifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            identity = {
                # Owner information
                "owner": {
                    "company_name": company,
                    "first_name": "Privacy",
                    "last_name": "Protection",
                    "full_name": f"Privacy Protection {identifier}",
                    "email": self.privacy_email,
                    "phone": phone,
                    "address": address["street"],
                    "city": address["city"],
                    "state": address["state"],
                    "postal_code": address["postal_code"],
                    "country": address["country"],
                    "country_name": address["country_name"]
                },
                # Admin contact (same as owner for privacy)
                "admin": {
                    "company_name": company,
                    "first_name": "Admin",
                    "last_name": "Contact",
                    "full_name": f"Admin Contact {identifier}",
                    "email": self.privacy_email,
                    "phone": phone,
                    "address": address["street"],
                    "city": address["city"],
                    "state": address["state"],
                    "postal_code": address["postal_code"],
                    "country": address["country"],
                    "country_name": address["country_name"]
                },
                # Tech contact
                "tech": {
                    "company_name": company,
                    "first_name": "Technical",
                    "last_name": "Support",
                    "full_name": f"Technical Support {identifier}",
                    "email": self.privacy_email,
                    "phone": phone,
                    "address": address["street"],
                    "city": address["city"],
                    "state": address["state"],
                    "postal_code": address["postal_code"],
                    "country": address["country"],
                    "country_name": address["country_name"]
                },
                # Additional metadata
                "metadata": {
                    "identifier": identifier,
                    "privacy_enabled": True,
                    "company": company,
                    "location": address["country_name"]
                }
            }
            
            logger.info(f"✅ Generated privacy identity for domain: {domain_name or 'generic'}")
            return identity
            
        except Exception as e:
            logger.error(f"❌ Error generating identity: {e}")
            # Return minimal fallback identity
            return {
                "owner": {
                    "company_name": "Nomadly Privacy Services",
                    "first_name": "Privacy",
                    "last_name": "Protected",
                    "email": "privacy@nomadly.com",
                    "phone": "+1.8885550100",
                    "address": "Privacy Protected",
                    "city": "Privacy Protected",
                    "state": "N/A",
                    "postal_code": "00000",
                    "country": "US"
                },
                "admin": None,  # Same as owner
                "tech": None,   # Same as owner
                "metadata": {
                    "privacy_enabled": True,
                    "error": str(e)
                }
            }
    
    def get_openprovider_contact(self, identity_data: Dict[str, Any], contact_type: str = "owner") -> Dict[str, Any]:
        """Convert identity to OpenProvider contact format"""
        contact = identity_data.get(contact_type, identity_data.get("owner"))
        
        if not contact:
            return None
            
        return {
            "name": {
                "first_name": contact.get("first_name", "Privacy"),
                "last_name": contact.get("last_name", "Protected"),
                "full_name": contact.get("full_name", "Privacy Protected")
            },
            "company_name": contact.get("company_name", ""),
            "email": contact.get("email", self.privacy_email),
            "phone": {
                "country_code": contact.get("phone", "+1.8885550100").split('.')[0],
                "number": contact.get("phone", "+1.8885550100").split('.')[1] if '.' in contact.get("phone", "") else "8885550100"
            },
            "address": {
                "street": contact.get("address", "Privacy Protected"),
                "city": contact.get("city", "Privacy Protected"),
                "state": contact.get("state", "N/A"),
                "zip_code": contact.get("postal_code", "00000"),
                "country": contact.get("country", "US")
            }
        }

# Global instance for easy access
identity_generator = IdentityGenerator()

def get_identity_generator():
    """Get the global identity generator instance"""
    return identity_generator