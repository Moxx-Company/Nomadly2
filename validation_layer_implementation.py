#!/usr/bin/env python3
"""
Comprehensive Validation Layer Implementation for Nomadly3
Demonstrates proper Pydantic schema patterns with examples
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, Field
import re

# =============================================================================
# VALIDATION LAYER (SCHEMAS) - COMPREHENSIVE IMPLEMENTATION
# =============================================================================

class ValidationLayer:
    """
    Tech: Pydantic models
    Responsibilities:
    • Enforce API payload shapes
    • Validate incoming/outgoing data
    • Type conversion and sanitization
    • Business rule validation
    • Generate API documentation
    """

# =============================================================================
# 1. DOMAIN REGISTRATION VALIDATION SCHEMAS
# =============================================================================

class SupportedTLD(str, Enum):
    """Supported Top-Level Domains with offshore pricing"""
    COM = ".com"
    NET = ".net"
    ORG = ".org"
    INFO = ".info"
    BIZ = ".biz"
    ME = ".me"
    CO = ".co"
    IO = ".io"
    CC = ".cc"
    TV = ".tv"

class NameserverMode(str, Enum):
    """DNS Management Options"""
    CLOUDFLARE = "cloudflare"
    CUSTOM = "custom"

class DomainRegistrationRequest(BaseModel):
    """
    Domain Registration Input Validation
    Enforces: Domain format, TLD validation, pricing rules
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    domain_name: str = Field(
        ..., 
        min_length=1, 
        max_length=63,
        description="Domain name without TLD (e.g., 'mycompany')"
    )
    tld: SupportedTLD = Field(
        ...,
        description="Top-level domain from supported list"
    )
    nameserver_mode: NameserverMode = Field(
        default=NameserverMode.CLOUDFLARE,
        description="DNS management preference"
    )
    contact_email: Optional[EmailStr] = Field(
        default=None,
        description="Technical contact email (optional for anonymous registration)"
    )
    registration_years: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Registration period (1-10 years)"
    )
    auto_renew: bool = Field(
        default=True,
        description="Enable automatic renewal"
    )
    
    @field_validator('domain_name')
    @classmethod
    def validate_domain_name(cls, v: str) -> str:
        """Validate domain name format"""
        # Remove any accidental TLD inclusion
        v = v.lower().split('.')[0]
        
        # RFC compliant domain validation
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        if not re.match(pattern, v):
            raise ValueError(
                'Domain name must start and end with alphanumeric characters, '
                'contain only letters, numbers, and hyphens, max 63 characters'
            )
        
        # Business rules
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('Domain cannot start or end with hyphen')
        if '--' in v:
            raise ValueError('Domain cannot contain consecutive hyphens')
            
        return v
    
    @property
    def full_domain(self) -> str:
        """Generate complete domain name"""
        return f"{self.domain_name}{self.tld.value}"
    
    @property
    def offshore_price_usd(self) -> Decimal:
        """Calculate offshore pricing (3.3x multiplier)"""
        base_prices = {
            ".com": Decimal("15.00"),
            ".net": Decimal("18.00"), 
            ".org": Decimal("16.00"),
            ".info": Decimal("14.00"),
            ".biz": Decimal("17.00"),
            ".me": Decimal("25.00"),
            ".co": Decimal("30.00"),
            ".io": Decimal("45.00"),
            ".cc": Decimal("35.00"),
            ".tv": Decimal("40.00")
        }
        base_price = base_prices.get(self.tld.value, Decimal("20.00"))
        return (base_price * Decimal("3.3") * self.registration_years).quantize(Decimal("0.01"))

class DomainRegistrationResponse(BaseModel):
    """Domain Registration Output Validation"""
    model_config = ConfigDict(from_attributes=True)
    
    domain_id: int
    domain_name: str
    full_domain: str
    status: str = Field(..., pattern="^(pending|registered|failed)$")
    price_paid_usd: Decimal
    expires_at: datetime
    nameserver_mode: NameserverMode
    cloudflare_zone_id: Optional[str] = None
    order_id: str
    registration_date: datetime
    
    @field_validator('price_paid_usd')
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('Price must be positive')
        return v.quantize(Decimal('0.01'))

# =============================================================================
# 2. DNS MANAGEMENT VALIDATION SCHEMAS
# =============================================================================

class DNSRecordType(str, Enum):
    """Supported DNS Record Types"""
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    SRV = "SRV"

class DNSRecordRequest(BaseModel):
    """DNS Record Creation/Update Validation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    record_type: DNSRecordType
    name: str = Field(..., max_length=255)
    content: str = Field(..., max_length=65535)
    ttl: int = Field(default=300, ge=60, le=86400)
    priority: Optional[int] = Field(default=None, ge=0, le=65535)
    
    @field_validator('content')
    @classmethod
    def validate_content_by_type(cls, v: str, info) -> str:
        """Validate content based on record type"""
        if 'record_type' not in info.data:
            return v
            
        record_type = info.data['record_type']
        
        if record_type == DNSRecordType.A:
            # IPv4 validation
            ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            if not re.match(ipv4_pattern, v):
                raise ValueError('A record must contain valid IPv4 address')
                
        elif record_type == DNSRecordType.AAAA:
            # IPv6 validation (simplified)
            if ':' not in v or len(v) < 3:
                raise ValueError('AAAA record must contain valid IPv6 address')
                
        elif record_type == DNSRecordType.CNAME:
            # FQDN validation
            if not v.endswith('.'):
                v = v + '.'
            if not re.match(r'^[a-zA-Z0-9.-]+\.$', v):
                raise ValueError('CNAME must be valid FQDN')
                
        elif record_type == DNSRecordType.MX:
            # MX format validation
            if not re.match(r'^[a-zA-Z0-9.-]+\.?$', v):
                raise ValueError('MX record must contain valid hostname')
                
        return v
    
    @field_validator('priority')
    @classmethod
    def validate_priority_for_mx(cls, v: Optional[int], info) -> Optional[int]:
        """MX records require priority"""
        if 'record_type' in info.data and info.data['record_type'] == DNSRecordType.MX:
            if v is None:
                raise ValueError('MX records require priority value')
        return v

class GeoBlockingRequest(BaseModel):
    """Geographic Access Control Validation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    action: str = Field(..., pattern="^(allow|block|challenge)$")
    countries: List[str] = Field(
        ..., 
        min_items=1,
        description="ISO 3166-1 alpha-2 country codes"
    )
    rule_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    
    @field_validator('countries')
    @classmethod
    def validate_country_codes(cls, v: List[str]) -> List[str]:
        """Validate ISO country codes"""
        # Common country codes (partial list for example)
        valid_codes = {
            'US', 'CA', 'GB', 'FR', 'DE', 'IT', 'ES', 'NL', 'SE', 'NO',
            'CN', 'RU', 'JP', 'KR', 'IN', 'AU', 'BR', 'MX', 'AR', 'CL'
        }
        
        invalid_codes = []
        for code in v:
            if code.upper() not in valid_codes:
                invalid_codes.append(code)
        
        if invalid_codes:
            raise ValueError(f'Invalid country codes: {invalid_codes}')
            
        return [code.upper() for code in v]

# =============================================================================
# 3. PAYMENT PROCESSING VALIDATION SCHEMAS
# =============================================================================

class CryptoCurrency(str, Enum):
    """Supported Cryptocurrencies"""
    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    DOGE = "DOGE"
    TRON = "TRON"
    BCH = "BCH"

class PaymentInitiationRequest(BaseModel):
    """Cryptocurrency Payment Request Validation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    amount_usd: Decimal = Field(
        ..., 
        gt=0,
        description="Payment amount in USD"
    )
    cryptocurrency: CryptoCurrency = Field(
        ...,
        description="Selected cryptocurrency"
    )
    order_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r'^ORD-[A-Z0-9]+$',
        description="Order identifier (format: ORD-XXXXX)"
    )
    callback_url: Optional[str] = Field(
        default=None,
        description="Webhook URL for payment notifications"
    )
    
    @field_validator('amount_usd')
    @classmethod
    def validate_payment_amount(cls, v: Decimal) -> Decimal:
        """Validate payment amount ranges"""
        if v < Decimal('0.01'):
            raise ValueError('Minimum payment amount is $0.01')
        if v > Decimal('10000.00'):
            raise ValueError('Maximum payment amount is $10,000.00')
        return v.quantize(Decimal('0.01'))

class PaymentStatusResponse(BaseModel):
    """Payment Status Output Validation"""
    model_config = ConfigDict(from_attributes=True)
    
    payment_id: str
    status: str = Field(..., pattern="^(pending|confirmed|expired|failed)$")
    crypto_address: str
    amount_usd: Decimal
    amount_crypto: Decimal
    cryptocurrency: CryptoCurrency
    confirmations: int = Field(ge=0)
    required_confirmations: int = Field(ge=1)
    qr_code_data: str
    expires_at: datetime
    created_at: datetime
    confirmed_at: Optional[datetime] = None

# =============================================================================
# 4. USER MANAGEMENT VALIDATION SCHEMAS
# =============================================================================

class LanguageCode(str, Enum):
    """Supported Languages"""
    ENGLISH = "en"
    FRENCH = "fr"
    HINDI = "hi"
    CHINESE = "zh"
    SPANISH = "es"

class UserRegistrationRequest(BaseModel):
    """User Registration Input Validation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    telegram_id: int = Field(..., gt=0)
    username: Optional[str] = Field(default=None, max_length=32)
    first_name: Optional[str] = Field(default=None, max_length=64)
    last_name: Optional[str] = Field(default=None, max_length=64)
    language: LanguageCode = Field(default=LanguageCode.ENGLISH)
    initial_balance: Optional[Decimal] = Field(
        default=None,
        ge=0
    )
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate Telegram username format"""
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$', v):
            raise ValueError('Username must start with letter, 5-32 chars, alphanumeric + underscore only')
        return v

class UserDashboardResponse(BaseModel):
    """User Dashboard Data Validation"""
    model_config = ConfigDict(from_attributes=True)
    
    user_info: Dict[str, Any]
    wallet_balance: Decimal
    total_domains: int = Field(ge=0)
    active_orders: int = Field(ge=0)
    recent_transactions: List[Dict[str, Any]]
    expiring_domains: List[Dict[str, Any]]
    loyalty_tier: str
    
    @field_validator('wallet_balance')
    @classmethod
    def validate_balance(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal('0.01'))

# =============================================================================
# 5. COMPREHENSIVE VALIDATION EXAMPLES
# =============================================================================

def demonstrate_validation_patterns():
    """
    Comprehensive examples of validation layer usage
    """
    
    print("🎯 VALIDATION LAYER IMPLEMENTATION EXAMPLES")
    print("=" * 60)
    
    # Example 1: Domain Registration Validation
    print("\n📌 Example 1: Domain Registration Validation")
    print("-" * 40)
    
    try:
        # Valid request
        domain_request = DomainRegistrationRequest(
            domain_name="mycompany",
            tld=SupportedTLD.COM,
            nameserver_mode=NameserverMode.CLOUDFLARE,
            contact_email="admin@example.com",
            registration_years=2,
            auto_renew=True
        )
        
        print(f"✅ Valid domain request:")
        print(f"   Full domain: {domain_request.full_domain}")
        print(f"   Offshore price: ${domain_request.offshore_price_usd}")
        print(f"   Nameserver mode: {domain_request.nameserver_mode}")
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
    
    # Example 2: Invalid Domain Validation
    print("\n📌 Example 2: Invalid Domain Validation")
    print("-" * 40)
    
    try:
        # Invalid request (should fail)
        invalid_domain = DomainRegistrationRequest(
            domain_name="-invalid-domain-",  # Invalid format
            tld=SupportedTLD.COM
        )
    except Exception as e:
        print(f"✅ Caught invalid domain: {e}")
    
    # Example 3: DNS Record Validation
    print("\n📌 Example 3: DNS Record Validation")
    print("-" * 40)
    
    try:
        # Valid A record
        dns_record = DNSRecordRequest(
            record_type=DNSRecordType.A,
            name="www",
            content="192.168.1.1",
            ttl=3600
        )
        print(f"✅ Valid A record: {dns_record.name} -> {dns_record.content}")
        
        # Valid MX record  
        mx_record = DNSRecordRequest(
            record_type=DNSRecordType.MX,
            name="@",
            content="mail.example.com",
            priority=10,
            ttl=3600
        )
        print(f"✅ Valid MX record: priority {mx_record.priority}")
        
    except Exception as e:
        print(f"❌ DNS validation error: {e}")
    
    # Example 4: Payment Validation
    print("\n📌 Example 4: Payment Validation")
    print("-" * 40)
    
    try:
        payment_request = PaymentInitiationRequest(
            amount_usd=Decimal("49.50"),
            cryptocurrency=CryptoCurrency.BTC,
            order_id="ORD-DOM123",
            callback_url="https://api.nomadly.offshore/webhook"
        )
        print(f"✅ Valid payment: ${payment_request.amount_usd} {payment_request.cryptocurrency}")
        
    except Exception as e:
        print(f"❌ Payment validation error: {e}")
    
    # Example 5: Geo-blocking Validation
    print("\n📌 Example 5: Geo-blocking Validation")
    print("-" * 40)
    
    try:
        geo_blocking = GeoBlockingRequest(
            action="block",
            countries=["CN", "RU", "KP"],
            rule_name="Block High-Risk Countries",
            description="Block access from high-risk jurisdictions"
        )
        print(f"✅ Valid geo-blocking: {geo_blocking.action} {geo_blocking.countries}")
        
    except Exception as e:
        print(f"❌ Geo-blocking validation error: {e}")
    
    print(f"\n🎉 Validation Layer Implementation Complete!")
    print("📋 Features implemented:")
    print("   • Domain format validation with TLD enforcement")
    print("   • DNS record type-specific content validation")
    print("   • Payment amount and cryptocurrency validation")
    print("   • Geographic access control validation")
    print("   • User registration with Telegram ID validation")
    print("   • Comprehensive error handling and feedback")
    print("   • Business rule enforcement (pricing, limits)")
    print("   • Type conversion and sanitization")

if __name__ == "__main__":
    demonstrate_validation_patterns()