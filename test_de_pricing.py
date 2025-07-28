#!/usr/bin/env python3
from trustee_service_manager import TrusteeServiceManager

# Test the updated .de domain handling
trustee_manager = TrusteeServiceManager()

# Test a .de domain
domain = 'example.de'
base_price = 49.50

trustee_info = trustee_manager.check_trustee_requirement(domain)
total_cost, pricing_info = trustee_manager.calculate_trustee_pricing(base_price, domain)

print(f'Domain: {domain}')
print(f'Requires Trustee: {trustee_info["requires_trustee"]}')
print(f'Base Price: ${base_price:.2f}')
print(f'Total Cost: ${total_cost:.2f}')
print(f'Savings vs Previous: ${148.50 - total_cost:.2f}')
print(f'Risk Level: {pricing_info["risk_level"]}')
print(f'Country: {trustee_info["country"]}')