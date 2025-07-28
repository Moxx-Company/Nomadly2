"""
Domain model for Nomadly3 Domain Registration Bot
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, BIGINT, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional

from ..core.database import Base

# Forward declarations for type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
    from .dns_record import DNSRecord

class RegisteredDomain(Base):
    """Domain registrations with DNS and nameserver management"""

    __tablename__ = "registered_domains"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    domain_name = Column(String(255), nullable=False, index=True)

    # OpenProvider integration
    openprovider_domain_id = Column(String(100))
    openprovider_contact_handle = Column(String(100))

    # Cloudflare integration
    cloudflare_zone_id = Column(String(100))
    nameservers = Column(JSONB, default=[])
    nameserver_mode = Column(String(50), default="cloudflare")  # cloudflare or custom

    # Registration details
    registration_date = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    status = Column(String(50), default="active")  # active, expired, suspended

    # Payment information
    price_paid = Column(DECIMAL(10, 2))
    payment_method = Column(String(50))  # wallet, btc, eth, etc.

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="domains", lazy="select")
    dns_records = relationship(
        "DNSRecord", back_populates="domain", cascade="all, delete-orphan",
        lazy="select", order_by="DNSRecord.record_type, DNSRecord.name"
    )
    
    # External service integrations - forward references to avoid import issues
    cloudflare_integration = relationship(
        "CloudflareIntegration", back_populates="domain", uselist=False, 
        cascade="all, delete-orphan", lazy="select"
    )
    openprovider_integration = relationship(
        "OpenProviderIntegration", back_populates="domain", uselist=False,
        cascade="all, delete-orphan", lazy="select"
    )
    telegram_notifications = relationship(
        "TelegramIntegration", back_populates="domain", 
        cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self):
        return f"<RegisteredDomain(domain_name={self.domain_name}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Check if domain is currently active"""
        return self.status == "active"

    @property
    def is_expired(self) -> bool:
        """Check if domain has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def days_until_expiry(self) -> Optional[int]:
        """Get number of days until domain expires"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    @property
    def uses_cloudflare_dns(self) -> bool:
        """Check if domain uses Cloudflare DNS"""
        return self.nameserver_mode == "cloudflare"

    @property
    def uses_custom_dns(self) -> bool:
        """Check if domain uses custom nameservers"""
        return self.nameserver_mode == "custom"

    def get_nameservers(self) -> List[str]:
        """Get domain nameservers as list"""
        if isinstance(self.nameservers, list):
            return self.nameservers
        return []

    def set_nameservers(self, nameservers: List[str]) -> None:
        """Set domain nameservers"""
        self.nameservers = nameservers

    def get_dns_record_count(self) -> int:
        """Get count of DNS records for this domain"""
        return len(self.dns_records) if self.dns_records else 0

    def mark_expired(self) -> None:
        """Mark domain as expired"""
        self.status = "expired"

    def renew_domain(self, new_expiry_date: datetime, price_paid: Decimal = None) -> None:
        """Renew domain registration"""
        self.expires_at = new_expiry_date
        self.status = "active"
        if price_paid:
            self.price_paid = price_paid
    
    def get_dns_records_by_type(self, record_type: str) -> List['DNSRecord']:
        """Get DNS records of specific type"""
        return [record for record in self.dns_records if record.record_type.upper() == record_type.upper()]
    
    def has_dns_record_type(self, record_type: str) -> bool:
        """Check if domain has DNS records of specific type"""
        return len(self.get_dns_records_by_type(record_type)) > 0
    
    def get_a_records(self) -> List['DNSRecord']:
        """Get all A records for this domain"""
        return self.get_dns_records_by_type("A")
    
    def get_mx_records(self) -> List['DNSRecord']:
        """Get all MX records for this domain"""
        return self.get_dns_records_by_type("MX")
    
    def get_txt_records(self) -> List['DNSRecord']:
        """Get all TXT records for this domain"""
        return self.get_dns_records_by_type("TXT")
    
    def get_root_records(self) -> List['DNSRecord']:
        """Get DNS records for the root domain (@)"""
        return [record for record in self.dns_records if record.is_root_record]
    
    def get_subdomain_records(self) -> List['DNSRecord']:
        """Get DNS records for subdomains"""
        return [record for record in self.dns_records if record.is_subdomain_record]
        if price_paid:
            self.price_paid = price_paid

    def suspend_domain(self) -> None:
        """Suspend domain"""
        self.status = "suspended"

    def reactivate_domain(self) -> None:
        """Reactivate suspended domain"""
        self.status = "active"


class OpenProviderContact(Base):
    """OpenProvider contact information for domain registration"""

    __tablename__ = "openprovider_contacts"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    handle = Column(String(100), nullable=False, unique=True)
    
    # Contact details (generated for privacy)
    company_name = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    
    # Address details
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    zipcode = Column(String(20))
    country = Column(String(2))  # ISO country code
    
    # Contact type and usage
    contact_type = Column(String(50), default="registrant")  # registrant, admin, tech, billing
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="openprovider_contacts")

    def __repr__(self):
        return f"<OpenProviderContact(handle={self.handle}, type={self.contact_type})>"

    @property
    def full_name(self) -> str:
        """Get full name of contact"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        parts = [self.address, self.city, self.state, self.zipcode, self.country]
        return ", ".join(filter(None, parts))

    def to_openprovider_dict(self) -> Dict[str, Any]:
        """Convert contact to OpenProvider API format"""
        return {
            "firstName": self.first_name,
            "lastName": self.last_name,
            "companyName": self.company_name,
            "email": self.email,
            "phone": self.phone,
            "address": {
                "street": self.address,
                "city": self.city,
                "state": self.state,
                "zipcode": self.zipcode,
                "country": self.country
            }
        }