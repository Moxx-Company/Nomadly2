#!/usr/bin/env python3
"""
Trustee Cost Calculator for Customer Invoices
Calculate total cost including trustee services for domain registration
"""

def calculate_domain_cost_with_trustee(tld, base_price):
    """Calculate total domain cost including trustee service"""
    
    # Trustee service costs based on OpenProvider research
    trustee_costs = {
        # Free trustee services (no additional cost)
        '.com.br': 0,  # Brazil - free
        '.hu': 0,      # Hungary - free  
        '.jp': 0,      # Japan - free
        '.kr': 0,      # Korea - free
        '.sg': 0,      # Singapore - free
        '.com.sg': 0,  # Singapore - free
        
        # Paid trustee services (additional annual cost in USD) - 2x MULTIPLIER APPLIED
        '.fr': 30,     # France - EU local presence (15 * 2)
        '.eu': 30,     # European Union - EU residency (15 * 2)
        '.ca': 40,     # Canada - Canadian local presence (20 * 2)
        '.au': 50,     # Australia - Australian local presence (25 * 2)
        '.de': 20,     # Germany - optional trustee service (10 * 2)
        '.dk': 24,     # Denmark - 2025 compliance requirements (12 * 2)
        '.br': 36,     # Brazil - paid trustee option (18 * 2)
        
        # Special cases
        '.it': None,   # Italy - blocked (requires EEA residency + fiscal code)
    }
    
    tld_lower = tld.lower()
    trustee_cost = trustee_costs.get(tld_lower, 0)  # Default to 0 if TLD not in list
    
    # Apply 3.3x markup to base domain price
    marked_up_price = base_price * 3.3
    
    if trustee_cost is None:
        return {
            'status': 'blocked',
            'reason': 'TLD requires documentation not available through trustee service',
            'total_cost': 0,
            'breakdown': {
                'base_price': base_price,
                'markup_multiplier': 3.3,
                'marked_up_price': 0,
                'trustee_cost': 0,
                'total': 0
            }
        }
    
    total_cost = marked_up_price + trustee_cost
    
    return {
        'status': 'available',
        'total_cost': round(total_cost, 2),
        'breakdown': {
            'base_price': base_price,
            'markup_multiplier': 3.3,
            'marked_up_price': round(marked_up_price, 2),
            'trustee_cost': trustee_cost,
            'total': round(total_cost, 2)
        }
    }

def generate_invoice_line_items(domain, tld, base_price):
    """Generate invoice line items for domain with trustee service"""
    
    cost_calc = calculate_domain_cost_with_trustee(tld, base_price)
    
    if cost_calc['status'] == 'blocked':
        return {
            'line_items': [],
            'error': f"Domain {domain} cannot be registered - {cost_calc['reason']}"
        }
    
    breakdown = cost_calc['breakdown']
    line_items = []
    
    # Main domain registration line
    line_items.append({
        'description': f'Domain Registration - {domain} (1 year)',
        'amount': breakdown['marked_up_price']
    })
    
    # Trustee service line (if applicable)
    if breakdown['trustee_cost'] > 0:
        line_items.append({
            'description': f'Local Presence Service - {tld.upper()} (1 year)',
            'amount': breakdown['trustee_cost']
        })
    
    return {
        'line_items': line_items,
        'total': breakdown['total'],
        'error': None
    }

def print_trustee_cost_summary():
    """Print comprehensive trustee cost summary"""
    
    print("🏢 OPENPROVIDER TRUSTEE SERVICE COSTS - 2025")
    print("=" * 60)
    
    categories = {
        'Free Trustee Services (No Additional Cost)': {
            '.com.br': 'Brazil - Included free',
            '.hu': 'Hungary - Included free', 
            '.jp': 'Japan - Included free',
            '.kr': 'Korea - Included free',
            '.sg': 'Singapore - Included free',
            '.com.sg': 'Singapore - Included free'
        },
        
        'Paid Trustee Services (Additional Annual Cost)': {
            '.fr': 'France - $15/year (EU local presence)',
            '.eu': 'European Union - $15/year (EU residency)', 
            '.ca': 'Canada - $20/year (Canadian local presence)',
            '.au': 'Australia - $25/year (Australian local presence)',
            '.de': 'Germany - $10/year (optional trustee)',
            '.dk': 'Denmark - $12/year (2025 compliance)',
            '.br': 'Brazil - $18/year (paid option)'
        },
        
        'Blocked TLDs (Registration Not Possible)': {
            '.it': 'Italy - Requires EEA residency + fiscal code (no trustee available)'
        }
    }
    
    for category, tlds in categories.items():
        print(f"\n📋 {category}:")
        print("-" * 50)
        
        for tld, description in tlds.items():
            print(f"  {tld:8} | {description}")
    
    print(f"\n💰 INVOICE CALCULATION EXAMPLES:")
    print("-" * 40)
    
    examples = [
        ('.com', 12.00, 'Standard domain (no trustee)'),
        ('.fr', 15.00, 'France domain (with trustee)'),
        ('.com.br', 18.00, 'Brazil domain (free trustee)'),
        ('.ca', 14.00, 'Canada domain (with trustee)'),
        ('.it', 16.00, 'Italy domain (blocked)')
    ]
    
    for tld, base_price, description in examples:
        result = calculate_domain_cost_with_trustee(tld, base_price)
        
        if result['status'] == 'blocked':
            print(f"  {tld:8} | Base: ${base_price:5.2f} | BLOCKED - {description}")
        else:
            breakdown = result['breakdown']
            print(f"  {tld:8} | Base: ${base_price:5.2f} | Markup: ${breakdown['marked_up_price']:5.2f} | Trustee: ${breakdown['trustee_cost']:2} | Total: ${breakdown['total']:6.2f}")

if __name__ == "__main__":
    # Print comprehensive summary
    print_trustee_cost_summary()
    
    print(f"\n🧮 INTERACTIVE COST CALCULATOR")
    print("-" * 40)
    
    # Example calculations
    test_cases = [
        ('example.fr', '.fr', 15.50),
        ('test.com.br', '.com.br', 18.75), 
        ('sample.ca', '.ca', 14.25),
        ('domain.it', '.it', 16.00)
    ]
    
    for domain, tld, base_price in test_cases:
        print(f"\n📄 Invoice for: {domain}")
        invoice = generate_invoice_line_items(domain, tld, base_price)
        
        if invoice['error']:
            print(f"   ❌ ERROR: {invoice['error']}")
        else:
            for item in invoice['line_items']:
                print(f"   • {item['description']}: ${item['amount']:.2f}")
            print(f"   TOTAL: ${invoice['total']:.2f}")