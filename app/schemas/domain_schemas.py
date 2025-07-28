"""
Domain Pydantic schemas for Nomadly3 API
"""

from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class DomainBase(BaseModel):
    """Base domain schema with common fields"""
    domain_name: str
    nameserver_mode: str = "cloudflare"
    auto_renew: bool = True
    
    @field_validator('domain_name')
    @classmethod
    def validate_domain_name(cls, v):
        import re
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v.lower()):
            raise ValueError('Invalid domain name format')
        return v.lower()
    
    @field_validator('nameserver_mode')
    @classmethod
    def validate_nameserver_mode(cls, v):
        if v not in ['cloudflare', 'custom']:
            raise ValueError('Nameserver mode must be cloudflare or custom')
        return v

class DomainCreate(DomainBase):
    """Schema for creating a new domain registration"""
    telegram_id: int
    price_paid: Decimal
    payment_method: str
    expires_at: Optional[datetime] = None
    
    @field_validator('price_paid')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

class DomainRegistrationRequest(BaseModel):
    """Schema for domain registration requests"""
    domain_name: str
    tld: str
    nameserver_type: str = "cloudflare"
    contact_handle: Optional[str] = None
    price_paid: Decimal
    payment_method: str = "cryptocurrency"
    auto_renew: bool = True
    
    @field_validator('domain_name')
    @classmethod
    def validate_domain_name(cls, v):
        import re
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$'
        if not re.match(pattern, v.lower()):
            raise ValueError('Invalid domain name format')
        return v.lower()
    
    @field_validator('tld')
    @classmethod
    def validate_tld(cls, v):
        if not v.startswith('.'):
            v = '.' + v
        if len(v) < 3 or len(v) > 10:
            raise ValueError('Invalid TLD format')
        return v.lower()
    
    @field_validator('nameserver_type')
    @classmethod
    def validate_nameserver_type(cls, v):
        if v not in ['cloudflare', 'custom']:
            raise ValueError('Nameserver type must be cloudflare or custom')
        return v

class DomainUpdate(BaseModel):
    """Schema for updating domain information"""
    nameserver_mode: Optional[str] = None
    auto_renew: Optional[bool] = None
    status: Optional[str] = None
    nameservers: Optional[List[str]] = None
    
    @field_validator('nameserver_mode')
    @classmethod
    def validate_nameserver_mode(cls, v):
        if v is not None and v not in ['cloudflare', 'custom']:
            raise ValueError('Nameserver mode must be cloudflare or custom')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ['active', 'expired', 'suspended']:
            raise ValueError('Status must be active, expired, or suspended')
        return v

# Alias for consistency with other files
DomainUpdateRequest = DomainUpdate

class DomainAvailabilityRequest(BaseModel):
    """Schema for domain availability check requests"""
    domain_name: str
    tld: str
    
    @field_validator('domain_name')
    @classmethod
    def validate_domain_name(cls, v):
        import re
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$'
        if not re.match(pattern, v.lower()):
            raise ValueError('Invalid domain name format')
        return v.lower()
    
    @field_validator('tld')
    @classmethod
    def validate_tld(cls, v):
        if not v.startswith('.'):
            v = '.' + v
        if len(v) < 3 or len(v) > 10:
            raise ValueError('Invalid TLD format')
        return v.lower()

class DomainAvailabilityResponse(BaseModel):
    """Schema for domain availability check responses"""
    domain_name: str
    tld: str
    available: bool
    price: Optional[Decimal] = None
    currency: str = "USD"
    message: Optional[str] = None

class DomainResponse(DomainBase):
    """Schema for domain API responses"""
    id: int
    telegram_id: int
    openprovider_domain_id: Optional[str] = None
    openprovider_contact_handle: Optional[str] = None
    cloudflare_zone_id: Optional[str] = None
    nameservers: List[str] = []
    registration_date: datetime
    expires_at: Optional[datetime] = None
    status: str
    price_paid: Optional[Decimal] = None
    payment_method: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DomainListResponse(BaseModel):
    """Schema for domain list API responses"""
    domains: List[DomainResponse]
    total: int
    page: int = 1
    per_page: int = 50
    total_pages: int
    
    @classmethod
    def create(cls, domains: List[DomainResponse], total: int, page: int = 1, per_page: int = 50):
        """Create a domain list response with pagination info"""
        total_pages = (total + per_page - 1) // per_page
        return cls(
            domains=domains,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

class NameserverUpdate(BaseModel):
    """Schema for updating domain nameservers"""
    nameservers: List[str]
    nameserver_mode: Optional[str] = None
    
    @field_validator('nameservers')
    @classmethod
    def validate_nameservers(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one nameserver is required')
        
        for ns in v:
            # Basic nameserver validation
            import re
            pattern = r'^[a-zA-Z0-9][a-zA-Z0-9.-]{0,253}[a-zA-Z0-9]$'
            if not re.match(pattern, ns):
                raise ValueError(f'Invalid nameserver format: {ns}')
        
        return v

class DomainRenewal(BaseModel):
    """Schema for domain renewal"""
    new_expiry_date: datetime
    price_paid: Optional[Decimal] = None
    
    @field_validator('new_expiry_date')
    @classmethod
    def validate_expiry_date(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('Expiry date must be in the future')
        return v

class ContactBase(BaseModel):
    """Base contact schema"""
    company_name: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    state: Optional[str] = None
    zipcode: str
    country: str
    contact_type: str = "registrant"
    
    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        if len(v) != 2:
            raise ValueError('Country must be 2-character ISO code')
        return v.upper()
    
    @field_validator('contact_type')
    @classmethod
    def validate_contact_type(cls, v):
        if v not in ['registrant', 'admin', 'tech', 'billing']:
            raise ValueError('Invalid contact type')
        return v

class ContactCreate(ContactBase):
    """Schema for creating a new contact"""
    telegram_id: int
    handle: str
    is_default: bool = False

class ContactResponse(ContactBase):
    """Schema for contact API responses"""
    id: int
    telegram_id: int
    handle: str
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ContactUpdate(BaseModel):
    """Schema for updating contact information"""
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None