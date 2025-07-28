"""
OpenProvider Models for Nomadly3
Domain registration and contact management models
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class OpenProviderContact:
    """OpenProvider contact information for domain registration"""
    handle: Optional[str] = None
    first_name: str = "Privacy"
    last_name: str = "Protected"
    email: str = ""
    phone: str = "+1.5555551234"
    organization: str = "Nameword Offshore Services"
    
    # Address fields
    street: str = "1234 Privacy Lane"
    city: str = "Georgetown"
    state: str = "GT"
    postal_code: str = "KY1-1111"
    country: str = "KY"  # Cayman Islands
    
    # Internal tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    telegram_id: Optional[int] = None
    
    def to_openprovider_format(self) -> Dict[str, Any]:
        """Convert to OpenProvider API format"""
        return {
            "name": {
                "first_name": self.first_name,
                "last_name": self.last_name
            },
            "email": self.email,
            "phone": {
                "country_code": "+1",
                "area_code": "555",
                "subscriber_number": "5551234"
            },
            "address": {
                "street": self.street,
                "city": self.city,
                "state": self.state,
                "zipcode": self.postal_code,
                "country": self.country
            },
            "organization_name": self.organization
        }
    
    @classmethod
    def create_anonymous_contact(cls, email: Optional[str] = None, telegram_id: Optional[int] = None) -> 'OpenProviderContact':
        """Create anonymous contact for privacy-focused registrations"""
        return cls(
            email=email or "privacy@nameword.offshore",
            telegram_id=telegram_id,
            first_name="Anonymous",
            last_name="User",
            organization="Nameword Privacy Services"
        )
    
    @classmethod
    def create_from_user_data(cls, user_data: Dict[str, Any], telegram_id: int) -> 'OpenProviderContact':
        """Create contact from user-provided data"""
        return cls(
            first_name=user_data.get("first_name", "Privacy"),
            last_name=user_data.get("last_name", "Protected"),
            email=user_data.get("email", "privacy@nameword.offshore"),
            telegram_id=telegram_id,
            organization=user_data.get("organization", "Nameword Offshore Services")
        )

@dataclass
class OpenProviderDomain:
    """OpenProvider domain information"""
    domain_name: str
    openprovider_id: Optional[str] = None
    status: str = "pending"
    
    # Registration details
    registrant_handle: Optional[str] = None
    admin_handle: Optional[str] = None
    tech_handle: Optional[str] = None
    billing_handle: Optional[str] = None
    
    # Nameservers
    nameservers: list = field(default_factory=list)
    
    # Dates
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def to_registration_request(self) -> Dict[str, Any]:
        """Convert to OpenProvider domain registration format"""
        return {
            "domain": {"name": self.domain_name},
            "period": 1,
            "nameservers": [{"name": ns} for ns in self.nameservers] if self.nameservers else [],
            "owner_handle": self.registrant_handle,
            "admin_handle": self.admin_handle or self.registrant_handle,
            "tech_handle": self.tech_handle or self.registrant_handle,
            "billing_handle": self.billing_handle or self.registrant_handle
        }

# Legacy aliases for compatibility
RegisteredDomain = OpenProviderDomain