#!/usr/bin/env python3
"""
Comprehensive Validation Layer Examples for Nomadly3
Demonstrates proper Pydantic schema implementation with real use cases
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, Field
import re

# =============================================================================
# VALIDATION LAYER (SCHEMAS) IMPLEMENTATION
# =============================================================================

print("🎯 NOMADLY3 VALIDATION LAYER IMPLEMENTATION")
print("=" * 60)

# =============================================================================
# 1. DOMAIN REGISTRATION VALIDATION EXAMPLES
# =============================================================================

class SupportedTLD(str, Enum):
    """Offshore Domain TLDs with Pricing"""
    COM = ".com"
    NET = ".net" 
    ORG = ".org"
    IO = ".io"
    ME = ".me"

class DomainRegistrationRequest(BaseModel):
    """Domain Registration Input Validation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    domain_name: str = Field(..., min_length=1, max_length=63)
    tld: SupportedTLD
    nameserver_mode: str = Field(default="cloudflare", pattern="^(cloudflare|custom)$")
    contact_email: Optional[EmailStr] = None
    registration_years: int = Field(default=1, ge=1, le=10)
    
    @field_validator('domain_name')
    @classmethod
    def validate_domain_name(cls, v: str) -> str:
        """Validate domain name format"""
        v = v.lower().split('.')[0]  # Remove any TLD
        
        # RFC compliant validation
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        if not re.match(pattern, v):
            raise ValueError('Invalid domain name format')
        
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('Domain cannot start or end with hyphen')
            
        return v
    
    @property
    def full_domain(self) -> str:
        return f"{self.domain_name}{self.tld.value}"
    
    @property
    def offshore_price_usd(self) -> Decimal:
        """Calculate offshore pricing (3.3x multiplier)"""
        base_prices = {
            ".com": Decimal("15.00"),
            ".net": Decimal("18.00"),
            ".org": Decimal("16.00"),
            ".io": Decimal("45.00"),
            ".me": Decimal("25.00")
        }
        base = base_prices.get(self.tld.value, Decimal("20.00"))
        return (base * Decimal("3.3") * self.registration_years).quantize(Decimal("0.01"))

# =============================================================================
# 2. DNS RECORD VALIDATION EXAMPLES
# =============================================================================

class DNSRecordType(str, Enum):
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"

class DNSRecordRequest(BaseModel):
    """DNS Record Validation with Type-Specific Rules"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    record_type: DNSRecordType
    name: str = Field(..., max_length=255)
    content: str = Field(..., max_length=65535)
    ttl: int = Field(default=300, ge=60, le=86400)
    priority: Optional[int] = Field(default=None, ge=0, le=65535)
    
    @field_validator('content')
    @classmethod
    def validate_content_by_type(cls, v: str, info) -> str:
        """Type-specific content validation"""
        if 'record_type' not in info.data:
            return v
            
        record_type = info.data['record_type']
        
        if record_type == DNSRecordType.A:
            # IPv4 validation
            ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            if not re.match(ipv4_pattern, v):
                raise ValueError('A record must contain valid IPv4 address')
                
        elif record_type == DNSRecordType.MX:
            if not re.match(r'^[a-zA-Z0-9.-]+\.?$', v):
                raise ValueError('MX record must contain valid hostname')
                
        return v

# =============================================================================
# 3. PAYMENT PROCESSING VALIDATION EXAMPLES
# =============================================================================

class CryptoCurrency(str, Enum):
    BTC = "BTC"
    ETH = "ETH" 
    LTC = "LTC"
    DOGE = "DOGE"

class PaymentInitiationRequest(BaseModel):
    """Cryptocurrency Payment Validation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    amount_usd: Decimal = Field(..., gt=0)
    cryptocurrency: CryptoCurrency
    order_id: str = Field(..., pattern=r'^ORD-[A-Z0-9]+$')
    
    @field_validator('amount_usd')
    @classmethod
    def validate_payment_amount(cls, v: Decimal) -> Decimal:
        """Validate payment ranges"""
        if v < Decimal('0.01'):
            raise ValueError('Minimum payment amount is $0.01')
        if v > Decimal('10000.00'):
            raise ValueError('Maximum payment amount is $10,000.00')
        return v.quantize(Decimal('0.01'))

# =============================================================================
# 4. USER MANAGEMENT VALIDATION EXAMPLES  
# =============================================================================

class LanguageCode(str, Enum):
    ENGLISH = "en"
    FRENCH = "fr"

class UserRegistrationRequest(BaseModel):
    """User Registration Validation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    telegram_id: int = Field(..., gt=0)
    username: Optional[str] = Field(default=None, max_length=32)
    language: LanguageCode = Field(default=LanguageCode.ENGLISH)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Telegram username validation"""
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$', v):
            raise ValueError('Invalid username format')
        return v

# =============================================================================
# 5. COMPREHENSIVE VALIDATION EXAMPLES
# =============================================================================

def demonstrate_validation_examples():
    """Show comprehensive validation examples"""
    
    print("\n📌 Example 1: Domain Registration Validation")
    print("-" * 40)
    
    try:
        # Valid domain request
        domain_request = DomainRegistrationRequest(
            domain_name="mycompany",
            tld=SupportedTLD.COM,
            nameserver_mode="cloudflare",
            contact_email="admin@example.com",
            registration_years=2
        )
        
        print(f"✅ Valid domain request:")
        print(f"   Full domain: {domain_request.full_domain}")
        print(f"   Offshore price: ${domain_request.offshore_price_usd}")
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
    
    print("\n📌 Example 2: DNS Record Validation")
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
        
        # Try invalid A record
        try:
            invalid_dns = DNSRecordRequest(
                record_type=DNSRecordType.A,
                name="www",
                content="invalid-ip",
                ttl=3600
            )
        except Exception as e:
            print(f"✅ Caught invalid A record: {e}")
        
    except Exception as e:
        print(f"❌ DNS validation error: {e}")
    
    print("\n📌 Example 3: Payment Validation")
    print("-" * 40)
    
    try:
        payment_request = PaymentInitiationRequest(
            amount_usd=Decimal("49.50"),
            cryptocurrency=CryptoCurrency.BTC,
            order_id="ORD-DOM123"
        )
        print(f"✅ Valid payment: ${payment_request.amount_usd} {payment_request.cryptocurrency}")
        
        # Try invalid amount
        try:
            invalid_payment = PaymentInitiationRequest(
                amount_usd=Decimal("0.00"),  # Too low
                cryptocurrency=CryptoCurrency.BTC,
                order_id="ORD-DOM123"
            )
        except Exception as e:
            print(f"✅ Caught invalid payment amount: {e}")
        
    except Exception as e:
        print(f"❌ Payment validation error: {e}")
    
    print("\n📌 Example 4: User Registration Validation")
    print("-" * 40)
    
    try:
        user_request = UserRegistrationRequest(
            telegram_id=123456789,
            username="johndoe",
            language=LanguageCode.ENGLISH
        )
        print(f"✅ Valid user: {user_request.telegram_id} (@{user_request.username})")
        
        # Try invalid telegram_id
        try:
            invalid_user = UserRegistrationRequest(
                telegram_id=-1,  # Invalid
                username="johndoe"
            )
        except Exception as e:
            print(f"✅ Caught invalid telegram_id: {e}")
        
    except Exception as e:
        print(f"❌ User validation error: {e}")
    
    print(f"\n🎉 VALIDATION LAYER IMPLEMENTATION COMPLETE!")
    print("📋 Key Features Demonstrated:")
    print("   • Domain name format validation with business rules")
    print("   • DNS record type-specific content validation")
    print("   • Payment amount validation with range checking")
    print("   • User registration with Telegram ID validation")
    print("   • Enum-based validation for controlled values")
    print("   • Custom field validators with complex logic")
    print("   • Error handling with descriptive messages")
    print("   • Type conversion and data sanitization")

if __name__ == "__main__":
    demonstrate_validation_examples()