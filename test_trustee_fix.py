from trustee_service_manager import TrusteeServiceManager

def test_fix():
    manager = TrusteeServiceManager()    
    domain_price = 40
    total, info = manager.calculate_trustee_pricing(domain_price, "test.ca")
    
    print(f"Domain: test.ca")
    print(f"Domain Cost: ${info['domain_cost']:.2f}")
    print(f"Trustee Cost: ${info['trustee_cost']:.2f}")
    print(f"Total: ${info['total_cost']:.2f}")
    
    # Verify fix worked
    expected_trustee = 40.00  # $20 base × 2
    if abs(info['trustee_cost'] - expected_trustee) < 0.01:
        print("✅ FIX SUCCESSFUL!")
    else:
        print("❌ FIX FAILED!")

if __name__ == "__main__":
    test_fix()
