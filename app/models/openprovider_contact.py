"""
OpenProvider Contact model for domain registration
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class OpenProviderContact:
    """Contact information for OpenProvider domain registration"""
    
    # Required fields
    first_name: str
    last_name: str
    email: str
    
    # Address information
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    country: str = "NL"  # Default to Netherlands for offshore hosting
    
    # Phone information
    phone: Optional[str] = None
    
    # Organization (optional)
    company_name: Optional[str] = None
    
    # OpenProvider specific
    handle: Optional[str] = None  # Contact handle from OpenProvider
    type: str = "registrant"  # registrant, admin, tech, billing
    
    def __post_init__(self):
        """Validate required fields"""
        if not self.first_name or not self.last_name:
            raise ValueError("First name and last name are required")
        
        if not self.email or "@" not in self.email:
            raise ValueError("Valid email address is required")
    
    def to_openprovider_dict(self) -> dict:
        """Convert to OpenProvider API format"""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "address": {
                "street": self.address or "Offshore Address",
                "city": self.city or "Amsterdam", 
                "state": self.state or "",
                "zipcode": self.zipcode or "1000 AA",
                "country": self.country
            },
            "phone": {
                "country_code": "+31",
                "area_code": "",
                "subscriber_number": self.phone or "201234567"
            },
            "company_name": self.company_name or "",
            "type": self.type
        }
    
    @classmethod
    def create_anonymous_contact(cls, email: Optional[str] = None) -> "OpenProviderContact":
        """Create anonymous contact for privacy-focused registration"""
        return cls(
            first_name="Offshore",
            last_name="Registrant",
            email=email or "privacy@nameword.offshore",
            address="Privacy Protected Address",
            city="Amsterdam",
            state="North Holland",
            zipcode="1000 AA",
            country="NL",
            phone="+31201234567",
            company_name="Nameword Offshore Services"
        )
    
    @classmethod
    def from_user_input(cls, first_name: str, last_name: str, email: str, 
                       phone: Optional[str] = None, company: Optional[str] = None) -> "OpenProviderContact":
        """Create contact from user input"""
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company,
            address="User Provided Address",
            city="Amsterdam",  # Default offshore location
            country="NL"
        )