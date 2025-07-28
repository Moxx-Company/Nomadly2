#!/usr/bin/env python3
"""
Enhanced Validation System - Comprehensive Input Validation with Auto-Correction
"""

import re
import asyncio
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of validation with correction suggestions"""
    is_valid: bool
    corrected_value: Optional[str] = None
    error_message: Optional[str] = None
    suggestions: List[str] = None
    
    def get(self, key: str, default=None):
        """Dict-like access for backward compatibility"""
        return getattr(self, key, default)

class EnhancedValidator:
    """Comprehensive validation system with auto-correction"""
    
    def __init__(self):
        self.common_typos = {
            # Nameserver typos
            'pribatehoster': 'privatehoster',
            'prviatehoster': 'privatehoster', 
            'privatehoster': 'privatehoster',
            'ns1.cloudflare': 'ns1.cloudflare.com',
            'ns2.cloudflare': 'ns2.cloudflare.com',
            'cloudfare': 'cloudflare',
            'cloudflar': 'cloudflare',
            
            # Domain typos
            'exampl.com': 'example.com',
            'gooogle': 'google',
            'yahooo': 'yahoo',
            'gmial': 'gmail',
            
            # Common DNS record typos
            'wwww': 'www',
            'maail': 'mail',
            'ftp1': 'ftp',
        }
        
        self.domain_patterns = {
            'valid': r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z]{2,}(\.[a-zA-Z]{2,})*)$',
            'invalid_chars': r'[^a-zA-Z0-9.-]',
            'double_dots': r'\.\.',
            'leading_dot': r'^\.',
            'trailing_dot': r'\.$'
        }
        
        self.nameserver_patterns = {
            'valid': r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z]{2,}(\.[a-zA-Z]{2,})*)$',
            'max_length': 253
        }
        
        self.email_patterns = {
            'valid': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'invalid_start': r'^@',
            'invalid_end': r'@$',
            'double_at': r'@@'
        }
    
    def auto_correct_typos(self, text: str) -> str:
        """Auto-correct common typos"""
        corrected = text.lower()
        
        for typo, correction in self.common_typos.items():
            if typo in corrected:
                corrected = corrected.replace(typo, correction)
        
        return corrected if corrected != text.lower() else text
    
    def validate_domain(self, domain: str) -> ValidationResult:
        """Validate domain name with auto-correction"""
        if not domain:
            return ValidationResult(False, error_message="Domain cannot be empty")
        
        # Auto-correct typos
        corrected_domain = self.auto_correct_typos(domain.strip())
        
        # Remove leading/trailing dots
        if corrected_domain.startswith('.'):
            corrected_domain = corrected_domain[1:]
        if corrected_domain.endswith('.') and not corrected_domain.endswith('..'):
            corrected_domain = corrected_domain[:-1]
        
        # Check for invalid characters
        if re.search(self.domain_patterns['invalid_chars'], corrected_domain):
            return ValidationResult(
                False, 
                error_message="Domain contains invalid characters. Only letters, numbers, dots, and hyphens allowed."
            )
        
        # Check for double dots
        if re.search(self.domain_patterns['double_dots'], corrected_domain):
            return ValidationResult(
                False,
                corrected_value=corrected_domain.replace('..', '.'),
                error_message="Domain contains consecutive dots"
            )
        
        # Validate format
        if not re.match(self.domain_patterns['valid'], corrected_domain):
            suggestions = []
            if '.' not in corrected_domain:
                suggestions.append(f"{corrected_domain}.com")
                suggestions.append(f"{corrected_domain}.org")
            
            return ValidationResult(
                False,
                error_message="Invalid domain format. Domain must be like 'example.com'",
                suggestions=suggestions
            )
        
        # Domain length check
        if len(corrected_domain) > 253:
            return ValidationResult(
                False,
                error_message="Domain too long (maximum 253 characters)"
            )
        
        # Check if correction was made
        if corrected_domain != domain:
            return ValidationResult(
                True,
                corrected_value=corrected_domain
            )
        
        return ValidationResult(True)
    
    def validate_nameserver(self, nameserver: str) -> ValidationResult:
        """Validate nameserver with auto-correction"""
        if not nameserver:
            return ValidationResult(False, error_message="Nameserver cannot be empty")
        
        # Auto-correct typos
        corrected_ns = self.auto_correct_typos(nameserver.strip().lower())
        
        # Auto-complete common nameservers
        if corrected_ns.startswith('ns1.') and not corrected_ns.endswith('.com'):
            if 'cloudflare' in corrected_ns and not corrected_ns.endswith('.com'):
                corrected_ns += '.com'
        
        # Length check
        if len(corrected_ns) > self.nameserver_patterns['max_length']:
            return ValidationResult(
                False,
                error_message=f"Nameserver too long (maximum {self.nameserver_patterns['max_length']} characters)"
            )
        
        # Format validation
        if not re.match(self.nameserver_patterns['valid'], corrected_ns):
            return ValidationResult(
                False,
                error_message="Invalid nameserver format. Must be like 'ns1.example.com'"
            )
        
        # Check if correction was made
        if corrected_ns != nameserver.lower():
            return ValidationResult(
                True,
                corrected_value=corrected_ns
            )
        
        return ValidationResult(True)
    
    def validate_nameserver_list(self, nameservers: List[str]) -> ValidationResult:
        """Validate list of nameservers"""
        if not nameservers:
            return ValidationResult(False, error_message="At least one nameserver required")
        
        if len(nameservers) < 2:
            return ValidationResult(False, error_message="At least 2 nameservers required")
        
        if len(nameservers) > 4:
            return ValidationResult(False, error_message="Maximum 4 nameservers allowed")
        
        corrected_nameservers = []
        errors = []
        
        for i, ns in enumerate(nameservers):
            result = self.validate_nameserver(ns)
            if not result.is_valid:
                errors.append(f"Nameserver {i+1}: {result.error_message}")
            else:
                corrected_nameservers.append(result.corrected_value or ns)
        
        if errors:
            return ValidationResult(
                False,
                error_message="\n".join(errors)
            )
        
        # Check if any corrections were made
        if corrected_nameservers != nameservers:
            return ValidationResult(
                True,
                corrected_value=corrected_nameservers
            )
        
        return ValidationResult(True)
    
    def validate_email(self, email: str) -> ValidationResult:
        """Validate email with auto-correction"""
        if not email:
            return ValidationResult(False, error_message="Email cannot be empty")
        
        email = email.strip().lower()
        
        # Fix common email issues
        if email.startswith('@'):
            return ValidationResult(
                False,
                error_message="Email cannot start with @",
                suggestions=[f"user{email}", f"contact{email}"]
            )
        
        if email.endswith('@'):
            return ValidationResult(
                False, 
                error_message="Email cannot end with @",
                suggestions=[f"{email}domain.com", f"{email}example.com"]
            )
        
        if '@@' in email:
            corrected_email = email.replace('@@', '@')
            return ValidationResult(
                True,
                corrected_value=corrected_email
            )
        
        # Standard email validation
        if not re.match(self.email_patterns['valid'], email):
            return ValidationResult(
                False,
                error_message="Invalid email format. Must be like 'user@domain.com'"
            )
        
        return ValidationResult(True)
    
    def validate_dns_record_value(self, record_type: str, value: str) -> ValidationResult:
        """Validate DNS record values"""
        if not value:
            return ValidationResult(False, error_message=f"{record_type} record value cannot be empty")
        
        value = value.strip()
        
        if record_type.upper() == 'A':
            # IPv4 validation
            ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            if not re.match(ipv4_pattern, value):
                return ValidationResult(
                    False,
                    error_message="Invalid IPv4 address format. Must be like '192.168.1.1'"
                )
        
        elif record_type.upper() == 'CNAME':
            # Domain validation for CNAME
            return self.validate_domain(value)
        
        elif record_type.upper() == 'MX':
            # MX record validation (priority + domain)
            if ' ' not in value:
                return ValidationResult(
                    False,
                    corrected_value=f"10 {value}",
                    error_message="MX record must include priority. Example: '10 mail.example.com'"
                )
            
            parts = value.split(' ', 1)
            try:
                priority = int(parts[0])
                domain_result = self.validate_domain(parts[1])
                if not domain_result.is_valid:
                    return domain_result
            except ValueError:
                return ValidationResult(
                    False,
                    error_message="MX record priority must be a number. Example: '10 mail.example.com'"
                )
        
        elif record_type.upper() == 'TXT':
            # TXT record validation (allow most content)
            if len(value) > 255:
                return ValidationResult(
                    False,
                    error_message="TXT record too long (maximum 255 characters)"
                )
        
        return ValidationResult(True)
    
    async def validate_user_input(self, input_type: str, value: str) -> ValidationResult:
        """General user input validation router"""
        if input_type == 'domain':
            return self.validate_domain(value)
        elif input_type == 'nameserver':
            return self.validate_nameserver(value)
        elif input_type == 'email':
            return self.validate_email(value)
        elif input_type.startswith('dns_'):
            record_type = input_type.replace('dns_', '').upper()
            return self.validate_dns_record_value(record_type, value)
        else:
            return ValidationResult(True)  # Unknown type, pass through
    
    def validate_domain_name(self, domain_name: str) -> Dict[str, Any]:
        """Validate domain name with suggestions (dict format for testing)"""
        result = self.validate_domain(domain_name)
        return {
            'is_valid': result.is_valid,
            'errors': [result.error_message] if result.error_message else [],
            'suggestions': result.suggestions or [],
            'warnings': []
        }
    
    def validate_callback_data(self, callback_data: str) -> Dict[str, Any]:
        """Validate callback data (dict format for testing)"""
        if not callback_data or not isinstance(callback_data, str):
            return {
                'is_valid': False,
                'errors': ['Callback data is required'],
                'suggestions': [],
                'warnings': []
            }
        
        # Basic sanitization checks
        if '<' in callback_data or '>' in callback_data or 'script' in callback_data.lower():
            return {
                'is_valid': False,
                'errors': ['Callback data contains invalid characters'],
                'suggestions': ['Use only alphanumeric characters and underscores'],
                'warnings': []
            }
        
        return {
            'is_valid': True,
            'errors': [],
            'suggestions': [],
            'warnings': []
        }

# Integration with bot
def format_validation_message(result: ValidationResult) -> str:
    """Format validation result for user display"""
    if result.is_valid and result.corrected_value:
        return f"✅ Auto-corrected: {result.corrected_value}"
    elif not result.is_valid:
        message = f"❌ {result.error_message}"
        if result.corrected_value:
            message += f"\n💡 Suggestion: {result.corrected_value}"
        elif result.suggestions:
            message += f"\n💡 Suggestions: {', '.join(result.suggestions)}"
        return message
    else:
        return "✅ Valid"

async def test_enhanced_validation():
    """Test the enhanced validation system"""
    print("🧪 TESTING ENHANCED VALIDATION SYSTEM")
    print("=" * 50)
    
    validator = EnhancedValidator()
    
    # Test cases
    test_cases = [
        ('domain', 'exampl.com'),
        ('domain', 'google.com'),
        ('domain', '.example.com'),
        ('nameserver', 'ns1.pribatehoster.cc'),
        ('nameserver', 'ns1.cloudflare'),
        ('email', '@domain.com'),
        ('email', 'user@@domain.com'),
        ('email', 'valid@example.com'),
        ('dns_A', '192.168.1.1'),
        ('dns_A', '999.999.999.999'),
    ]
    
    for input_type, test_value in test_cases:
        result = await validator.validate_user_input(input_type, test_value)
        message = format_validation_message(result)
        print(f"{input_type:12} '{test_value:20}' → {message}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_validation())