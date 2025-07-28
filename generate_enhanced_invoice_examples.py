#!/usr/bin/env python3
"""
Generate enhanced invoice examples showing 2x trustee markup integration
"""

from trustee_cost_calculator import calculate_domain_cost_with_trustee, generate_invoice_line_items

def generate_comprehensive_invoice_examples():
    """Generate comprehensive invoice examples with 2x trustee markup"""
    
    print("🧾 ENHANCED INVOICE EXAMPLES - 2X TRUSTEE MARKUP APPLIED")
    print("=" * 70)
    
    # Sample customer scenarios with different TLDs
    customer_scenarios = [
        {
            "customer": "Customer A - Standard Business",
            "domains": [
                ("mybusiness.com", 15.00),
                ("mybusiness.org", 18.00),
            ]
        },
        {
            "customer": "Customer B - International Expansion", 
            "domains": [
                ("startup.fr", 20.00),
                ("startup.eu", 22.00),
                ("startup.de", 16.00),
            ]
        },
        {
            "customer": "Customer C - Global Presence",
            "domains": [
                ("company.ca", 18.00),
                ("company.au", 24.00),
                ("company.com.br", 19.00),
            ]
        },
        {
            "customer": "Customer D - Mixed Portfolio",
            "domains": [
                ("brand.com", 12.00),
                ("brand.fr", 15.00),
                ("brand.jp", 25.00),
            ]
        }
    ]
    
    total_examples = 0
    total_revenue = 0
    
    for scenario in customer_scenarios:
        print(f"\n📋 {scenario['customer']}")
        print("-" * 50)
        
        customer_total = 0
        
        for domain, base_price in scenario['domains']:
            tld = "." + domain.split(".", 1)[1]
            
            # Calculate costs using enhanced calculator
            cost_result = calculate_domain_cost_with_trustee(tld, base_price)
            
            if cost_result['status'] == 'blocked':
                print(f"❌ {domain}: BLOCKED - {cost_result['reason']}")
                continue
            
            breakdown = cost_result['breakdown']
            total_cost = breakdown['total']
            
            # Generate detailed invoice
            invoice = generate_invoice_line_items(domain, tld, base_price)
            
            if invoice['error']:
                print(f"❌ {domain}: {invoice['error']}")
                continue
            
            print(f"\n🌐 Domain: {domain}")
            for item in invoice['line_items']:
                print(f"   • {item['description']}: ${item['amount']:.2f}")
            print(f"   SUBTOTAL: ${total_cost:.2f}")
            
            customer_total += total_cost
            total_examples += 1
        
        print(f"\n💰 CUSTOMER TOTAL: ${customer_total:.2f}")
        total_revenue += customer_total
    
    # Summary statistics
    print(f"\n" + "=" * 70)
    print(f"📊 BILLING SUMMARY")
    print(f"=" * 70)
    print(f"Total Domains: {total_examples}")
    print(f"Total Revenue: ${total_revenue:.2f}")
    print(f"Average per Domain: ${total_revenue/total_examples:.2f}" if total_examples > 0 else "N/A")
    
    # Trustee service breakdown
    print(f"\n🏢 TRUSTEE SERVICE IMPACT ANALYSIS:")
    print("-" * 40)
    
    trustee_revenue = 0
    free_trustee_domains = 0
    paid_trustee_domains = 0
    
    for scenario in customer_scenarios:
        for domain, base_price in scenario['domains']:
            tld = "." + domain.split(".", 1)[1]
            cost_result = calculate_domain_cost_with_trustee(tld, base_price)
            
            if cost_result['status'] != 'blocked':
                trustee_cost = cost_result['breakdown']['trustee_cost']
                
                if trustee_cost > 0:
                    trustee_revenue += trustee_cost
                    paid_trustee_domains += 1
                else:
                    free_trustee_domains += 1
    
    print(f"Free Trustee Domains: {free_trustee_domains}")
    print(f"Paid Trustee Domains: {paid_trustee_domains}")
    print(f"Trustee Service Revenue: ${trustee_revenue:.2f}")
    print(f"Base Domain Revenue: ${total_revenue - trustee_revenue:.2f}")
    print(f"Trustee Revenue %: {(trustee_revenue/total_revenue)*100:.1f}%" if total_revenue > 0 else "0%")

if __name__ == "__main__":
    generate_comprehensive_invoice_examples()