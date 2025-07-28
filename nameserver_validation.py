#!/usr/bin/env python3
"""
Nameserver Input Validation System
Comprehensive validation for custom nameserver inputs to prevent API failures
"""

import re
from typing import List, Tuple, Dict

class NameserverValidator:
    """Comprehensive nameserver validation with error correction"""
    
    # Common typo corrections
    TYPO_CORRECTIONS = {
        'pribatehoster.cc': 'privatehoster.cc',
        'privathoster.cc': 'privatehoster.cc',
        'ns1.pribatehoster.cc': 'ns1.privatehoster.cc',
        'ns2.pribatehoster.cc': 'ns2.privatehoster.cc',
        'cloudflare.con': 'cloudflare.com',
        'ns1.cloudflare.con': 'ns1.cloudflare.com',
        'ns2.cloudflare.con': 'ns2.cloudflare.com',
        'nameserver1': None,  # Invalid format
        'nameserver2': None,  # Invalid format
    }
    
    @staticmethod
    def validate_hostname(hostname: str) -> Tuple[bool, str]:
        """
        Validate a single hostname according to RFC standards
        Returns: (is_valid, error_message)
        """
        if not hostname:
            return False, "Hostname cannot be empty"
        
        hostname = hostname.strip()
        
        # Length check (RFC 1035)
        if len(hostname) > 253:
            return False, f"Hostname too long (max 253 characters, got {len(hostname)})"
        
        if len(hostname) < 1:
            return False, "Hostname too short"
        
        # RFC compliant hostname pattern
        # Allows letters, numbers, hyphens. Must start/end with alphanumeric
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        
        if not re.match(hostname_pattern, hostname):
            return False, f"Invalid hostname format: {hostname}"
        
        # Check for consecutive dots
        if '..' in hostname:
            return False, f"Invalid hostname - consecutive dots not allowed: {hostname}"
        
        # Must have at least one dot (be a FQDN)
        if '.' not in hostname:
            return False, f"Nameserver must be fully qualified (include domain): {hostname}"
        
        return True, "Valid hostname"
    
    @staticmethod
    def check_for_typos(hostname: str) -> Tuple[bool, str, str]:
        """
        Check for common typos and suggest corrections
        Returns: (has_typo, suggestion, original)
        """
        hostname = hostname.strip().lower()
        
        if hostname in NameserverValidator.TYPO_CORRECTIONS:
            suggestion = NameserverValidator.TYPO_CORRECTIONS[hostname]
            if suggestion:
                return True, suggestion, hostname
            else:
                return True, f"'{hostname}' is not a valid nameserver format", hostname
        
        return False, hostname, hostname
    
    @staticmethod
    def validate_nameserver_list(nameservers: List[str]) -> Tuple[bool, List[str], str]:
        """
        Validate a list of nameservers with typo checking and corrections
        Returns: (is_valid, corrected_list, error_message)
        """
        if not nameservers:
            return False, [], "No nameservers provided"
        
        # Filter out empty entries
        nameservers = [ns.strip() for ns in nameservers if ns.strip()]
        
        if len(nameservers) < 2:
            return False, nameservers, "At least 2 nameservers required (RFC requirement)"
        
        if len(nameservers) > 4:
            return False, nameservers, "Maximum 4 nameservers allowed per domain"
        
        corrected_nameservers = []
        corrections_made = []
        
        for ns in nameservers:
            # Check for typos first
            has_typo, suggestion, original = NameserverValidator.check_for_typos(ns)
            
            if has_typo and suggestion and suggestion != original:
                # Found a typo with suggestion
                corrections_made.append(f"'{original}' → '{suggestion}'")
                ns_to_validate = suggestion
            elif has_typo and not suggestion:
                # Found invalid format
                return False, nameservers, f"Invalid nameserver format: {original}"
            else:
                ns_to_validate = ns
            
            # Validate the hostname
            is_valid, error_msg = NameserverValidator.validate_hostname(ns_to_validate)
            if not is_valid:
                return False, nameservers, f"Invalid nameserver '{ns_to_validate}': {error_msg}"
            
            corrected_nameservers.append(ns_to_validate)
        
        # Check for duplicates
        if len(set(corrected_nameservers)) != len(corrected_nameservers):
            return False, corrected_nameservers, "Duplicate nameservers are not allowed"
        
        # Success message with corrections if any
        if corrections_made:
            correction_msg = f"Validated with corrections: {', '.join(corrections_made)}"
        else:
            correction_msg = f"All {len(corrected_nameservers)} nameservers validated successfully"
        
        return True, corrected_nameservers, correction_msg
    
    @staticmethod
    def format_validation_result(is_valid: bool, nameservers: List[str], message: str) -> Dict:
        """Format validation result for bot responses"""
        return {
            'valid': is_valid,
            'nameservers': nameservers,
            'message': message,
            'count': len(nameservers)
        }

def test_validation():
    """Test the validation system"""
    print("🧪 TESTING NAMESERVER VALIDATION SYSTEM")
    print("=" * 50)
    
    test_cases = [
        # Valid cases
        ["ns1.privatehoster.cc", "ns2.privatehoster.cc"],
        ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"],
        
        # Typo cases (from your testing)
        ["ns1.privatehoster.cc", "ns2.pribatehoster.cc"],  # The actual typo you encountered
        
        # Edge cases
        [],  # Empty
        ["ns1.example.com"],  # Too few
        ["ns1.example.com", "ns2.example.com", "ns3.example.com", "ns4.example.com", "ns5.example.com"],  # Too many
        ["invalid", "also.invalid"],  # Invalid format
        ["ns1.example.com", "ns1.example.com"],  # Duplicates
    ]
    
    validator = NameserverValidator()
    
    for i, test_ns in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_ns}")
        valid, corrected, message = validator.validate_nameserver_list(test_ns)
        result = validator.format_validation_result(valid, corrected, message)
        
        status = "✅ VALID" if valid else "❌ INVALID"
        print(f"Result: {status}")
        print(f"Message: {message}")
        if corrected != test_ns:
            print(f"Corrected: {corrected}")

if __name__ == "__main__":
    test_validation()