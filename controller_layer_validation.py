#!/usr/bin/env python3
"""
Controller/Handler Layer Architecture Validation
Validates proper implementation of Controller layer patterns
"""

import os
import inspect
from pathlib import Path
from typing import Dict, List, Any

def validate_controller_architecture():
    """Validate Controller/Handler layer implementation"""
    
    print("🎯 Controller/Handler Layer Architecture Validation")
    print("=" * 60)
    
    controllers_dir = Path("app/controllers")
    if not controllers_dir.exists():
        print("❌ Controllers directory missing")
        return False
    
    validation_results = {
        "base_controller": validate_base_controller(),
        "domain_controller": validate_domain_controller(),
        "dns_controller": validate_dns_controller(),
        "payment_controller": validate_payment_controller(),
        "user_controller": validate_user_controller(),
        "nameserver_controller": validate_nameserver_controller(),
        "controller_patterns": validate_controller_patterns()
    }
    
    # Summary
    passed = sum(1 for result in validation_results.values() if result)
    total = len(validation_results)
    
    print(f"\n📊 CONTROLLER LAYER VALIDATION SUMMARY")
    print("=" * 60)
    
    for component, result in validation_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {component.replace('_', ' ').title()}")
    
    print(f"\nOverall Controller Architecture: {passed}/{total} components validated ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Controller/Handler layer architecture fully compliant!")
        return True
    else:
        print("⚠️ Some controller components need attention")
        return False

def validate_base_controller():
    """Validate BaseController implementation"""
    print("\n🔍 Base Controller Validation")
    print("-" * 40)
    
    base_controller_path = Path("app/controllers/base_controller.py")
    if not base_controller_path.exists():
        print("❌ BaseController missing")
        return False
    
    # Check for required methods
    required_methods = [
        'success_response',
        'error_response', 
        'paginated_response',
        'validate_input',
        'handle_service_error',
        'map_domain_to_dto'
    ]
    
    try:
        with open(base_controller_path, 'r') as f:
            content = f.read()
        
        missing_methods = []
        for method in required_methods:
            if f"def {method}" not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing methods: {missing_methods}")
            return False
        
        print("✅ BaseController has all required methods")
        return True
        
    except Exception as e:
        print(f"❌ Error validating BaseController: {e}")
        return False

def validate_domain_controller():
    """Validate DomainController implementation"""
    print("\n🔍 Domain Controller Validation")
    print("-" * 40)
    
    controller_path = Path("app/controllers/domain_controller.py")
    if not controller_path.exists():
        print("❌ DomainController missing")
        return False
    
    # Check for required controller methods
    required_methods = [
        'check_domain_availability',
        'register_domain',
        'get_user_domains',
        'get_domain_details',
        'update_domain_settings'
    ]
    
    return validate_controller_methods(controller_path, "DomainController", required_methods)

def validate_dns_controller():
    """Validate DNSController implementation"""
    print("\n🔍 DNS Controller Validation")
    print("-" * 40)
    
    controller_path = Path("app/controllers/dns_controller.py")
    if not controller_path.exists():
        print("❌ DNSController missing")
        return False
    
    required_methods = [
        'create_dns_record',
        'get_domain_dns_records',
        'update_dns_record',
        'delete_dns_record',
        'configure_geo_blocking',
        'sync_cloudflare_records'
    ]
    
    return validate_controller_methods(controller_path, "DNSController", required_methods)

def validate_payment_controller():
    """Validate PaymentController implementation"""
    print("\n🔍 Payment Controller Validation")
    print("-" * 40)
    
    controller_path = Path("app/controllers/payment_controller.py")
    if not controller_path.exists():
        print("❌ PaymentController missing")
        return False
    
    required_methods = [
        'initiate_crypto_payment',
        'get_payment_status',
        'confirm_payment',
        'get_user_payment_history',
        'process_overpayment'
    ]
    
    return validate_controller_methods(controller_path, "PaymentController", required_methods)

def validate_user_controller():
    """Validate UserController implementation"""
    print("\n🔍 User Controller Validation")
    print("-" * 40)
    
    controller_path = Path("app/controllers/user_controller.py")
    if not controller_path.exists():
        print("❌ UserController missing")
        return False
    
    required_methods = [
        'register_user',
        'get_user_profile',
        'update_user_profile',
        'update_user_language',
        'get_user_dashboard_data'
    ]
    
    return validate_controller_methods(controller_path, "UserController", required_methods)

def validate_nameserver_controller():
    """Validate NameserverController implementation"""
    print("\n🔍 Nameserver Controller Validation")
    print("-" * 40)
    
    controller_path = Path("app/controllers/nameserver_controller.py")
    if not controller_path.exists():
        print("❌ NameserverController missing")
        return False
    
    required_methods = [
        'get_domain_nameservers',
        'update_domain_nameservers',
        'set_nameserver_preset',
        'get_nameserver_presets',
        'get_propagation_status'
    ]
    
    return validate_controller_methods(controller_path, "NameserverController", required_methods)

def validate_controller_methods(controller_path: Path, controller_name: str, required_methods: List[str]) -> bool:
    """Validate controller has required methods with proper patterns"""
    try:
        with open(controller_path, 'r') as f:
            content = f.read()
        
        missing_methods = []
        pattern_issues = []
        
        for method in required_methods:
            if f"async def {method}" not in content:
                missing_methods.append(method)
            else:
                # Check for controller patterns
                method_content = extract_method_content(content, method)
                if method_content:
                    issues = validate_method_patterns(method, method_content)
                    pattern_issues.extend(issues)
        
        if missing_methods:
            print(f"❌ Missing methods in {controller_name}: {missing_methods}")
            return False
        
        if pattern_issues:
            print(f"⚠️ Pattern issues in {controller_name}:")
            for issue in pattern_issues[:3]:  # Show first 3 issues
                print(f"    - {issue}")
            return False
        
        print(f"✅ {controller_name} has all required methods with proper patterns")
        return True
        
    except Exception as e:
        print(f"❌ Error validating {controller_name}: {e}")
        return False

def extract_method_content(file_content: str, method_name: str) -> str:
    """Extract method content for pattern validation"""
    lines = file_content.split('\n')
    method_lines = []
    in_method = False
    indent_level = 0
    
    for line in lines:
        if f"async def {method_name}" in line:
            in_method = True
            indent_level = len(line) - len(line.lstrip())
            method_lines.append(line)
        elif in_method:
            if line.strip() == "":
                method_lines.append(line)
            elif len(line) - len(line.lstrip()) <= indent_level and line.strip():
                # End of method
                break
            else:
                method_lines.append(line)
    
    return '\n'.join(method_lines)

def validate_method_patterns(method_name: str, method_content: str) -> List[str]:
    """Validate controller method follows proper patterns"""
    issues = []
    
    # Check for input validation (allow manual validation or BaseController method)
    if "validate_input" not in method_content and "Validate input" not in method_content and "if not" not in method_content:
        issues.append(f"{method_name}: Missing input validation")
    
    # Check for service calls
    if "await" not in method_content:
        issues.append(f"{method_name}: Missing async service calls")
    
    # Check for DTO mapping
    if "_dto" not in method_content and "map_domain_to_dto" not in method_content:
        issues.append(f"{method_name}: Missing DTO mapping")
    
    # Check for response formatting
    if "success_response" not in method_content:
        issues.append(f"{method_name}: Missing success response formatting")
    
    # Check for error handling
    if "handle_service_error" not in method_content:
        issues.append(f"{method_name}: Missing proper error handling")
    
    return issues

def validate_controller_patterns():
    """Validate overall controller architecture patterns"""
    print("\n🔍 Controller Architecture Patterns Validation")
    print("-" * 40)
    
    patterns_valid = True
    
    # Check controller inheritance
    controllers_dir = Path("app/controllers")
    controller_files = [f for f in controllers_dir.glob("*_controller.py") if f.name != "base_controller.py"]
    
    for controller_file in controller_files:
        try:
            with open(controller_file, 'r') as f:
                content = f.read()
            
            # Check inheritance from BaseController
            if "BaseController" not in content:
                print(f"⚠️ {controller_file.name}: Not inheriting from BaseController")
                patterns_valid = False
            
            # Check dependency injection in __init__
            if "__init__(self," not in content:
                print(f"⚠️ {controller_file.name}: Missing dependency injection constructor")
                patterns_valid = False
            
        except Exception as e:
            print(f"❌ Error checking {controller_file.name}: {e}")
            patterns_valid = False
    
    if patterns_valid:
        print("✅ All controllers follow proper architecture patterns")
    
    return patterns_valid

def generate_controller_usage_examples():
    """Generate usage examples for controllers"""
    print("\n📋 Controller Usage Examples")
    print("-" * 40)
    
    examples = {
        "Domain Registration Flow": """
# UI Input → Controller → Service → Repository → Database
domain_controller = DomainController(domain_service, user_service)

# 1. Receive input from UI
request = DomainRegistrationRequest(
    domain_name="example.com",
    price_usd=49.50,
    registration_years=1
)

# 2. Controller handles validation and coordination
result = await domain_controller.register_domain(request, telegram_id=12345)

# 3. Response formatted as DTO
{
    "success": True,
    "data": {
        "domain_id": 123,
        "domain_name": "example.com",
        "status": "registered",
        "expires_at": "2026-01-23T15:30:00",
        "order_id": "ORD-456"
    },
    "message": "Domain example.com registered successfully"
}
""",
        
        "DNS Management Flow": """
# DNS Record Creation
dns_controller = DNSController(dns_service, domain_service)

# 1. Input validation and ownership check
request = DNSRecordRequest(
    record_type="A",
    name="www",
    content="192.168.1.1",
    ttl=300
)

# 2. Controller coordinates DNS service and Cloudflare sync  
result = await dns_controller.create_dns_record(domain_id=123, request=request, telegram_id=12345)

# 3. DTO response with sync status
{
    "success": True,
    "data": {
        "id": 789,
        "record_type": "A",
        "name": "www",
        "content": "192.168.1.1",
        "cloudflare_id": "cf_abc123",
        "status": "active"
    }
}
""",
        
        "Payment Processing Flow": """
# Crypto Payment Initiation
payment_controller = PaymentController(payment_service, wallet_service, user_service)

# 1. Input validation and user verification
request = PaymentInitiationRequest(
    amount_usd=49.50,
    cryptocurrency="BTC",
    order_id="ORD-456"
)

# 2. Controller coordinates payment address generation
result = await payment_controller.initiate_crypto_payment(request, telegram_id=12345)

# 3. DTO with payment details
{
    "success": True,
    "data": {
        "payment_id": "PAY-789",
        "crypto_address": "bc1q...",
        "amount_crypto": 0.001234,
        "qr_code_data": "bitcoin:bc1q...?amount=0.001234",
        "expires_at": "2025-01-24T15:30:00"
    }
}
"""
    }
    
    for title, example in examples.items():
        print(f"\n📌 {title}")
        print(example)

if __name__ == "__main__":
    success = validate_controller_architecture()
    
    if success:
        generate_controller_usage_examples()
        print("\n🎉 Controller/Handler Layer Architecture Validation Complete!")
        print("📋 All controllers properly implement:")
        print("   • UI input handling and validation")
        print("   • Service layer coordination")
        print("   • DTO mapping and response formatting")
        print("   • Comprehensive error handling")
        print("   • Clean separation of concerns")
    else:
        print("\n⚠️ Controller layer needs attention before production deployment")