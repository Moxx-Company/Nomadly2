"""
OpenProvider API Models for Nomadly3
Data models for OpenProvider domain registration integration
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class OpenProviderContact:
    """Contact information for domain registration with OpenProvider"""
    
    # Required fields
    email: str
    
    # Personal information (can be privacy-protected)
    first_name: str = "Privacy"
    last_name: str = "Protected"
    
    # Address information (offshore-focused defaults)
    company_name: Optional[str] = "Nameword Offshore Services"
    street: str = "Offshore Business District"
    city: str = "Privacy City"
    state: str = "Discretion"
    zipcode: str = "00000"
    country: str = "NL"  # Netherlands for offshore hosting
    
    # Contact details
    phone: str = "+31.000000000"  # Netherlands phone format
    fax: Optional[str] = None
    
    # Organization details
    organization_type: str = "individual"
    vat: Optional[str] = None
    
    def to_openprovider_format(self) -> Dict[str, Any]:
        """Convert to OpenProvider API format"""
        return {
            "name": {
                "firstName": self.first_name,
                "lastName": self.last_name,
                "fullName": f"{self.first_name} {self.last_name}"
            },
            "address": {
                "street": self.street,
                "city": self.city,
                "state": self.state,
                "zipcode": self.zipcode,
                "country": self.country
            },
            "phone": {
                "countryCode": self.phone.split('.')[0].replace('+', ''),
                "areaCode": "",
                "subscriberNumber": self.phone.split('.')[1] if '.' in self.phone else self.phone.replace('+', '').replace('.', '')
            },
            "email": self.email,
            "companyName": self.company_name,
            "organizationType": self.organization_type
        }
    
    @classmethod
    def create_privacy_contact(cls, email: str = "privacy@nameword.offshore") -> "OpenProviderContact":
        """Create privacy-protected contact for anonymous registrations"""
        return cls(
            email=email,
            first_name="Privacy",
            last_name="Protected",
            company_name="Nameword Offshore Services",
            street="Offshore Business District",
            city="Privacy City",
            state="Discretion",
            zipcode="00000",
            country="NL",
            phone="+31.000000000"
        )
    
    @classmethod
    def create_from_user_data(cls, email: str, **kwargs) -> "OpenProviderContact":
        """Create contact from user-provided data with privacy defaults"""
        return cls(
            email=email,
            first_name=kwargs.get('first_name', 'Privacy'),
            last_name=kwargs.get('last_name', 'Protected'),
            company_name=kwargs.get('company_name', 'Nameword Offshore Services'),
            street=kwargs.get('street', 'Offshore Business District'),
            city=kwargs.get('city', 'Privacy City'),
            state=kwargs.get('state', 'Discretion'),
            zipcode=kwargs.get('zipcode', '00000'),
            country=kwargs.get('country', 'NL'),
            phone=kwargs.get('phone', '+31.000000000')
        )

@dataclass
class OpenProviderDomain:
    """Domain information from OpenProvider API"""
    
    id: int
    name: str
    status: str
    creation_date: datetime
    expiry_date: datetime
    
    # Registration details
    registrant_handle: Optional[str] = None
    admin_handle: Optional[str] = None
    tech_handle: Optional[str] = None
    billing_handle: Optional[str] = None
    
    # Nameserver information
    nameservers: List[str] = None
    
    # Lock status
    is_locked: bool = False
    is_private: bool = True
    
    def __post_init__(self):
        if self.nameservers is None:
            self.nameservers = []
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "OpenProviderDomain":
        """Create domain object from OpenProvider API response"""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            status=data.get('status'),
            creation_date=datetime.fromisoformat(data.get('creationDate', '').replace('Z', '+00:00')),
            expiry_date=datetime.fromisoformat(data.get('expiryDate', '').replace('Z', '+00:00')),
            registrant_handle=data.get('registrantHandle'),
            admin_handle=data.get('adminHandle'),
            tech_handle=data.get('techHandle'),
            billing_handle=data.get('billingHandle'),
            nameservers=data.get('nameServers', []),
            is_locked=data.get('isLocked', False),
            is_private=data.get('isPrivate', True)
        )

@dataclass
class DomainAvailabilityResult:
    """Result from domain availability check"""
    
    domain: str
    available: bool
    premium: bool = False
    price: Optional[float] = None
    currency: str = "USD"
    alternative_suggestions: List[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.alternative_suggestions is None:
            self.alternative_suggestions = []

@dataclass
class DomainRegistrationRequest:
    """Request for domain registration"""
    
    domain_name: str
    registration_period: int = 1
    nameserver_mode: str = "cloudflare"  # cloudflare or custom
    custom_nameservers: Optional[List[str]] = None
    technical_email: Optional[str] = None
    privacy_protection: bool = True
    auto_renew: bool = False
    
    def __post_init__(self):
        if self.custom_nameservers is None:
            self.custom_nameservers = []